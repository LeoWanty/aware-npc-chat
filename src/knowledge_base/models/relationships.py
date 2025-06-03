from typing import Dict, Optional, Any
from uuid import UUID, uuid4

from pydantic import BaseModel, Field

# --- Relationship Type Constants ---
RELATIONSHIP_TYPE_KNOWS = "KNOWS"
RELATIONSHIP_TYPE_VISITED = "VISITED"
RELATIONSHIP_TYPE_PARTICIPATED_IN = "PARTICIPATED_IN"
RELATIONSHIP_TYPE_OWNS = "OWNS"
RELATIONSHIP_TYPE_LOCATED_AT = "LOCATED_AT"
RELATIONSHIP_TYPE_FAMILY_OF = "FAMILY_OF"
RELATIONSHIP_TYPE_ENEMY_OF = "ENEMY_OF"
RELATIONSHIP_TYPE_ALLY_OF = "ALLY_OF"
RELATIONSHIP_TYPE_MEMBER_OF = "MEMBER_OF" # For group/organization membership
RELATIONSHIP_TYPE_INTERACTED_WITH_OBJECT = "INTERACTED_WITH_OBJECT" # General interaction
RELATIONSHIP_TYPE_MISC = "MISC" # Other uncategorized relationship type for wiki links

class Relationship(BaseModel):
    """Represents a relationship between two entities."""
    id: UUID = Field(default_factory=uuid4)
    source_entity_id: UUID
    target_entity_id: UUID
    relationship_type: str # e.g., KNOWS, VISITED, FAMILY_OF
    description: Optional[str] = Field(default=None, description="Optional context for the relationship")
    depth: Optional[int] = Field(default=None, description="Numerical depth for quantifiable relationships")
    time_or_period: Optional[str] = Field(default=None, description="If the relationship can be placed in time")
    metadata: Dict[str, Any] = Field(default_factory=dict)

    def __repr__(self) -> str:
        return (f"<Relationship id='{self.id}' source='{self.source_entity_id}' "
                f"target='{self.target_entity_id}' type='{self.relationship_type}' depth='{self.depth}'>")

    def __eq__(self, other) -> bool:
        if not isinstance(other, Relationship):
            return NotImplemented
        return self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)


# --- Relationship Depth Categories ---

# CHARACTER_KNOWS_CHARACTER depth levels:
# 1.  Aware of (name mentioned in proximity / heard of)
# 2.  Met briefly / superficial interaction
# 3.  Acquaintance / regular but casual interaction
# 4.  Works with / collaborator (task-oriented)
# 5.  Friend / confidante
# 6.  Close friend / deep trust / shares secrets
# 7.  Mentor / Protégé
# 8.  Deep emotional bond (non-familial, non-romantic)
# 9.  Romantic partner / Spouse
# 10. Life-defining connection / Soulmate / Arch-nemesis (extreme positive or negative)

# CHARACTER_IS_FAMILY_OF_CHARACTER depth levels:
# 1.  Distant relative (e.g., third cousin, great-great-grandparent)
# 2.  Extended family (e.g., cousin, aunt/uncle, grandparent)
# 3.  Close extended family (e.g., first cousin regularly interacted with, close aunt/uncle)
# 4.  Step-family (e.g., step-parent, step-sibling) with moderate closeness
# 5.  Immediate family (e.g., parent, sibling, child)
# 6.  Very close immediate family (strong bond, lives together or constant contact)
# 7.  Twin / Inseparable sibling
# 8.  Primary caregiver / Dependent child (strongest bond of care)
# 9.  Ancestral lineage (direct line, e.g. parent-child-grandchild, historical figures)
# 10. Progenitor / Founder of a bloodline or dynasty

# CHARACTER_PARTICIPATED_IN_EVENT depth levels:
# 1.  Indirectly affected / Present in the general area but not involved
# 2.  Observer / Witness (passive presence)
# 3.  Minor participant / Contributed in a small, non-critical way
# 4.  Active participant / Had a defined role
# 5.  Significant participant / Role was crucial to the event's progress
# 6.  Key decision-maker / Influenced the event's direction
# 7.  Leader / Instigator of the event
# 8.  Central figure / Event revolved around this character
# 9.  Sole participant (if applicable, e.g., a solo journey event)
# 10. Defining moment / Event fundamentally changed the character

# CHARACTER_VISITED_PLACE depth levels:
# 1.  Passed through / Brief, unremarkable presence (e.g., layover in an airport)
# 2.  Short visit / Tourist (e.g., visited a landmark for a day)
# 3.  Temporary residence / Stayed for a notable period (e.g., a summer vacation home)
# 4.  Frequent visitor / Regular but not permanent (e.g., visits a town weekly for market)
# 5.  Worked there / Place of employment (significant time spent, task-oriented)
# 6.  Lived there for a period / Former residence
# 7.  Current residence / Home
# 8.  Birthplace / Place of origin
# 9.  Place of profound personal significance (e.g., site of a major life event, spiritual sanctuary)
# 10. Never left / Entire life spent in one place

# CHARACTER_OWNS_OBJECT depth levels:
# 1.  Borrowed / Temporary possession
# 2.  Custodial possession / Holding for someone else
# 3.  Shared ownership / Partial claim
# 4.  Regularly uses but doesn't own (e.g., a tool at work)
# 5.  Personal possession / Belongs to the character
# 6.  Highly valued possession / Sentimental or practical importance
# 7.  Signature item / Strongly associated with the character
# 8.  Magical attunement / Unique bond (if applicable in the context)
# 9.  Inherited / Ancestral ownership
# 10. Created / Crafted by the character

# CHARACTER_INTERACTED_WITH_OBJECT depth levels:
# 1.  Briefly touched / superficial contact
# 2.  Examined / Inspected
# 3.  Used once / for a specific, limited purpose
# 4.  Regularly used / common interaction
# 5.  Repaired / Maintained
# 6.  Modified / Altered
# 7.  Studied / Researched extensively
# 8.  Destroyed / Disassembled
# 9.  Relied upon for survival / critical use
# 10. Discovered / Unearthed

# CHARACTER_STUDIED_OBJECT depth levels:
# 1.  Glanced at / Noticed
# 2.  Examined superficially / Basic understanding
# 3.  Observed / Casually looked over
# 4.  Read about / Heard descriptions
# 5.  Studied briefly / Some practical knowledge
# 6.  Thoroughly studied / Detailed understanding
# 7.  Experimented with / Hands-on experience
# 8.  Researched extensively / Expert knowledge
# 9.  Mastered / Comprehensive expertise
# 10. Pioneered research / Groundbreaking discoveries
