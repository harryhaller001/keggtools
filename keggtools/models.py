"""KEGG pathway models to parse object relational."""

from pydantic_xml import BaseXmlModel, attr

from ._types import EntryTypeAlias, GraphicTypeAlias, ReactionTypeAlias, RelationSubtypeAlias, RelationTypeAlias


class Subtype(BaseXmlModel, tag="subtype"):
    """Subtype model class."""

    name: RelationSubtypeAlias = attr(name="name")
    value: str = attr(name="value")


class Relation(BaseXmlModel, tag="relation"):
    """Relation model class."""

    entry1: str = attr(name="entry1")
    entry2: str = attr(name="entry2")
    type: RelationTypeAlias = attr(name="type")
    subtypes: list[Subtype] = []


class Component(BaseXmlModel, tag="component"):
    """Component model."""

    id: str = attr(name="id")


class Graphics(BaseXmlModel, tag="graphics"):
    """Graphics information for rendering."""

    x: int | None = attr(name="x", default=None)
    y: int | None = attr(name="y", default=None)
    width: int | None = attr(name="width", default=None)
    height: int | None = attr(name="height", default=None)
    coords: str | None = attr(name="coords", default=None)
    name: str | None = attr(name="name", default=None)
    type: GraphicTypeAlias | None = attr(name="type", default=None)

    # TODO: check if valid hex color
    fgcolor: str | None = attr(name="fgcolor", default=None)
    bgcolor: str | None = attr(name="bgcolor", default=None)


class Entry(BaseXmlModel, tag="entry", search_mode="unordered"):
    """Entry model class."""

    id: str = attr(name="id")
    name: str = attr(name="name")
    type: EntryTypeAlias = attr(name="type")
    link: str | None = attr(name="link", default=None)
    reaction: str | None = attr(name="reaction", default=None)

    graphics: Graphics | None = None
    components: list[Component] = []

    def has_multiple_names(self) -> bool:
        """Checks if entry has multiple names that are space seperated.

        :return: Retruns True if entry has multiple names.
        :rtype: bool
        """
        return len(self.name.split(" ")) > 1

    def get_gene_id(self) -> list[str]:
        """Parse variable 'name' of Entry into KEGG id.

        :return: List of KEGG identifier.
        :rtype: list[str]
        """
        # TODO: validate return valid !!
        # r"^([a-z]){3}([0-9]){5}$"
        return [value.split(":")[1] for value in self.name.split(" ")]


class Alt(BaseXmlModel, tag="alt"):
    """Alt model."""

    name: str = attr(name="name")


class Product(BaseXmlModel, tag="product"):
    """Reaction Product model."""

    id: str = attr(name="id")
    name: str = attr(name="name")
    alt: Alt | None = None


class Substrate(BaseXmlModel, tag="substrate"):
    """reaction Substrate model."""

    id: str = attr(name="id")
    name: str = attr(name="name")
    alt: Alt | None = None


class Reaction(BaseXmlModel, tag="reaction", search_mode="unordered"):
    """Reaction model."""

    id: str = attr(name="id")
    name: str = attr(name="name")
    type: ReactionTypeAlias = attr(name="type")

    products: list[Product] = []
    substrates: list[Substrate] = []


class Pathway(BaseXmlModel, tag="pathway", search_mode="unordered"):
    """KEGG Pathway object.

    The KEGG pathway object stores graphics information and related objects.
    """

    name: str = attr(name="name")
    org: str = attr(name="org")
    number: str = attr(name="number")
    # TODO: check with is_valid_pathway_name, is_valid_pathway_org, is_valid_pathway_number
    title: str | None = attr(name="title", default=None)
    image: str | None = attr(name="image", default=None)
    link: str | None = attr(name="link", default=None)

    relations: list[Relation] = []
    entries: list[Entry] = []
    reactions: list[Reaction] = []

    def get_entry_by_id(self, entry_id: str) -> Entry | None:
        """Get pathway Entry object by id.

        :param str entry_id: Id of Entry.
        :return: Returns Entry instance if id is found in Pathway. Otherwise returns None.
        :rtype: typing.Optional[Entry]
        """
        for item in self.entries:
            if item.id == entry_id:
                return item
        return None

    def get_genes(self) -> list[str]:
        """List all genes from pathway.

        :return: List of entry ids with type gene.
        :rtype: typing.List[str]
        """
        result: list[str] = []

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
