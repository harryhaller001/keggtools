""" KEGG pathway models to parse object relational """
# pylint: disable=invalid-name,too-few-public-methods

from xml.etree import ElementTree
from xml.etree.ElementTree import Element
from typing import Any, Dict, List, Union, Optional

import re

from .const import (
    RELATION_TYPES,
    RELATION_SUBTYPES,
    ENTRY_TYPE,
    GRAPHICS_TYPE,
)

from .utils import (
    get_attribute,
    get_numeric_attribute,
    parse_xml,
)




def is_valid_org(value: str) -> bool:
    """
    Check if org identifier is valid.
    """

    # Organism must be 3 letter code
    # Identifier can also be KO or Enzyme identifer
    # TODO: validate with KEGG organism list
    return value in ["ko", "ec"] or re.match(pattern=r"^([a-z]{3})$", string=value) is not None





class Subtype:
    """
    Subtype model class.
    """

    def __init__(
        self,
        name: str,
        value: str,
    ) -> None:
        """
        Init Subtype model instance.
        """
        self.name: str = name
        self.value: str = value


    @staticmethod
    def parse(item: Element) -> "Subtype":
        """
        Parse subtype XML Element.
        """

        # check correct type
        assert item.tag == "subtype"


        name: str = get_attribute(element=item, key="name")
        value: str = get_attribute(element=item, key="value")

        # TODO: check for valid subtype names in RELATION_SUBTYPES

        return Subtype(name=name, value=value)




class Relation:
    """
    Relation model class.
    """

    def __init__(
        self,
        entry1: str,
        entry2: str,
        type: str,
    ) -> None:
        """
        Init relation model instance.
        """

        self.entry1: str = entry1
        self.entry2: str = entry2
        self.type: str = type
        self.subtypes: List[Subtype] = []


    @staticmethod
    def parse(item: Element) -> "Relation":
        """
        Parse xml ElementTree into KEGG Relation.
        :param item: ElementTree
        :return: Relation
        """

        # Check tag of relation is correct
        assert item.tag == "relation"


        entry1: str = get_numeric_attribute(element=item, key="entry1")
        entry2: str = get_numeric_attribute(element=item, key="entry2")
        type: str = get_attribute(element=item, key="type")

        if type not in RELATION_TYPES:
            raise ValueError(f"Relation type '{type}' not in list of valid types.")


        # Create relation instance from attributes
        relation: Relation = Relation(
            entry1=entry1,
            entry2=entry2,
            type=type,
        )


        # Parse Child items of xml element by iterating of child elements
        for child in item:
            relation.subtypes.append(Subtype.parse(item=child))


        return relation


    def __str__(self) -> str:
        """
        Generate string from relation instance.
        """
        return f"<Relation {self.entry1}->{self.entry2} type='{self.type}'>"




class Component:
    """
    The component element is a subelement of the entry element, and is used when the entry
    element is a complex node; namely, when the type attribute value of the entry element
    is "group". The nodes that constitute the complex are specified by recurrent calls. For
    example, when the complex is composed of two nodes, two component elements are specified.
    The attribute of this element is as follows.
    """

    def __init__(self, id: str) -> None:
        """
        Init Component model.
        """

        self.id: str = id


    @staticmethod
    def parse(item: Element) -> "Component":
        """
        Parsing ElementTree into Component.
        :param item: ElementTree
        :return: Component
        """

        # Check for correct xml tag
        assert item.tag == "component"

        component_id: str = get_attribute(element=item, key="id")

        # Check pattern of component id

        # Create component instance from id attribute
        component: Component = Component(id=component_id)
        return component



class Graphics:
    """
    Graphics information for rendering.
    """

    def __init__(self) -> None:
        """
        Init Graphics model instance.
        """

        self.x: Optional[str] = None
        self.y: Optional[str] = None
        self.width: Optional[str] = None
        self.height: Optional[str] = None
        self.name: Optional[str] = None
        self.type: Optional[str] = None
        self.fgcolor: Optional[str] = None


    def __str__(self) -> str:
        """
        Build Graphics summary.
        :return: str
        """

        return f"<Graphics name='{self.name}'>"



    @staticmethod
    def parse(item: Element) -> "Graphics":
        """
        Parse xml ElementTree into KEGG Graphics

        :param item: ElementTree
        :return: Graphics
        """

        # Check xml tag
        assert item.tag == "graphics"

        graphic: Graphics = Graphics()

        # Parse attributes from XML element
        graphic.x = item.attrib.get("x")
        graphic.y = item.attrib.get("y")
        graphic.width = item.attrib.get("width")
        graphic.height = item.attrib.get("height")
        graphic.name = item.attrib.get("name")
        graphic.type = item.attrib.get("type")
        graphic.fgcolor = item.attrib.get("fgcolor")

        return graphic


