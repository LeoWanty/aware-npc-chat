import networkx as nx
from typing import List, Dict, Optional, Any, Union, Mapping
from uuid import UUID
import json
from pathlib import Path

# Import all specific entity types for the factory in load_kb
from knowledge_base.models.entities import Entity, Character, Place, Event, SpecialObject
from knowledge_base.models.relationships import Relationship
from knowledge_base.utils.serializer import UUIDEncoder


class KnowledgeBase:
    def __init__(self):
        """
        Initializes the Knowledge Base with an empty directed graph
        and an entity lookup dictionary.
        """
        self.graph = nx.MultiDiGraph()
        self.map_entity_name_to_id: Dict[str, Entity] = {}  # Stores entity objects by their ID (UUID as string)

    def add_entity(self, entity: Entity) -> None:
        """
        Adds an entity to the knowledge base.

        If the entity ID already exists, it will not be re-added, and
        its attributes in the graph will not be updated by this call.
        """
        if entity.id not in self.graph.nodes:
            self.graph.add_node(entity.id, type=entity.__class__.__name__, entity=entity)
            self.map_entity_name_to_id[entity.name] = entity.id

    def add_entities(self, entities: List[Entity]) -> None:
        """
        A convenience method to add a list of entities.
        """
        for entity in entities:
            self.add_entity(entity)

    def add_relationship(self, relationship: Relationship) -> None:
        """
        Adds a relationship (edge) to the graph.

        Assumes source and target entities are already added. If not,
        NetworkX will add them as nodes, but they won't be in self.entities
        or have attributes unless added via add_entity.
        """
        source_id_str = str(relationship.source_entity_id)
        target_id_str = str(relationship.target_entity_id)

        if source_id_str not in self.graph:
            print(
                f"Warning: Source entity {source_id_str} for relationship {relationship.id} not in graph. Adding as a bare node.")
            # Optionally add a placeholder or fetch if available, for now NetworkX handles node creation
        if target_id_str not in self.graph:
            print(
                f"Warning: Target entity {target_id_str} for relationship {relationship.id} not in graph. Adding as a bare node.")

        # The relationship.id (UUID as string) can serve as a unique key for the edge if needed,
        # especially if multiple edges of the same type can exist between two nodes.
        # DiGraph.add_edge can store multiple edges if a key is provided: self.graph.add_edge(u, v, key=key, **attrs)
        # For now, if multiple relationships (same type, same direction) are added, attributes of later ones might overwrite earlier ones
        # unless we use MultiDiGraph or unique keys for each edge.
        # Let's use relationship.id as the key to allow multiple distinct relationships.
        self.graph.add_edge(source_id_str, target_id_str, key=relationship.id, relationship=relationship)

    def add_relationships(self, relationships: List[Relationship]) -> None:
        """
        A convenience method to add a list of relationships.
        """
        for relationship in relationships:
            self.add_relationship(relationship)

    def get_entity_by_id(self, entity_id: Union[str, UUID]) -> Optional[Entity]:
        """
        Retrieves an entity object by its ID.
        """
        entity_id = UUID(entity_id) if isinstance(entity_id, str) else entity_id
        return self.graph.nodes.get(entity_id)

    def get_entity_by_name(self, name: str):
        """
        Retrieves an entity object by its name. Must be an exact match
        """
        if name not in self.map_entity_name_to_id:
            raise KeyError(f"Entity name '{name}' not found in KB.")
        return self.get_entity_by_id(self.map_entity_name_to_id.get(name))

    def get_node_attributes(self, entity_id: Union[str, UUID]) -> Optional[Dict[str, Any]]:
        """
        Retrieves the attributes of a node (entity) from the graph.
        """
        entity_id = UUID(entity_id) if isinstance(entity_id, str) else entity_id
        if self.graph.has_node(entity_id):
            return self.graph.nodes[entity_id]
        else:
            raise KeyError(f"Entity {entity_id} not found in KB.")

    def get_edge_attributes(self, source_id: Union[str, UUID], target_id: Union[str, UUID],
                            relationship_id: Union[str, UUID]) -> Optional[Mapping[str, Any]]:
        """
        Retrieves attributes of a specific edge identified by its relationship ID (used as key).
        """
        source_id_str = UUID(source_id)
        target_id_str = UUID(target_id)
        rel_id_str = UUID(relationship_id)
        if self.graph.has_edge(source_id_str, target_id_str, key=rel_id_str):
            return self.graph.get_edge_data(source_id_str, target_id_str, key=rel_id_str)
        return None

    def get_all_edges_between(self, source_id: Union[str, UUID], target_id: Union[str, UUID]) -> Optional[
        Mapping[str, Dict[str, Any]]]:
        """
        Retrieves all edges (and their attributes) between two nodes.
        Returns a dictionary where keys are relationship IDs (edge keys).
        """
        source_id_str = UUID(source_id)
        target_id_str = UUID(target_id)

        if self.graph.has_edge(source_id_str, target_id_str):
            return self.graph.get_edge_data(source_id_str, target_id_str)
        else:
            raise ValueError(f"No edges between {source_id} and {target_id} found in KB.")

    def save_kb(self, file_path: Union[str, Path]) -> None:
        """
        Saves the knowledge base graph to a JSON file.
        """
        file_path_obj = Path(file_path)
        try:
            # Preserve current behavior for edges by specifying edges="links"
            dict_to_dump = dict(
                graph_data=nx.readwrite.json_graph.node_link_data(self.graph, edges="links"),
                map_entity_name_to_id = self.map_entity_name_to_id,
            )
            with file_path_obj.open('w', encoding='utf-8') as f:
                json.dump(dict_to_dump, f, indent=4, cls=UUIDEncoder)

            print(f"KnowledgeBase saved to {file_path_obj}")
        except IOError as e:
            print(f"Error saving KnowledgeBase to {file_path_obj}: {e}")
        except Exception as e:
            raise Exception(f"An unexpected error occurred during saving: {e}")

    @classmethod
    def from_json(cls, file_path: Union[str, Path]) -> 'KnowledgeBase':
        """
        Loads the knowledge base graph from a JSON file.
        Also repopulates the self.entities dictionary.
        """
        file_path_obj = Path(file_path)
        if not file_path_obj.exists():
            raise FileExistsError(f"File not found at {file_path_obj}")

        with file_path_obj.open('r', encoding='utf-8') as f:
            data_dict = json.load(f)

        entity_type_map: dict[str, Entity] = {
            "Character": Character,
            "Place": Place,
            "Event": Event,
            "SpecialObject": SpecialObject,
        }

        kb = cls.__new__(cls)
        kb.__init__()

        entities = [
            entity_type_map[dumped_entity["type"]].model_validate(dumped_entity["entity"])
            for dumped_entity in data_dict["graph_data"]["nodes"]
        ]
        kb.add_entities(entities=entities)
        # kb.add_relationships()

        print(f"KnowledgeBase loaded from {file_path_obj}")
        print(f"  Nodes (entities) loaded: {kb.graph.number_of_nodes()}")
        print(f"  Edges (relationships) loaded: {kb.graph.number_of_edges()}")
        return kb