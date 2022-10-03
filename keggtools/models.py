""" KEGG pathway models to parse object relational """
# pylint: disable=invalid-name,redefined-builtin,too-many-lines


# from warnings import warn
from datetime import datetime
from xml.etree import ElementTree
from xml.etree.ElementTree import Element
from typing import List, Union, Optional

from .const import (
    REACTION_TYPE,
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
            raise ValueError(
                f"Name of relation subtype '{name}' is not in list of valid subtypes."
            )

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
            value=get_attribute(element=item, key="value"),
        )

    def to_xml(self) -> Element:
        """
        Generate XML string from Subtype element.

        :return: XML string.
        :rtype: xml.etree.ElementTree.Element
        """

        return Element(
            "subtype",
            attrib={"name": self.name, "value": self.value},
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

    def to_xml(self) -> Element:
        """
        Generate XML string from Relation element.

        :return: XML string.
        :rtype: xml.etree.ElementTree.Element
        """

        return Element(
            "relation",
            attrib={
                "entry1": self.entry1,
                "entry2": self.entry2,
                "type": self.type,
            },
        )

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

    def to_xml(self) -> Element:
        """
        Generate XML string from Component element.

        :return: XML string.
        :rtype: xml.etree.ElementTree.Element
        """

        return Element(
            "component",
            attrib={
                "id": self.id,
            },
        )

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

    # pylint: disable=too-many-instance-attributes

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

        :param typing.Optional[str] x:
        :param typing.Optional[str] y:
        :param typing.Optional[str] width:
        :param typing.Optional[str] height:
        :param typing.Optional[str] coords:
        :param typing.Optional[str] name:
        :param typing.Optional[str] type:
        :param typing.Optional[str] fgcolor:
        :param typing.Optional[str] bgcolor:
        """

        # pylint: disable=too-many-arguments

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
            x=item.attrib.get("x"),
            y=item.attrib.get("y"),
            width=item.attrib.get("width"),
            height=item.attrib.get("height"),
            name=item.attrib.get("name"),
            type=item.attrib.get("type"),
            fgcolor=item.attrib.get("fgcolor"),
            bgcolor=item.attrib.get("bgcolor"),
            coords=item.attrib.get("coords"),
        )

    def to_xml(self) -> Element:
        """
        Generate XML string from Graphics element.

        :return: XML string.
        :rtype: xml.etree.ElementTree.Element
        """

        graphics_element: Element = Element(
            "graphics",
        )

        if self.x is not None:
            graphics_element.attrib["x"] = self.x

        if self.y is not None:
            graphics_element.attrib["y"] = self.y

        if self.width is not None:
            graphics_element.attrib["width"] = self.width

        if self.height is not None:
            graphics_element.attrib["height"] = self.height

        if self.name is not None:
            graphics_element.attrib["name"] = self.name

        if self.type is not None:
            graphics_element.attrib["type"] = self.type

        if self.fgcolor is not None:
            graphics_element.attrib["fgcolor"] = self.fgcolor

        if self.bgcolor is not None:
            graphics_element.attrib["bgcolor"] = self.bgcolor

        if self.coords is not None:
            graphics_element.attrib["coords"] = self.coords

        return graphics_element

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
        :param typing.Optional[str] link: Link to KEGG database with reference to entry.
        :param typing.Optional[str] reaction: Reaction TODO: specify. Is str format correct?
        """

        # pylint: disable=too-many-arguments

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

    @property
    def has_multiple_names(self) -> bool:
        """
        Checks if entry has multiple names that are space seperated.

        :return: Retruns True if entry has multiple names.
        :rtype: bool
        """

        return len(self.name.split(" ")) > 1

    @staticmethod
    def parse(item: Element) -> "Entry":
        """
        Parsing XML element into Entry instance.

        :param xml.etree.ElementTree.Element item: XML element to parse.
        :return: Parsed Entry instance.
        :rtype: Entry
        """

        assert item.tag == "entry"

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

    def to_xml(self) -> Element:
        """
        Generate XML string from Entry element.

        :return: XML string.
        :rtype: xml.etree.ElementTree.Element
        """

        entry_element: Element = Element(
            "entry", attrib={"id": self.id, "name": self.name, "type": self.type}
        )

        # Add optional attributes to xml element
        if self.link is not None:
            entry_element.attrib["link"] = self.link

        if self.reaction is not None:
            entry_element.attrib["reaction"] = self.reaction

        # generate xml element from children elements

        # Add graphics element to entry element
        if self.graphics is not None:
            entry_element.append(self.graphics.to_xml())

        # Iterate over components and add to entry element
        for component in self.components:
            entry_element.append(component.to_xml())

        return entry_element

    def __str__(self) -> str:
        """
        Build Entry summary string.

        :return: String of Entry instance.
        :rtype: str
        """
        return f"<Entry id='{self.id}' name='{self.name}' type='{self.type}'>"

    def get_gene_id(self) -> List[str]:
        """
        Parse variable 'name' of Entry into KEGG id.

        :return: List of KEGG identifier.
        :rtype: typing.List[str]
        """

        # TODO: validate return valid !!
        # r"^([a-z]){3}([0-9]){5}$"

        # return self.name.split(":")[1]
        return [value.split(":")[1] for value in self.name.split(" ")]


class Alt:
    """
    Alt model.
    """

    def __init__(self, name: str) -> None:
        """
        Init Alt instance.

        :param str name: Alt element name.
        """

        self.name: str = name

    @staticmethod
    def parse(item: Element) -> "Alt":
        """
        Parse Alt instance from XML element.

        :param xml.etree.ElementTree.Element item: XML element to parse.
        :rtype: Alt
        :return: Parsed Alt element.
        """
        assert item.tag == "alt"

        return Alt(name=get_attribute(element=item, key="name"))

    def to_xml(self) -> Element:
        """
        Generate XML string from Alt element.

        :return: XML string.
        :rtype: xml.etree.ElementTree.Element
        """

        return Element(
            "alt",
            attrib={
                "name": self.name,
            },
        )

    def __str__(self) -> str:
        """
        Build string from Alt instance.

        :return: String of Alt instance.
        :rtype: str
        """

        return f"<Alt name='{self.name}'>"


class Product:
    """
    Reaction Product model.
    """

    def __init__(self, id: str, name: str, alt: Optional[Alt] = None) -> None:
        """
        Init Product instance.

        :param str id: Identifier of Product in pathway.
        :param str name: KEGG identifier of compound.
        :param Alt alt: Alternative name of element.
        """

        # TODO: verify correct format

        self.id: str = id
        self.name: str = name
        self.alt: Optional[Alt] = alt

    @staticmethod
    def parse(item: Element) -> "Product":
        """
        Parse XML element instance to Product model instance.

        :param xml.etree.ElementTree.Element item: XML element to parse.
        :return: Parsed Product model.
        :rtype: Product
        """

        assert item.tag == "product"

        parsed_product: Product = Product(
            id=get_attribute(element=item, key="id"),
            name=get_attribute(element=item, key="name"),
        )

        # Parse child alt elements
        for child in item:
            if child.tag == "alt":

                # TODO warn if overwrite
                # TODO: or raise exception (only 1 alt should be presnet)
                # if parsed_product.alt is not None:
                #     warn(message="'Alt'")

                parsed_product.alt = Alt.parse(item=child)

        return parsed_product

    def to_xml(self) -> Element:
        """
        Generate XML string from Product element.

        :return: XML string.
        :rtype: xml.etree.ElementTree.Element
        """

        product_element: Element = Element(
            "product",
            attrib={
                "id": self.id,
                "name": self.name,
            },
        )

        # Add optional alt element if exist
        if self.alt is not None:
            product_element.append(self.alt.to_xml())

        return product_element

    def __str__(self) -> str:
        """
        Build string from Product instance.

        :return: String of Product instance.
        :rtype: str
        """
        return f"<Product id='{self.id}' name='{self.name}'>"


class Substrate:
    """
    reaction Substrate model
    """

    def __init__(
        self,
        id: str,
        name: str,
        alt: Optional[Alt] = None,
    ) -> None:
        """
        Init Substrate instance.

        :param str id: Identifier of Substrate in pathway.
        :param str name: KEGG identifier of compound.
        :param Alt alt: Alternative name of element.
        """

        # TODO: verify correct format

        self.id: str = id
        self.name: str = name
        self.alt: Optional[Alt] = alt

    @staticmethod
    def parse(item: Element) -> "Substrate":
        """
        Parse XML element instance to Substrate model instance.

        :param xml.etree.ElementTree.Element item: XML element to parse.
        :return: Parsed Substrate model.
        :rtype: Substrate
        """

        assert item.tag == "substrate"

        parsed_substrate: Substrate = Substrate(
            id=get_attribute(element=item, key="id"),
            name=get_attribute(element=item, key="name"),
        )

        # Parse child alt elements
        for child in item:
            if child.tag == "alt":

                # TODO warn if overwrite
                # TODO: or raise exception (only 1 alt should be presnet)
                # if parsed_substrate.alt is not None:
                #     warn(message="'Alt'")

                parsed_substrate.alt = Alt.parse(item=child)

        return parsed_substrate

    def to_xml(self) -> Element:
        """
        Generate XML string from Substrate element.

        :return: XML string.
        :rtype: xml.etree.ElementTree.Element
        """

        substrate_element: Element = Element(
            "substrate",
            attrib={
                "id": self.id,
                "name": self.name,
            },
        )

        # Add optional alt element if exist
        if self.alt is not None:
            substrate_element.append(self.alt.to_xml())

        return substrate_element

    def __str__(self) -> str:
        """
        Build string from Substrate instance.

        :return: String of Substrate instance.
        :rtype: str
        """
        return f"<Substrate id='{self.id}' name='{self.name}'>"


class Reaction:
    """
    Reaction model.
    """

    def __init__(
        self,
        id: str,
        name: str,
        type: str,
    ) -> None:
        """
        Init Reaction model instance.

        :param str id: Identifier of reaction.
        :param str name: KEGG identifer of reaction.
        :param str type: Type of reaction. Must be contained in list of valid reaction types.
        """

        if type not in REACTION_TYPE:
            raise ValueError("Type of reaction is not in list of valid reaction types.")

        # TODO: check valid reaction id
        self.id = id
        self.name = name
        self.type = type

        # Child elements of reaction
        self.products: List[Product] = []
        self.substrates: List[Substrate] = []

    @staticmethod
    def parse(item: Element) -> "Reaction":
        """
        Parse XML element instance to Reaction model instance.

        :param xml.etree.ElementTree.Element item: XML element to parse.
        :return: Parsed Reaction model.
        :rtype: Reaction
        """

        assert item.tag == "reaction"

        # Parse reaction instance from xml attributes
        parsed_reaction: Reaction = Reaction(
            id=get_attribute(element=item, key="id"),
            name=get_attribute(element=item, key="name"),
            type=get_attribute(element=item, key="type"),
        )

        # Parse product and substrate from child elements
        for child in item:
            if child.tag == "product":
                parsed_reaction.products.append(Product.parse(child))
            elif child.tag == "substrate":
                parsed_reaction.substrates.append(Substrate.parse(child))

        return parsed_reaction

    def to_xml(self) -> Element:
        """
        Generate XML string from Reaction element.

        :return: XML string.
        :rtype: xml.etree.ElementTree.Element
        """

        reaction_element: Element = Element(
            "reaction",
            attrib={
                "id": self.id,
                "name": self.name,
                "type": self.type,
            },
        )

        # Add substrate and product to reaction element

        for substrate in self.substrates:
            reaction_element.append(substrate.to_xml())

        for product in self.products:
            reaction_element.append(product.to_xml())

        return reaction_element

    def __str__(self) -> str:
        """
        Build string of reaction instance.

        :return: String of Reaction instance.
        :rtype: str
        """

        return f"<Reaction id='{self.id}' name='{self.name}'>"


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
        :param typing.Optional[str] title: Title of pathway.
        :param typing.Optional[str] image: Image for pathway provided by KEGG database.
        :param typing.Optional[str] link: Link to pathway in KEGG database.
        """

        # pylint: disable=too-many-arguments

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
        self.reactions: List[Reaction] = []

    @staticmethod
    def parse(data: Union[Element, str]) -> "Pathway":
        """
        Parsing XML string or element in Pathway instance.

        :param typing.Union[xml.etree.ElementTree.Element, str] data: String or XML element to parse.
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
            elif child.tag == "reaction":
                pathway.reactions.append(Reaction.parse(child))

        return pathway

    def to_xml(self) -> Element:
        """
        Generate XML element from Pathway instance and its children.

        :return: XML element in KGML format.
        :rtype: xml.etree.ElementTree.Element
        """

        pathway_element: Element = Element(
            "pathway",
            attrib={
                "name": self.name,
                "org": self.org,
                "number": self.number,
            },
        )

        # Adding optional attributes to pathway root element
        if self.title is not None:
            pathway_element.attrib["title"] = self.title

        if self.link is not None:
            pathway_element.attrib["link"] = self.link

        if self.image is not None:
            pathway_element.attrib["image"] = self.image

        # add children entries, relations and reactions

        for entry in self.entries:
            pathway_element.append(entry.to_xml())

        for relation in self.relations:
            pathway_element.append(relation.to_xml())

        for reaction in self.reactions:
            pathway_element.append(reaction.to_xml())

        return pathway_element

    def to_xml_string(self) -> str:
        """
        Generate XML string from pathway instance.

        :return: XML string in KGML format.
        :rtype: str
        """

        # Generate xml header string
        # docstring is not supported by build-in xml builer
        xml_timestamp: str = (
            datetime.now().astimezone().strftime("%b %d, %Y %H:%M:%S (GMT%z)")
        )
        xml_header: str = (
            '<?xml version="1.0"?>\n'
            '<!DOCTYPE pathway SYSTEM "http://www.kegg.jp/kegg/xml/KGML_v0.7.2_.dtd">\n'
            f"<!-- Creation date: {xml_timestamp} -->\n"
        )

        pathway_element: Element = self.to_xml()

        xml_content: str = ElementTree.tostring(pathway_element).decode("utf-8")

        return xml_header + xml_content

    def get_entry_by_id(self, entry_id: str) -> Optional[Entry]:
        """
        Get pathway Entry object by id.

        :param str entry_id: Id of Entry.
        :return: Returns Entry instance if id is found in Pathway. Otherwise returns None.
        :rtype: typing.Optional[Entry]
        """

        for item in self.entries:
            if item.id == entry_id:
                return item
        return None

    def get_genes(self) -> List[str]:
        """
        List all genes from pathway.

        :return: List of entry ids with type gene.
        :rtype: typing.List[str]
        """

        result: List[str] = []

        # Iterate of entries and get all gene type
        # Keep list of genes unique
        for entry in self.entries:
            if entry.type == "gene":

                # Get name of entry (KEGG identifier)
                # if " " in entry.name:
                #     # Check if name contains a space, which indicates list of multiple identifier
                #     splitted_entries: List[str] = entry.name.split(" ")
                #     for single_entry in splitted_entries:
                #         if single_entry not in result:
                #             result.append(single_entry)

                # elif entry.name not in result:
                #     result.append(entry.name)

                for gene_id in entry.get_gene_id():
                    if gene_id not in result:
                        result.append(gene_id)

        return result

    def __str__(self) -> str:
        """
        Build string summary for KEGG pathway.

        :return: String of Pathway instance.
        :rtype: str
        """
        return f"<Pathway path:{self.org}{self.number} title='{self.title}'>"

    # TODO: has to be implemented
    # def merge(self) -> "Pathway":
    #     """
    #     Merge identical entries in Pathway together and generate new pathway instance.

    #     :return: Merged Pathway instance.
    #     :rtype: Pathway
    #     """

    #     merged_pathway: Pathway = Pathway(
    #         name=self.name,
    #         org=self.org,
    #         number=self.number,
    #         title=self.title,
    #     )

    #     # TODO find duplicate entries in pathway

    #     return merged_pathway