class Entry:
    """
    Entry model.
    """

    def __init__(self) -> None:
        """
        Init entry model instance.
        """

        # REQUIRED
        self.id = ""
        self.name = ""
        self.type = ""

        # IMPLIED
        self.link = ""
        self.reaction = ""


        # Implied child instances
        self.graphics: Optional[Graphics] = None
        self.components: List[Component] = []


    def get_gene_id(self) -> int:
        """
        Parse variable 'name' into KEGG ID
        :return: int
        """

        # TODO: change entrez id to string !!

        return int(self.name.split(":")[1])


    def get_id(self) -> int:
        """
        Parse variable 'name' into KEGG ID

        :return: int
        """

        return int(self.name.split(":")[1])


    @staticmethod
    def parse(item: Element) -> "Entry":
        """
        Parsing xml ElementTree into KEGG Entry

        :param item: ElementTree
        :return: Entry
        """

        entry: Entry = Entry()
        entry.id = item.attrib["id"]
        entry.name = item.attrib["name"].split(" ")[0]
        entry.type = item.attrib["type"]

        entry.link = item.attrib.get("link", "")
        entry.reaction = item.attrib.get("reaction", "")

        for child in item:
            if child.tag == "graphics":
                entry.graphics = Graphics.parse(child)
            elif child.tag == "component":
                entry.components.append(Component.parse(child))

        return entry


    def __str__(self) -> str:
        """
        Build Entry summary string

        :return: str
        """

        return f"<Entry id={self.id} name='{self.name}' type='{self.type}'>"


class Pathway:
    """
    KEGG Pathway object.
    The KEGG pathway object stores graphics information and related objects.
    """
    # pylint: disable=too-many-instance-attributes

    def __init__(
        self,
        name: str,
        org: str,
        number: str,
        ) -> None:
        """
        Init KEGG Pathway model.
        """

        # REQUIRED parameter of pathway element
        self.name: str = name
        self.org: str = org
        self.number: str = number

        # IMPLIED
        self.title: Optional[str] = None
        self.image: Optional[str] = None
        self.link: Optional[str] = None

        # Children
        self.relations: List[Relation] = []
        self.entries: List[Entry] = []
        # self.reactions: List[Reaction] = []




    @staticmethod
    def parse(data: Union[Element, str]) -> "Pathway":
        """
        Parsing xml String in KEGG Pathway.
        :param data: str
        :return: Pathway
        """

        # Generate correct format from string or XML element object
        item: Element = parse_xml(xml_object_or_string=data)


        # Init pathway instance with all required attributes
        pathway: Pathway = Pathway(
            name=get_attribute(element=item, key="name"),
            org=get_attribute(element=item, key="org"),
            number=get_attribute(element=item, key="number"),
        )


        # Parse optional KGML pathway attributes
        pathway.title = item.attrib.get("title")
        pathway.image = item.attrib.get("image")
        pathway.link = item.attrib.get("link")


        # Parse child items of pathway
        for child in item:
            if child.tag == "entry":
                pathway.entries.append(Entry.parse(child))
            elif child.tag == "relation":
                pathway.relations.append(Relation.parse(child))
            # elif child.tag == "reaction":
            #     # TODO: implement parsing, not needed for current use case
            #     pass


        return pathway









    def get_entry_by_id(self, entry_id: Union[str, int]):
        """
        Get pathway Entry by id

        :param entry_id: Union[str, int]
        :return: Any
        """

        for item in self.entries:
            if int(item.id) == int(entry_id):
                return item
        return None


    def matches(self, gene_id_list: list):
        """
        Return percent value for matching genes. [int(<gene_id>), ...]

        :param gene_id_list: list
        :return: float
        """

        # run over entry:gene_id -> return count / len(entry)
        count = 0
        for entry in self.entries:
            if entry in gene_id_list:
                count += 1
        return count / len(self.entries)


    def get_genes(self) -> dict:
        """
        List all genes from pathway {<gene_id>: <gene_name>}

        :return: dict
        """

        result: dict = {}
        for entry in self.entries:
            if entry.type == "gene":
                if entry.graphics is not None:
                    result[entry.get_id()] = entry.graphics.name

        # logging.debug("Get %d unique genes from pathway", len(result.keys()))

        return result


    def __str__(self) -> str:
        """
        Build string summary for KEGG pathway.
        :return: str
        """
        return f"<Pathway path:{self.org}{self.number} title='{self.title}'>"


