from smolagents import tool

from knowledge_base.models.entities import Entity
from knowledge_base.models.knowledge_base import KnowledgeBase
from knowledge_base.models.relationships import Relationship


@tool
def get_character_infos(kb: KnowledgeBase, character_name: str) -> Entity | None:
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
        >>> character_info = get_character_infos(kb=kb, character_name="Gandalf")
        >>> print(character_info.__dict__)
        {
            'id': UUID('e895bb12-e2aa-4e02-81e6-c7a859445e4e'),
            'name': 'Gandalf',
            'description': 'A wise and powerful wizard.',
            'abilities': ["magic spells", "ancient tongues", "great history knowledge", "fireworks"],
            'aliases': ["Gandalaf the Grey", "Grand Elf"],
            'metadata': {},
            'occupation': "Concellor of",
            'personality_traits': [],
            'physical_description': {},
            'species': "Human",
            'time_or_period': None
        }
    """
    node = kb.get_entity_by_name(character_name)
    return node.get("entity")


@tool
def get_all_relationships(kb: KnowledgeBase, character_name: str) -> list[Relationship]:
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
        list[Relationship]: A list of relationships with the carachter's corresponding entity as source
            or target of the graph edge.

    Example:
        >>> kb = KnowledgeBase()
        >>> relationships = get_all_relationships(kb=kb, character_name="Gandalf")
        >>> print(relationships)
        [
            {
                'id': UUID('175e4632-e89b-31f3-a826-426934074099'),
                'type': 'FRIENDS_WITH',
                'description': 'Gandalf is friends with Aragorn.',
                'source_entity_id': UUID('123e4567-e89b-12d3-a456-426614174000'),
                'target_entity_id': UUID('223e4567-e89b-12d3-a456-426614174001')
            },
            {
                'id': 'UUID('175e4626-e89b-18c3-a826-426000074000')',
                'type': 'MENTOR_OF',
                'description': 'Gandalf is a mentor to Frodo.',
                'source_entity_id': UUID('123e4567-e89b-12d3-a456-426614174000'),
                'target_entity_id': UUID('323e4567-e89b-12d3-a456-426614174002')
            }
        ]
    """
    entity = kb.get_entity_by_name(character_name)
    targets = kb.graph.edges(entity)
    return [
        kb.graph.get_edge_data(entity.id, target.id)
        for target in targets
    ]
