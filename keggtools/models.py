""" KEGG pathway models to parse object relational """
# pylint: disable=invalid-name,too-few-public-methods

import logging
from xml.etree import ElementTree
from xml.etree.ElementTree import Element
from typing import Any, Dict, List, Union, Optional


from .const import (
    RELATION_TYPES,
    RELATION_SUBTYPES,
    ENTRY_TYPE,
    GRAPHICS_TYPE,
)

from .utils import is_valid_numeric_attribute, is_valid_attribute



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
        self.subtypes: Dict[str, str] = {}


    @staticmethod
    def parse(item: Element) -> "Relation":
        """
        Parse xml ElementTree into KEGG Relation.
        :param item: ElementTree
        :return: Relation
        """

        # Check tag of relation is correct
        assert item.tag == "relation"


        # Create relation instance from attributes
        relation: Relation = Relation()


        # Check attributes
        if is_valid_numeric_attribute(element=item, key="entry1"):

            # Set entry1 attribute to relation instance
            relation.entry1 = item.attrib.get("entry1")
        else:
            raise ValueError("Attribute 'entry1' from relation is not a string.")


        if is_valid_numeric_attribute(element=item, key="entry2"):

            # Set entry2 attribute to relation instance
            relation.entry2 = item.attrib.get("entry2")
        else:
            raise ValueError("Attribute 'entry2' from relation is not a string.")



        if is_valid_attribute(element=item, key="type"):

            # Check relation type is list of allowed relation types
            if item.attrib.get("type") not in RELATION_TYPES:
                raise ValueError("Attribute 'type' has invalid value.")

            # Set type attribute to relation instance
            relation.type = item.attrib.get("type")
        else:
            raise ValueError("Attribute 'type' from relation is not a string.")



        # for child in item:
        #     if child.tag == "subtype":
        #         # Parse subtypes
        #         _name: Any = child.attrib.get("name")
        #         _value: Any = child.attrib.get("value")
        #         if isinstance(_name, str) is True:
        #             relation.subtypes[_name] = _value

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
        Init Component model
        """

        self.id: str = id


    @staticmethod
    def parse(item: Element) -> "Component":
        """
        Parsing ElementTree into Component

        :param item: ElementTree
        :return: Component
        """

        assert item.tag == "component"

        # Get component id from xml
        component_id: Optional[str] = item.attrib.get("id")
        if component_id is None:
            raise TypeError("Component id is not type string.")

        # Create component instance
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


class KEGGPathway:
    """
    KEGG Pathway
    """
    # pylint: disable=too-many-instance-attributes

    def __init__(self):
        """
        Init KEGG Pathway model
        """

        # REQUIRED
        self.name = ""
        self.org = ""
        self.number = ""

        # IMPLIED
        self.title = ""
        self.image = ""
        self.link = ""

        # Children
        self.relations = []
        self.entries = []
        self.reactions = []


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
                result[entry.get_id()] = entry.graphics.name

        # logging.debug("Get %d unique genes from pathway", len(result.keys()))

        return result


    def __str__(self) -> str:
        """
        Build string summary for KEGG pathway

        :return: str
        """

        return f"<KEGGPathway path:{self.org}{self.number} title='{self.title}'>"




    @staticmethod
    def parse(data: str) -> "KEGGPathway":
        """
        Parsing xml String in KEGG Pathway

        :param data: str
        :return: KEGGPathway
        """

        pathw: KEGGPathway = KEGGPathway()

        root = ElementTree.fromstring(data)

        pathw.name = root.attrib["name"]
        pathw.org = root.attrib["org"]
        pathw.number = root.attrib["number"]

        pathw.title = root.attrib.get("title", "")
        pathw.image = root.attrib.get("image", "")
        pathw.link = root.attrib.get("link", "")

        for child in root:
            if child.tag == "entry":
                pathw.entries.append(Entry.parse(child))
            elif child.tag == "relation":
                pathw.relations.append(Relation.parse(child))
            elif child.tag == "reaction":
                # TODO: implement parsing, not needed for current use case
                pass
            else:
                logging.debug(child.tag)

        return pathw






# class Subtype:
#     """
#     Subtype model class.
#     """

#     def __init__(
#         self,
#         name: str,
#         value: str,
#     ) -> None:
#         """
#         Init Subtype model instance.
#         """
#         self.name: str = name
#         self.value: str = value


#     @staticmethod
#     def parse(item: Element) -> "Subtype":
#         """
#         Parse subtype XML Element.
#         """

#         if item.tag != "subtype":
#             raise ValueError("Tag of XML element is not 'subtype'.")


#         # Parse subtypes
#         _name: Optional[str] = item.attrib.get("name")
#         _value: Optional[str] = item.attrib.get("value")

#         if _name is None or _value is None:
#             raise TypeError("Attribute 'name' or 'value' is not type string.")

#         return Subtype(name=_name, value=_value)

