from abc import ABC, abstractmethod
from typing import List, Dict, Optional, Any
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class Entity(BaseModel):
    """Abstract base class for all entities in the knowledge base."""
    id: UUID = Field(default_factory=uuid4)
    name: str
    description: Optional[str] = Field(default=None, description="Optional context for the relationship")
    time_or_period: Optional[str] = Field(default=None, description="If the relationship can be placed in time")
    metadata: Dict[str, Any] = Field(default_factory=dict)

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} id='{self.id}' name='{self.name}'>"

    def __eq__(self, other) -> bool:
        if not isinstance(other, Entity):
            return NotImplemented
        return self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)


class Character(Entity):
    """Represents a character."""
    aliases: List[str]
    species: Optional[str]
    abilities: List[str]
    occupation: Optional[str]
    physical_description: Dict[str, str]
    personality_traits: List[str]


class Place(Entity):
    """Represents a location or place."""
    location_type: Optional[str] # e.g., City, Planet, Building, Region
    coordinates: Optional[str] # e.g., "lat,long" or other system


class Event(Entity):
    """Represents an event or occurrence."""
    event_type: Optional[str] # e.g., Natural Phenomena, Conflict or War, Feast / Ritual, Era


class SpecialObject(Entity):
    object_type: Optional[str] # e.g., Artifact, Weapon, Technology



