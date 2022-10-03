""" Render object """

# import logging
from typing import Any, Dict, List, Optional, Tuple, Union
from functools import lru_cache

# from enum import Enum, unique

from xml.etree.ElementTree import Element, SubElement
from xml.etree import ElementTree

from pydot import Dot, Node, Edge

from .storage import Storage
from .models import Pathway, Entry
from .resolver import (
    Resolver,
    # get_gene_names,
)
from .utils import ColorGradient


# TODO: add hex string to int tuple function
# TODO: add int tuple to hex string function


# Color variables
# TODO: implement all colors as tuple or Union[str, Tuple[int, int, int]]
# TODO: convert color from tuple to string on function level

# @unique
# class Color(Enum):
#     """
#     Color variables.
#     """
#     WHITE: Tuple[int, int, int] = (255, 255, 255)
#     BLACK: Tuple[int, int, int] = (0, 0, 0)


# TODO: use enum nested classes for different parameter options in pydot ???
# class PydotNode(Enum):
#     """
#     ...
#     """
#     class LineStyle(Enum):
#         """
#         ...
#         """
#         DASHED: str = ""


# Helper functions for renderer


def generate_embedded_html_table(
    items: Dict[str, str],
    border: int = 0,
    cellborder: int = 1,
    truncate: Optional[int] = None,
) -> str:
    """
    Generate HTML table in insert into label of dot node.

    `generate_embedded_html_table({"gene1": "#ffffff", "gene2": "#454545"})`

    :param typing.Dict[str, str] items: Items are dicts with have format `{name: hex_color}`.
    :param int border: Thickness of table border. (Default: 0)
    :param int cellborder: Thickness of cell border within the table. (Default: 1)
    :param typing.Optional[int] truncate: Maximal number of items in table. Set to None to disable trunaction. \
        (Default: None)
    :return: Returns html string of table.
    :rtype: str
    """

    # TODO: items input must be an ordered iterable!

    # TODO: implement more suppored html attributes in table, tr and td elements

    element_table: Element = Element(
        "table",
        attrib={
            "border": str(border),
            "cellborder": str(cellborder),
            "cellspacing": "0",
            "cellpadding": "4",
        },
    )

    # TODO: implement multiple cols for longer lists (square format)
    for index, (key, value) in enumerate(items.items()):

        element_row: Element = SubElement(element_table, "tr", attrib={})

        element_col: Element = SubElement(element_row, "td")

        if truncate is not None and index >= truncate:

            element_col.text = f"{len(items.items()) - truncate} more genes..."
            break

        element_col.attrib = {"bgcolor": value}

        # Set key as inner text of table cell
        element_col.text = key

    return ElementTree.tostring(element_table).decode("utf-8")


