""" KEGG pathway models to parse object relational """
# pylint: disable=invalid-name,redefined-builtin


from xml.etree.ElementTree import Element
from typing import List, Union, Optional

from .const import (
    RELATION_TYPES,
    RELATION_SUBTYPES,
    ENTRY_TYPE,
    GRAPHIC_TYPE,
)

from .utils import (
    get_attribute,
    get_numeric_attribute,
    parse_xml,
    is_valid_pathway_number,
    is_valid_hex_color,
    is_valid_pathway_name,
    is_valid_pathway_org,
)




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

        :param str name: Name of subtype. Must match list of valid subtypes.
        :param str value: Value of subtype.
        """

        # check for valid subtype names in RELATION_SUBTYPES
        if name not in RELATION_SUBTYPES:
            raise ValueError(f"Name of relation subtype '{name}' is not in list of valid subtypes.")

        self.name: str = name
        self.value: str = value



    @staticmethod
    def parse(item: Element) -> "Subtype":
        """
        Parse Subtype XML element.

        :param xml.etree.ElementTree.Element item: XML element.
        :return: Parsed Subtype instance.
        :rtype: Subtype
        """

        # check correct type
        assert item.tag == "subtype"

        # Generate and return subtype instance
        return Subtype(
            name=get_attribute(element=item, key="name"),
            value=get_attribute(element=item, key="value")
        )


    def __str__(self) -> str:
        """
        Generate string from Subtype instance.

        :return: String of Subtype instance.
        :rtype: str
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

        :param str entry1: Source entry of relation.
        :param str entry2: Destination entry of relation.
        :param str type: Type of Relation. Must be contained in list of valid relation types.
        """

        # Check if type is in valid relation types
        if type not in RELATION_TYPES:
            raise ValueError(f"Relation type '{type}' not in list of valid types.")

        self.entry1: str = entry1
        self.entry2: str = entry2
        self.type: str = type
        self.subtypes: List[Subtype] = []


    @staticmethod
    def parse(item: Element) -> "Relation":
        """
        Parse XML element into Relation instance.

        :param xml.etree.ElementTree.Element item: XML element to parse.
        :return: Relation instance.
        :rtype: Relation
        """

        # Check tag of relation is correct
        assert item.tag == "relation"


        # Create relation instance from attributes
        relation: Relation = Relation(
            entry1=get_numeric_attribute(element=item, key="entry1"),
            entry2=get_numeric_attribute(element=item, key="entry2"),
            type=get_attribute(element=item, key="type"),
        )


        # Parse Child items of xml element by iterating of child elements
        for child in item:
            relation.subtypes.append(Subtype.parse(item=child))


        return relation


    def __str__(self) -> str:
        """
        Generate string from relation instance.

        :return: String of Relation instance.
        :rtype: str
        """
        return f"<Relation {self.entry1}->{self.entry2} type='{self.type}'>"




class Component:
    """
    Component model.
    """

    def __init__(self, id: str) -> None:
        """
        Init Component model.

        :param str id: Id of component.
        """

        # id can't be empty
        if id == "":
            raise ValueError("Component id can't be empty.")


        # TODO: Check pattern of component id
        # TODO: component id should reference an existing entry !

        self.id: str = id


    @staticmethod
    def parse(item: Element) -> "Component":
        """
        Parsing ElementTree into Component.

        :param xml.etree.ElementTree.Element item: XML element to parse.
        :return: Parsed Component instance.
        :rtype: Component
        """

        # Check for correct xml tag
        assert item.tag == "component"

        # Create component instance from id attribute
        return Component(id=get_attribute(element=item, key="id"))


    def __str__(self) -> str:
        """
        Build string of component instance.

        :return: String of Component instance.
        :rtype: str
        """
        return f"<Component id='{self.id}'>"



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

        :param Optional[str] x:
        :param Optional[str] y:
        :param Optional[str] width:
        :param Optional[str] height:
        :param Optional[str] coords:
        :param Optional[str] name:
        :param Optional[str] type:
        :param Optional[str] fgcolor:
        :param Optional[str] bgcolor:
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


        # Check x,y,width and height are numeric (only if not None)
        if self.x is not None and str.isdigit(self.x) is False:
            raise ValueError("Value x is not a number.")

        if self.y is not None and str.isdigit(self.y) is False:
            raise ValueError("Value y is not a number.")

        if self.width is not None and str.isdigit(self.width) is False:
            raise ValueError("Value width is not a number.")

        if self.height is not None and str.isdigit(self.height) is False:
            raise ValueError("Value height is not a number.")


    @staticmethod
    def parse(item: Element) -> "Graphics":
        """
        Parse XML element into Graphics instance.

        :param xml.etree.ElementTree.Element item: XML element to parse.
        :return: Parsed Graphics instance.
        :rtype: Graphics
        """

        # Check xml tag
        assert item.tag == "graphics"

        # Parse attributes from XML element
        return Graphics(
            x = item.attrib.get("x"),
            y = item.attrib.get("y"),
            width = item.attrib.get("width"),
            height = item.attrib.get("height"),
            name = item.attrib.get("name"),
            type = item.attrib.get("type"),
            fgcolor = item.attrib.get("fgcolor"),
            bgcolor = item.attrib.get("bgcolor"),
            coords = item.attrib.get("coords"),
        )


    def __str__(self) -> str:
        """
        Return Graphics instance summary string.

        :return: String of Graphics instance.
        :rtype: str
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

        :param str id: Id of Entry.
        :param str name: Name of Entry.
        :param str type: Type of Entry. Must be contained in list of valid entry types.
        :param Optional[str] link: Link to KEGG database with reference to entry.
        :param Optional[str] reaction: Reaction TODO: specify. Is str format correct?
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
        Parsing XML element into Entry instance.

        :param xml.etree.ElementTree.Element item: XML element to parse.
        :return: Parsed Entry instance.
        :rtype: Entry
        """

        # Generate entry instance from required attributes
        entry: Entry = Entry(
            id=get_numeric_attribute(element=item, key="id"),
            name=get_attribute(element=item, key="name"),
            type=get_attribute(element=item, key="type"),
            link=item.attrib.get("link"),
            reaction=item.attrib.get("reaction"),
        )

        # Iterate over children and parse graphics, components, ...
        for child in item:
            if child.tag == "graphics":
                entry.graphics = Graphics.parse(child)
            elif child.tag == "component":
                entry.components.append(Component.parse(child))

        return entry


    def __str__(self) -> str:
        """
        Build Entry summary string.

        :return: String of Entry instance.
        :rtype: str
        """
        return f"<Entry id='{self.id}' name='{self.name}' type='{self.type}'>"



    def get_gene_id(self) -> str:
        """
        Parse variable 'name' of Entry into KEGG id.

        :return: KEGG id
        :rtype: str
        """

        # TODO: validate return valid !!
        # r"^([a-z]){3}([0-9]){5}$"

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

        :param str name: Name of pathway, which is the full KEGG identifier.
        :param str org: Organism code.
        :param str number: Number of pathway.
        :param Optional[str] title: Title of pathway.
        :param Optional[str] image: Image for pathway provided by KEGG database.
        :param Optional[str] link: Link to pathway in KEGG database.
        """

        # required parameter of pathway element
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


        # Check match of number, org and name
        if self.name != f"path:{self.org}{self.number}":
            raise ValueError("Mismatch of arguments name, org and number.")


        # implied
        self.title: Optional[str] = title
        self.image: Optional[str] = image
        self.link: Optional[str] = link

        # children
        self.relations: List[Relation] = []
        self.entries: List[Entry] = []
        # TODO self.reactions: List[Reaction] = []




    @staticmethod
    def parse(data: Union[Element, str]) -> "Pathway":
        """
        Parsing XML string or element in Pathway instance.

        :param Union[Element, str] data: String or XML element to parse.
        :return: Parsed Pathway instance.
        :rtype: Pathway
        """

        # Generate correct format from string or XML element object
        item: Element = parse_xml(xml_object_or_string=data)


        # Init pathway instance with all required attributes
        pathway: Pathway = Pathway(
            name=get_attribute(element=item, key="name"),
            org=get_attribute(element=item, key="org"),
            number=get_attribute(element=item, key="number"),
            title=item.attrib.get("title"),
            image=item.attrib.get("image"),
            link=item.attrib.get("link"),
        )


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



    def get_entry_by_id(self, entry_id: str) -> Optional[Entry]:
        """
        Get pathway Entry object by id.

        :param str entry_id: Id of Entry.
        :return: Returns Entry instance if id is found in Pathway. Otherwise returns None.
        :rtype: Optional[Entry]
        """

        for item in self.entries:
            if item.id == entry_id:
                return item
        return None



    def get_genes(self) -> List[str]:
        """
        List all genes from pathway.

        :return: List of entry ids with type gene.
        :rtype: List[str]
        """

        result: List[str] = []

        # Iterate of entries and get all gene type
        # Keep list of genes unique
        for entry in self.entries:
            if entry.type == "gene":

                # Get name of entry (KEGG identifier)
                if " " in entry.name:
                    # Check if name contains a space, which indicates list of multiple identifier
                    splitted_entries: List[str] = entry.name.split(" ")
                    for single_entry in splitted_entries:
                        if single_entry not in result:
                            result.append(single_entry)


                elif entry.name not in result:
                    result.append(entry.name)

        return result


    def __str__(self) -> str:
        """
        Build string summary for KEGG pathway.

        :return: String of Pathway instance.
        :rtype: str
        """
        return f"<Pathway path:{self.org}{self.number} title='{self.title}'>"
