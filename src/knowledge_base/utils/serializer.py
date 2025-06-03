from json import JSONEncoder
from uuid import UUID

from pydantic import BaseModel



class UUIDEncoder(JSONEncoder):

    def default(self, obj):
        try:
            if isinstance(obj, UUID):
                return str(obj)
            if isinstance(obj, BaseModel):
                return obj.model_dump()
            elif isinstance(obj, (list, tuple)):
                return [self.default(item) for item in obj]
            elif isinstance(obj, dict):
                return {self.default(key): self.default(value) for key, value in obj.items()}
        except Exception as e:
            print(f"Error serializing object {obj}: {e}")

        # Let the base class default method raise the TypeError
        return JSONEncoder.default(self, obj)