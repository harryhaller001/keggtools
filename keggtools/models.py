""" KEGG pathway models to parse object relational """
# pylint: disable=invalid-name,too-few-public-methods,redefined-builtin,too-many-arguments

# TODO: add to_xml() method to all classes to generate KGML xml object/string from instances
# TODO: add abstract parent class for all classes (KGMLElement)
# containing .parse() -> @, .to_xml() -> Element

from xml.etree.ElementTree import Element
from typing import List, Union, Optional

import re

from .const import (
    RELATION_TYPES,
    # RELATION_SUBTYPES,
    ENTRY_TYPE,
    GRAPHIC_TYPE,
)

from .utils import (
    get_attribute,
    get_numeric_attribute,
    parse_xml,
)



# TODO: functions needed ???

def is_valid_pathway_org(value: str) -> bool:
    """
    Check if org identifier is valid.
    """

    # Organism must be 3 letter code
    # Identifier can also be KO or Enzyme identifer
    # TODO: validate with KEGG organism list
    return re.match(pattern=r"^(ko|ec|[a-z]{3})$", string=value) is not None


def is_valid_pathway_number(value: str) -> bool:
    """
    Check if pathway number is valid.
    """

    # KEGG pathway number must be a 5 digit number
    return re.match(pattern=r"^([0-9]{5})$", string=value) is not None


def is_valid_pathway_name(value: str) -> bool:
    """
    Check if combined pathway identifer is valid. String must match "path:<org><number>".
    """

    return re.match(pattern=r"^path:(ko|ec|[a-z]{3})([0-9]{5})$", string=value) is not None


def is_valid_hex_color(value: str) -> bool:
    """
    Check if string is a valid hex color.
    """
    return re.match(pattern=r"^\#([a-fA-F0-9]{6})$", string=value) is not None



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


    def __str__(self) -> str:
        """
        Generate string from Subtype instance.
        """
        return f"<Subtype name='{self.name}' value='{self.value}'>"






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

    def __init__(
        self,
        x: Optional[str] = None,
        y: Optional[str] = None,
        width: Optional[str] = None,
        height: Optional[str] = None,
        coords: Optional[str] = None,
        name: Optional[str] = None,
        type: Optional[str] = None,
        fgcolor: Optional[str] = None,
        bgcolor: Optional[str] = None,
    ) -> None:
        """
        Init Graphics model instance.
        """

        # All parameter are implied (optional)
        self.x: Optional[str] = x
        self.y: Optional[str] = y
        self.width: Optional[str] = width
        self.height: Optional[str] = height
        self.coords: Optional[str] = coords
        self.name: Optional[str] = name
        self.type: Optional[str] = type
        self.fgcolor: Optional[str] = fgcolor
        self.bgcolor: Optional[str] = bgcolor


        # Validate parameter if not None

        # Check type is in list of valid types
        if self.type is not None and self.type not in GRAPHIC_TYPE:
            raise ValueError(f"Type '{self.type}' is not a valid graphics type.")

        # Check foreground and background color are hex format
        if self.fgcolor is not None and is_valid_hex_color(value=self.fgcolor) is False:
            raise ValueError("Fgcolor is not a valid hex color.")

        if self.bgcolor is not None and is_valid_hex_color(value=self.bgcolor) is False:
            raise ValueError("Bgcolor is not a valid hex color.")


        # TODO Checkx,y,width and height are numeric
        if self.x is not None and str.isdigit(self.x) is False:
            raise ValueError("Value x is not a number.")


    @staticmethod
    def parse(item: Element) -> "Graphics":
        """
        Parse xml ElementTree into KEGG Graphics
        :param item: ElementTree
        :return: Graphics
        """

        # Check xml tag
        assert item.tag == "graphics"

        # Parse attributes from XML element
        graphic: Graphics = Graphics(
            x = item.attrib.get("x"),
            y = item.attrib.get("y"),
            width = item.attrib.get("width"),
            height = item.attrib.get("height"),
            name = item.attrib.get("name"),
            type = item.attrib.get("type"),
            fgcolor = item.attrib.get("fgcolor"),
        )

        return graphic



    def __str__(self) -> str:
        """
        Return Graphics instance summary string.
        :return: str
        """
        return f"<Graphics name='{self.name}'>"



class Entry:
    """
    Entry model class.
    """

    def __init__(
        self,
        id: str,
        name: str,
        type: str,
        link: Optional[str] = None,
        reaction: Optional[str] = None,
    ) -> None:
        """
        Init entry model instance.
        """

        # required
        self.id: str = id
        self.name: str = name
        self.type: str = type

        # TODO: validate entry id and name


        if self.type not in ENTRY_TYPE:
            raise ValueError(f"Type '{self.type}' is not in list of valid entry types.")


        # optional (implied)
        self.link: Optional[str] = link
        self.reaction: Optional[str] = reaction

        # TODO: validate reaction if not None


        # Implied child instances
        self.graphics: Optional[Graphics] = None
        self.components: List[Component] = []



    @staticmethod
    def parse(item: Element) -> "Entry":
        """
        Parsing xml ElementTree into KEGG Entry

        :param item: ElementTree
        :return: Entry
        """

        # Generate entry instance from required attributes
        entry: Entry = Entry(
            id=get_numeric_attribute(element=item, key="id"),
            name=get_attribute(element=item, key="name"),
            type=get_attribute(element=item, key="type"),
        )


        # Set optional parameter to entry instance
        entry.link = item.attrib.get("link")
        entry.reaction = item.attrib.get("reaction")


        # Iterate over children and parse graphics, ...
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
        return f"<Entry id='{self.id}' name='{self.name}' type='{self.type}'>"



    def get_gene_id(self) -> str:
        """
        Parse variable 'name' into KEGG ID
        :return: str
        """

        # TODO: validate return valid !!

        return self.name.split(":")[1]




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
        title: Optional[str] = None,
        image: Optional[str] = None,
        link: Optional[str] = None,
        ) -> None:
        """
        Init KEGG Pathway model.
        """

        # REQUIRED parameter of pathway element
        self.name: str = name
        self.org: str = org
        self.number: str = number

        # Check all required parameter formats
        if not is_valid_pathway_name(value=name):
            raise ValueError(f"Pathway name '{name}' is not a valid value.")

        if not is_valid_pathway_org(value=org):
            raise ValueError(f"Pathway org '{org}' is not a valid value.")

        if not is_valid_pathway_number(value=number):
            raise ValueError(f"Pathway number '{number}' is not a valid value.")


        # IMPLIED
        self.title: Optional[str] = title
        self.image: Optional[str] = image
        self.link: Optional[str] = link

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
                    result[entry.id] = entry.graphics.name

        # logging.debug("Get %d unique genes from pathway", len(result.keys()))

        return result


    def __str__(self) -> str:
        """
        Build string summary for KEGG pathway.
        :return: str
        """
        return f"<Pathway path:{self.org}{self.number} title='{self.title}'>"