class Renderer:
    """
    Renderer for KEGG Pathway.
    """

    def __init__(
        self,
        kegg_pathway: Pathway,
        gene_dict: Optional[Dict[str, float]] = None,
        cache_or_resolver: Optional[Union[Storage, str, Resolver]] = None,
        # resolve_compounds: bool = True # TODO: Specify if renderer should resolver compounds in human readable text
        upper_color: Tuple[int, int, int] = (255, 0, 0),
        lower_color: Tuple[int, int, int] = (0, 0, 255),
    ) -> None:
        """
        Init Renderer instance for KEGG Pathway.

        :param Pathway kegg_pathway: Pathway instance to render.
        :param typing.Optional[typing.Dict[str, float]] gene_dict: Dict to specify overlay color \
            gradient to rendered entries.
        :param typing.Optional[typing.Union[Storage, str, cache_or_resolver]] cache: \
            Specify cache for resolver instance or pass resolver. Resolver is needed to get compound data needed for \
            rendering.
        :param typing.Tuple[int, int, int] upper_color: Color for upper bound of color gradient.
        :param typing.Tuple[int, int, int] lower_color: Color for lower bound of color gradient.
        """

        # pylint: disable=too-many-arguments

        # Pathway instance to render
        self.pathway: Pathway = kegg_pathway

        # Generate pydot Graph instance
        self.graph: Dot = Dot(
            "pathway",
            graph_type="digraph",
            bgcolor="#ffffff",
            labelloc="t",
            label=self.pathway.title,
            fontsize=25,
            rankdir="TB",
            splines="normal",  # "ortho"/line
            arrowhead="normal",
        )

        # overlay vars
        self.overlay: Dict[str, float] = {}

        if gene_dict is not None:
            self.overlay = gene_dict

        # TODO: move to render function ??
        # Generate color map
        self.upper_color: tuple = upper_color
        self.lower_color: tuple = lower_color

        # Init resolver instance from pathway org code.
        resolver_buffer: Optional[Resolver] = None

        if isinstance(cache_or_resolver, (str, Storage)) or cache_or_resolver is None:
            resolver_buffer = Resolver(cache=cache_or_resolver)
        elif isinstance(cache_or_resolver, Resolver):
            resolver_buffer = cache_or_resolver
        else:
            # Raise error of type is not correct
            raise TypeError(
                "String to directory, storage instance or resolver instance must be passed."
            )

        self.resolver: Resolver = resolver_buffer

    # implement color gradient as properties with lru_cache decorator
    @property
    def cmap_upreg(self) -> List[str]:
        """
        Generated color map as list of hexadecimal strings for upregulated genes in gene dict.
        """

        @lru_cache(maxsize=1)
        def cache_wrapper() -> List[str]:
            return ColorGradient(
                start=(255, 255, 255), stop=self.upper_color, steps=100
            ).get_list()

        return cache_wrapper()

    @property
    def cmap_downreg(self) -> List[str]:
        """
        Generated color map as list of hexadecimal strings for downregulated genes in gene dict.
        """

        @lru_cache(maxsize=1)
        def cache_wrapper() -> List[str]:
            return ColorGradient(
                start=(255, 255, 255), stop=self.lower_color, steps=100
            ).get_list()

        return cache_wrapper()

    def get_gene_color(
        self, gene_id: str, default_color: Tuple[int, int, int] = (255, 255, 255)
    ) -> str:
        """
        Get overlay color for given gene.

        :param str gene_id: Identify of gene.
        :param typing.Tuple[int, int, int] default_color: Default color to return if gene is not found in gene_dict. \
            Format in RGB tuple.
        :return: Color of gene by expression level specified in gene_dict.
        :rtype: str
        """

        # Return default color if gene is not found
        if self.overlay.get(gene_id) in (None, 0.0):
            return ColorGradient.to_hex(color=default_color)

        # Get expression limits
        exp_min: float = min(self.overlay.values())
        exp_max: float = max(self.overlay.values())

        if self.overlay[gene_id] < 0:
            # Expression below 0 (Downregulation)
            return self.cmap_downreg[abs(int(self.overlay[gene_id] / exp_min * 100))]

        # Expression above 0 (Upregulation)
        return self.cmap_upreg[abs(int(self.overlay[gene_id] / exp_max * 100))]

    # TODO: implement not here
    # def resolve_missing_gene_names(
    #     self,
    #     truncate_gene_list: Optional[int] = None,
    #     ) -> Dict[str, str]:
    #     """
    #     Resolve names of gene entries with only gene id given, but no human-readable names.
    #     This cases appears in entries with type gene with multiple, space-seperated gene id entries in the name
    #     attribute.

    #     :param typing.Optional[int] truncate_gene_list: With truncate entries with multiple space-seperated names \
    #         to given length. To keep all genes, set parameter to `None`.
    #     """

    #     # TODO: get list of genes with only kegg id and no label
    #     gene_names: List[str] = []

    #     # get all gene ids from entries with multiples names
    #     for entry in self.pathway.entries:
    #         if entry.type == "gene":
    #             name_parts: List[str] = entry.name.split(" ")
    #             if len(name_parts) > 1:

    #                 max_name_index: int = len(name_parts)

    #                 # Overwrite max index of list iteration, if truncation is set to integer below list length
    #                 if truncate_gene_list is not None and truncate_gene_list < max_name_index:
    #                     max_name_index = truncate_gene_list

    #                 for name_index in range(1, max_name_index):
    #                     if name_parts[name_index] not in gene_names:
    #                         gene_names.append(name_parts[name_index])

    #     # save in instance list of gene-id to gene name lookup dict
    #     # TODO: check if all genes got resolved

    #     loopup_dict: Dict[str, str] = {}

    #     # Split organism code from gene id
    #     for key, value in get_gene_names(genes=gene_names, max_genes=len(gene_names) + 1).items():
    #         loopup_dict[key.split(":")[1]] = value

    #     return loopup_dict

    def render(
        self,
        # resolve_unlabeled_genes: bool = True,
        display_unlabeled_genes: bool = True,
        # truncate_gene_list: Optional[int] = None,
    ) -> None:
        """
        Render KEGG pathway.


        :param bool display_unlabeled_genes: Entries in the KGML format can have space-seperated entry names. \
            Set this parameter to `False` to hide the entries.
        """

        # :param bool resolve_unlabeled_genes: If `True` the function will resolve all gene names for gene entries \
        #     which only have a gene id given.
        # :param typing.Optional[int] truncate_gene_list: With truncate entries with multiple space-seperated names \
        #     to given length. To keep all genes, set parameter to `None`.
        # """

        # pylint: disable=too-many-branches,too-many-locals,too-many-statements

        # resolved_gene_names: Dict[str, str] = {}
        # if resolve_unlabeled_genes is True:
        #     resolved_gene_names = self.resolve_missing_gene_names(truncate_gene_list=truncate_gene_list)

        # add all nodes and edges
        related_entries = [int(p.entry1) for p in self.pathway.relations]
        related_entries.extend([int(p.entry2) for p in self.pathway.relations])

        for entry in self.pathway.entries:

            # Use entry id as default label
            # TODO: use different default label as fallback
            entry_label: str = entry.id

            # only render genes with at least 1 relation
            if int(entry.id) in related_entries:
                # case select for types gene, comp, group, ...
                if entry.type == "gene":

                    # Get entry name by graphics element name attribute
                    if entry.graphics is not None and entry.graphics.name is not None:
                        entry_label = entry.graphics.name.split(", ")[0]

                    # Check if entry name contains multiple gene entries
                    # TODO: request the names of the entry names with .../find/gene1+gene2 ->
                    # parse list and use names as labels

                    if len(entry.get_gene_id()) > 1 and display_unlabeled_genes is True:
                        entry_gene_list: List[str] = entry.get_gene_id()

                        # Overwrite name of first item with graphics name
                        entry_gene_list[0] = entry_label

                        # TODO: resolve missing gene names by lookup dict
                        # Skip first entry
                        # for index in range(1, len(entry_gene_list)):
                        #     # Get item from lookup dict and fallback to gene id
                        #     # TODO: mark entry if gene id is used ??
                        #     entry_gene_list[index] = resolved_gene_names.get(
                        #         entry_gene_list[index], entry_gene_list[index]
                        #     )

                        # Add node
                        self.graph.add_node(
                            Node(
                                name=entry.id,
                                label="<"
                                + generate_embedded_html_table(
                                    items={
                                        gene_id: self.get_gene_color(gene_id)
                                        for gene_id in entry_gene_list
                                    }
                                )
                                + ">",
                                shape="plaintext",
                                style="filled",
                                color="#000000",
                                fillcolor="#ffffff",
                            )
                        )

                    else:

                        # Single node
                        self.graph.add_node(
                            Node(
                                name=entry.id,
                                label=entry_label,
                                shape="rectangle",
                                style="filled",
                                color="#000000",
                                fillcolor=self.get_gene_color(
                                    gene_id=entry.get_gene_id()[0]
                                ),
                            )
                        )

                elif entry.type == "group":

                    component_label: List[Tuple[str, str]] = []

                    # Iterate of components of group entry
                    for comp in entry.components:

                        component_entry: Optional[Entry] = self.pathway.get_entry_by_id(
                            comp.id
                        )

                        if (
                            component_entry is not None
                            and component_entry.graphics is not None
                            and component_entry.graphics.name is not None
                        ):

                            # Append tuple of gene id and color to labels
                            component_label.append(
                                (
                                    component_entry.graphics.name.split(", ")[0],
                                    self.get_gene_color(
                                        component_entry.get_gene_id()[0]
                                    ),
                                )
                            )

                    # Generate html table string from gene dict
                    # TODO: adjust cell spacing/padding, border

                    html_table_string: str = generate_embedded_html_table(
                        items=dict(component_label),
                    )

                    # Add dot node to graph
                    self.graph.add_node(
                        Node(
                            name=entry.id,
                            label=f"<{html_table_string}>",
                            # shape="rectangle",
                            shape="plaintext",
                            style="filled",
                            color="#000000",
                            fillcolor="#ffffff",
                        )
                    )

                elif entry.type == "compound":

                    # TODO: resolver compound with resolver

                    if entry.graphics is not None and entry.graphics.name is not None:
                        entry_label = entry.graphics.name.split(", ")[0]

                    # Add compound node to graph
                    self.graph.add_node(
                        Node(
                            name=entry.id,
                            label=entry_label,
                            shape="oval",
                            style="filled",
                            color="#000000",
                            fillcolor="#ffffff",
                        )
                    )

                elif entry.type == "reaction":

                    # TODO: implement reaction rendering

                    pass

                # TODO: add pathway map to dot graph
                # elif entry.type == "map":

                #     if entry.graphics is not None and entry.graphics.name is not None:
                #         entry_label = entry.graphics.name # .split(", ")[0]

                #     # Add map node to graph
                #     self.graph.add_node(Node(
                #         name=entry.id,
                #         label=entry_label,
                #         shape="rectangle",
                #         style="rounded,filled",
                #         color="#000000",
                #         fillcolor="#ffffff",
                #     ))

        for rel in self.pathway.relations:

            # Create edge instance from relation enties
            relation_edge: Edge = Edge(
                src=rel.entry1,
                dst=rel.entry2,
            )

            # default line style
            line_style: str = "solid"

            # Check for type of interaction and set line style of edge
            if rel.type == "GErel":
                # Gene expression interaction gets a distinct line style
                line_style = "dashed"

            elif rel.type == "PCrel":
                # Protein-compound interaction gets a distinct line style
                line_style = "dotted"

            # Add molecular events as edge labels
            molecular_event_dict: Dict[str, str] = {
                "phosphorylation": "+p",
                "dephosphorylation": "-p",
                "glycosylation": "+g",
                "ubiquitination": "+u",
                "methylation": "+m",
            }

            # Iterate over relation subtypes and check if moleuclar event is present
            edge_label: Optional[str] = None

            # Default arrowhead
            arrowhead: str = "none"

            for subtype in rel.subtypes:

                # Check if subtype is molecular event to set label of edge
                if subtype.name in molecular_event_dict:

                    # Check if label is none (no subtype found in prior iter steps)
                    if edge_label is None:
                        edge_label = molecular_event_dict[subtype.name]
                    else:
                        # TODO: is this event even possible ?
                        # TODO: handle but call warning
                        # A molecular event was already found. Append label to existing label
                        edge_label += ", " + molecular_event_dict[subtype.name]

                # Check for quality of interaction to set arrow head of edge
                if subtype.name in (
                    "activation",
                    "expression",
                    "indirect effect",
                    "binding/association",
                ):
                    arrowhead = "normal"

                elif subtype.name in ("inhibition", "repression", "dissociation"):
                    arrowhead = "tee"

                elif subtype.name == "state change":
                    arrowhead = "diamond"

            # set arrowhead to edge instance
            relation_edge.set(name="arrowhead", value=arrowhead)

            # Set label if molecular event is found in relation subtypes
            if edge_label is not None:
                relation_edge.set(name="label", value=edge_label)

            # Set line style to edge instance
            relation_edge.set(name="style", value=line_style)

            # Add edge to graph
            self.graph.add_edge(relation_edge)

    def to_string(self) -> str:
        """
        pydot graph instance to dot string.

        :return: Generated dot string of pathway.
        :rtype: str
        """

        # Generate dot string from pydot graph object
        render_string: Any = self.graph.to_string()

        # Check correct type of dot string
        if not isinstance(render_string, str):
            raise TypeError("Object returned from pydot graph object is not a string.")

        return render_string

    def to_binary(self, extension: str) -> bytes:
        """
        Export pydot graph to binary data.

        :param str extension: Extension of file to export. Use format string like "png", "svg", "pdf" or "jpeg".
        :return: File content are bytes object.
        :rtype: bytes
        :raises TypeError: If variable with generated dot graph is not type bytes.
        """

        # render with pydot to binary
        graph_data: Any = self.graph.create(prog="dot", format=extension)

        # Type check of return value
        if not isinstance(graph_data, bytes):
            raise TypeError(
                "Failed to create binary file object from pydot graph instance."
            )

        return graph_data

    def to_file(self, filename: str, extension: str) -> None:
        """
        Export pydot graph to file.

        :param str filename: Filename to save file at.
        :param str extension: Extension of file to export. Use format string like "png", "svg", "pdf" or "jpeg".
        """

        # TODO: get export format from filename

        # Get binary data from graph object
        binary_data: bytes = self.to_binary(extension=extension)

        # Save binary data to file object
        with open(filename, mode="wb") as file_obj:
            file_obj.write(binary_data)
