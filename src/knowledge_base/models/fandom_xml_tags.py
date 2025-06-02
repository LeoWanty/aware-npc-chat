from typing import List, Optional, Dict
from pydantic import BaseModel, HttpUrl, Field, field_validator
from datetime import datetime


class Contributor(BaseModel):
    username: Optional[str] = None
    id: Optional[int] = None
    ip: Optional[str] = None  # Added for anonymous contributors

    @field_validator('id', mode='before')
    def empty_str_to_none(cls, v):
        if isinstance(v, str) and v.strip() == "":
            return None
        return v


class Text(BaseModel):
    # Using alias='_' might not work as expected for direct text content with ElementTree.
    # This will likely be populated manually by accessing element.text in the parser.
    # The alias is more for when Pydantic parses a dict directly.
    # For now, we define it and will handle it in the parser.
    content: Optional[str] = None
    bytes: Optional[int] = None
    sha1: Optional[str] = None
    deleted: Optional[bool] = None  # For <text deleted="deleted" />

    @field_validator('bytes', mode='before')
    def empty_str_bytes_to_none(cls, v):
        if isinstance(v, str) and v.strip() == "":
            return None
        try:
            return int(v)
        except ValueError:
            return None  # Or raise error, depending on strictness


class Revision(BaseModel):
    id: int
    parentid: Optional[int] = None
    timestamp: datetime
    contributor: Contributor  # This will be a nested model
    minor: Optional[bool] = False  # Represented as <minor /> tag, default to False
    comment: Optional[str] = None
    model: Optional[str] = None
    format: Optional[str] = None
    text: Text  # This will be a nested model
    sha1: Optional[str] = None

    @field_validator('parentid', 'id', mode='before')
    def empty_str_int_to_none(cls, v):  # id should not be None, but pre-validation can help clean
        if isinstance(v, str) and v.strip() == "":
            return None
        if v is None: return None  # for parentid
        try:
            return int(v)
        except ValueError:
            # id must be int, parentid can be None
            if cls.model_fields['id'].is_required() and v is None:
                raise ValueError("ID cannot be None")
            return None


class Page(BaseModel):
    title: str
    ns: int  # Namespace
    id: int
    redirect_title: Optional[str] = None  # Populated from <redirect title="..."/>
    restrictions: Optional[List[str]] = Field(default_factory=list)
    revisions: List[Revision] = Field(default_factory=list)

    # If redirect_title is an alias for a sub-element, Pydantic would need this.
    # However, it's usually an attribute of a <redirect /> tag, handled in parser.
    # alias is more for mapping dict keys to field names.
    # Field(None, alias='redirect')

    @field_validator('ns', 'id', mode='before')
    def empty_str_to_int(cls, v):
        if isinstance(v, str) and v.strip() == "":
            # Or raise error if these fields are strictly required and cannot be derived
            return 0  # Defaulting to 0, or handle as error
        try:
            return int(v)
        except ValueError:
            return 0  # Defaulting or raise


class SiteInfo(BaseModel):
    sitename: Optional[str] = None
    dbname: Optional[str] = None
    base: Optional[HttpUrl] = None
    generator: Optional[str] = None
    case: Optional[str] = None
    # Namespaces can be complex, e.g. <namespace key="0" case="first-letter">Artikel</namespace>
    # Using a Dict where key is the namespace ID (int) and value is its name (str)
    namespaces: Optional[Dict[int, str]] = Field(default_factory=dict)


class FandomSiteContent(BaseModel):
    siteinfo: Optional[SiteInfo] = None
    pages: List[Page] = Field(default_factory=list)


# Example of how timestamp might be parsed if it's not directly ISO format
# This would typically be in the parser logic, not the model, unless mode='before' and always runs.
# @field_validator('timestamp', mode='before', always=True)
# def format_timestamp(cls, value):
#     if isinstance(value, str):
#         # Example: "2023-10-27T10:20:30Z" - ISO 8601, directly parsable
#         # If it's another format, convert it here
#         try:
#             return datetime.fromisoformat(value.replace('Z', '+00:00'))
#         except ValueError:
#             # Handle other formats or raise error
#             raise ValueError(f"Invalid timestamp format: {value}")
#     return value
