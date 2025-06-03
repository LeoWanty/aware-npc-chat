import networkx as nx
from typing import List, Dict, Optional, Any, Union, Mapping
from uuid import UUID
import json
from pathlib import Path

# Import all specific entity types for the factory in load_kb
from .entities import Entity, Character, Place, Event, SpecialObject
from .relationships import Relationship


class KnowledgeBase:
    def __init__(self):
        """
        Initializes the Knowledge Base with an empty directed graph
        and an entity lookup dictionary.
        """
        self.graph = nx.MultiDiGraph()  # Changed to MultiDiGraph
        self.entities: Dict[str, Entity] = {}  # Stores entity objects by their ID (UUID as string)

    def add_entity(self, entity: Entity) -> None:
        """
        Adds an entity to the knowledge base.

        If the entity ID already exists, it will not be re-added, and
        its attributes in the graph will not be updated by this call.
        """
        entity_id_str = str(entity.id)
        if entity_id_str not in self.entities:
            self.entities[entity_id_str] = entity
            # Use entity.to_dict() to get attributes for the node
            self.graph.add_node(entity_id_str, **entity.to_dict())
        # else:
        # Optionally, log that entity already exists or handle updates
        # print(f"Warning: Entity with ID {entity_id_str} already exists. Not re-adding.")

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

        # Use relationship.to_dict() for edge attributes.
        # The relationship.id (UUID as string) can serve as a unique key for the edge if needed,
        # especially if multiple edges of the same type can exist between two nodes.
        # DiGraph.add_edge can store multiple edges if a key is provided: self.graph.add_edge(u, v, key=key, **attrs)
        # For now, if multiple relationships (same type, same direction) are added, attributes of later ones might overwrite earlier ones
        # unless we use MultiDiGraph or unique keys for each edge.
        # Let's use relationship.id as the key to allow multiple distinct relationships.
        self.graph.add_edge(source_id_str, target_id_str, key=str(relationship.id), **relationship.to_dict())

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
        return self.entities.get(str(entity_id))

    def get_node_attributes(self, entity_id: Union[str, UUID]) -> Optional[Dict[str, Any]]:
        """
        Retrieves the attributes of a node (entity) from the graph.
        """
        entity_id_str = str(entity_id)
        if self.graph.has_node(entity_id_str):
            return self.graph.nodes[entity_id_str]
        return None

    def get_edge_attributes(self, source_id: Union[str, UUID], target_id: Union[str, UUID],
                            relationship_id: Union[str, UUID]) -> Optional[Mapping[str, Any]]:
        """
        Retrieves attributes of a specific edge identified by its relationship ID (used as key).
        """
        source_id_str = str(source_id)
        target_id_str = str(target_id)
        rel_id_str = str(relationship_id)
        if self.graph.has_edge(source_id_str, target_id_str, key=rel_id_str):
            return self.graph.get_edge_data(source_id_str, target_id_str, key=rel_id_str)
        return None

    def get_all_edges_between(self, source_id: Union[str, UUID], target_id: Union[str, UUID]) -> Optional[
        Mapping[str, Dict[str, Any]]]:
        """
        Retrieves all edges (and their attributes) between two nodes.
        Returns a dictionary where keys are relationship IDs (edge keys).
        """
        source_id_str = str(source_id)
        target_id_str = str(target_id)
        if self.graph.has_edge(source_id_str, target_id_str):
            # This actually gets the first edge if no key specified
            return self.graph.get_edge_data(source_id_str, target_id_str)
            # To get all: self.graph[source_id_str][target_id_str]
            # if self.graph.is_multigraph() else ...
            # For DiGraph, it's self.graph[u][v] if key is not used for multiple edges
            # or self.graph.get_edge_data(u,v,key=specific_key)
            # If keys are used for multiple edges:
            # This returns a dict like {edge_key1: attrs1, edge_key2: attrs2}
            # return self.graph[source_id_str].get(target_id_str, None)
        return None

    def save_kb(self, file_path: Union[str, Path]) -> None:
        """
        Saves the knowledge base graph to a JSON file.
        """
        file_path_obj = Path(file_path)
        try:
            # Preserve current behavior for edges by specifying edges="links"
            graph_data = nx.readwrite.json_graph.node_link_data(self.graph, edges="links")
            with file_path_obj.open('w', encoding='utf-8') as f:
                json.dump(graph_data, f, indent=4)
            print(f"KnowledgeBase saved to {file_path_obj}")
        except IOError as e:
            print(f"Error saving KnowledgeBase to {file_path_obj}: {e}")
        except Exception as e:
            print(f"An unexpected error occurred during saving: {e}")

    def load_kb(self, file_path: Union[str, Path]) -> None:
        """
        Loads the knowledge base graph from a JSON file.
        Also repopulates the self.entities dictionary.
        """
        file_path_obj = Path(file_path)
        if not file_path_obj.exists():
            print(f"Error: File not found at {file_path_obj}")
            return

        try:
            with file_path_obj.open('r', encoding='utf-8') as f:
                data_dict = json.load(f)

            # Important: Specify multigraph=True and directed=True when loading
            # Preserve current behavior for edges by specifying edges="links"
            self.graph = nx.readwrite.json_graph.node_link_graph(data_dict, directed=True, multigraph=True,
                                                                 edges="links")

            # Repopulate self.entities
            self.entities.clear()
            entity_type_map = {
                Character.ENTITY_TYPE: Character,
                Place.ENTITY_TYPE: Place,
                Event.ENTITY_TYPE: Event,
                SpecialObject.ENTITY_TYPE: SpecialObject,
                # Entity.ENTITY_TYPE: Entity # Base Entity should not be instantiated directly if abstract
            }

            for node_identifier, attributes_data in self.graph.nodes(data=True):
                entity_type_str = attributes_data.get('entity_type')
                entity_class = entity_type_map.get(entity_type_str)

                if entity_class:
                    try:
                        # Create a new dict for from_dict, ensuring 'id' is the node_identifier itself
                        reconstruction_data = attributes_data.copy()
                        reconstruction_data['id'] = node_identifier  # Use the actual node ID from the graph

                        reconstructed_entity = entity_class.model_validate(reconstruction_data, from_attributes=True)
                        self.entities[node_identifier] = reconstructed_entity
                    except Exception as e:
                        print(
                            f"Error reconstructing entity {node_identifier} of type {entity_type_str}: {e}. Attributes: {attributes_data}")
                else:
                    print(
                        f"Warning: Unknown entity type '{entity_type_str}' for node ID {node_identifier}. Cannot reconstruct fully.")

            print(f"KnowledgeBase loaded from {file_path_obj}")
            print(f"  Nodes loaded: {self.graph.number_of_nodes()}")
            print(f"  Edges loaded: {self.graph.number_of_edges()}")
            print(f"  Entities dictionary repopulated with {len(self.entities)} entries.")

        except IOError as e:
            print(f"Error loading KnowledgeBase from {file_path_obj}: {e}")
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON from {file_path_obj}: {e}")
        except Exception as e:  # Catch other potential errors during deserialization/reconstruction
            print(f"An unexpected error occurred during loading: {e}")