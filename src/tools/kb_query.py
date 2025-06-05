from typing import Dict, Any, Union
from uuid import UUID
from smolagents import tool
from knowledge_base.models.knowledge_base import KnowledgeBase

@tool
def get_character_infos(kb: KnowledgeBase, character_name: str) -> Dict[str, Any]:
    """
    Retrieve the content of a node for a given character.

    This function fetches the attributes of a character node from the knowledge base graph.
    It is useful for obtaining detailed information about a specific character.

    Args:
        kb (KnowledgeBase): An instance of the KnowledgeBase class containing the graph data.
        character_name (str): The name of the character whose node content is to be retrieved.
                             This name must exactly match the name stored in the knowledge base.

    Returns:
        Dict[str, Any]: A dictionary containing the node attributes of the character.
                        This includes properties such as the character's name, description, and other metadata.

    Example:
        >>> kb = KnowledgeBase()
        >>> character_info = get_character_infos(kb, "Gandalf")
        >>> print(character_info)
        {
            'id': '123e4567-e89b-12d3-a456-426614174000',
            'name': 'Gandalf',
            'description': 'A wise and powerful wizard.',
            'type': 'Character'
        }
    """
    entity_id = kb.get_entity_by_name(character_name)
    return kb.get_node_attributes(entity_id)

@tool
def get_all_relationships(kb: KnowledgeBase, character_name: str) -> Dict[str, Dict[str, Any]]:
    """
    Retrieve all relationships associated with a given character.

    This function collects all incoming and outgoing relationships for a specified character
    from the knowledge base graph. It is useful for understanding how a character is connected
    to other entities within the graph.

    Args:
        kb (KnowledgeBase): An instance of the KnowledgeBase class containing the graph data.
        character_name (str): The name of the character whose relationships are to be retrieved.
                             This name must exactly match the name stored in the knowledge base.

    Returns:
        Dict[str, Dict[str, Any]]: A dictionary where each key is a relationship ID and the value
                                    is a dictionary of relationship attributes. These attributes
                                    include the type of relationship, description, and other metadata.

    Example:
        >>> kb = KnowledgeBase()
        >>> relationships = get_all_relationships(kb, "Gandalf")
        >>> print(relationships)
        {
            'rel_1': {
                'relationship': {
                    'id': 'rel_1',
                    'type': 'FRIENDS_WITH',
                    'description': 'Gandalf is friends with Aragorn.',
                    'source_entity_id': '123e4567-e89b-12d3-a456-426614174000',
                    'target_entity_id': '223e4567-e89b-12d3-a456-426614174001'
                }
            },
            'rel_2': {
                'relationship': {
                    'id': 'rel_2',
                    'type': 'MENTOR_OF',
                    'description': 'Gandalf is a mentor to Frodo.',
                    'source_entity_id': '123e4567-e89b-12d3-a456-426614174000',
                    'target_entity_id': '323e4567-e89b-12d3-a456-426614174002'
                }
            }
        }
    """
    entity = kb.get_entity_by_name(character_name)
    relationships = {}
    for source, target, key, data in kb.graph.in_edges(entity.id, keys=True, data=True):
        relationships[key] = data
    for source, target, key, data in kb.graph.out_edges(entity.id, keys=True, data=True):
        relationships[key] = data
    return relationships
