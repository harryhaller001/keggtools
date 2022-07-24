""" Render object """

from typing import Any, Dict, List, Optional, Union

from xml.etree.ElementTree import Element, SubElement
from xml.etree import ElementTree

from pydot import Dot, Node, Edge

from .storage import Storage
from .models import Pathway, Entry
from .resolver import Resolver
from .utils import ColorGradient



def generate_embedded_html_table(
    items: Dict[str, str],
    border: int = 0,
    cellborder: int = 1,
    truncate: Optional[int] = 5
    ) -> str:
    """
    Generate HTML table in insert into label of dot node.

    `generate_embedded_html_table({"gene1": "#ffffff", "gene2": "#454545"})`

    :param typing.Dict[str, str] items: Items are dicts with have format `{name: hex_color}`.
    :param int border: Thickness of table border.
    :param int cellborder: Thickness of cell border within the table.
    :param int truncate: Maximal number of items in table. Set to None to disable trunaction.
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
        cache: Optional[Union[Storage, str]] = None,
        # resolve_compounds: bool = True # TODO: Specify if renderer should resolver compounds in human readable text

        upper_color: tuple = (255, 0, 0),
        lower_color: tuple = (0, 0, 255),
    ) -> None:
        """
        Init Renderer instance for KEGG Pathway.

        :param Pathway kegg_pathway: Pathway instance to render.
        :param typing.Optional[typing.Dict[str, float]] gene_dict: Dict to specify overlay color \
            gradient to rendered entries.
        :param typing.Optional[typing.Union[Storage, str]] cache: Specify cache to resolver compound \
            data needed for rendering.
        :param tuple upper_color: Color for upper bound of color gradient.
        :param tuple lower_color: Color for lower bound of color gradient.
        """

        # Pathway instance to render
        self.pathway: Pathway = kegg_pathway

        # Generate pydot Graph instance
        self.graph: Dot = Dot(
            'pathway',
            graph_type='digraph',
            bgcolor='#ffffff',
            labelloc="t",
            label=self.pathway.title,
            fontsize=25,
            rankdir="TB",
            splines="normal", # "ortho"/line
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

        self.cmap_upreg: List[str] = ColorGradient(
            start=(255, 255, 255),
            stop=self.upper_color,
            steps=100
        ).get_list()
        self.cmap_downreg: List[str] = ColorGradient(
            start=(255, 255, 255),
            stop=self.lower_color,
            steps=100
        ).get_list()


        # Init resolver instance from pathway org code.
        self.resolver: Resolver = Resolver(cache=cache)


    # TODO: fix because its broken
    def get_gene_color(self, gene_id: str, default_color: tuple = (255, 255, 255)) -> str:
        """
        Get overlay color for given gene.

        :param str gene_id: Identify of gene.
        :param tuple default_color: Default color to return if gene is not found in gene_dict. Format in RGB tuple.
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



    def render(
        self,
    ) -> None:
        """
        Render KEGG pathway.
        """

        # pylint: disable=too-many-branches,too-many-locals,too-many-statements


        # TODO: find all entries with multiple names (space-seperates)
        # TODO: request the names of the entry names with .../find/gene1+gene2 -> parse list and use names as labels

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
                    if len(entry.name.split(" ")) > 1:
                        entry_gene_list: List[str] = entry.name.split(" ")

                        # Overwrite name of first item with graphics name
                        entry_gene_list[0] = entry_label

                        # Overwrite label with html table
                        entry_label = "<" + generate_embedded_html_table(
                            items=dict(zip(entry_gene_list, ["#ffffff"] * len(entry_gene_list)))
                        ) + ">"


                    self.graph.add_node(Node(
                        name=entry.id,
                        label=entry_label,
                        shape="rectangle",
                        style="filled",
                        color="#000000",
                        fillcolor="#ffffff",
                    ))



                elif entry.type == "group":

                    labels: List[str] = []

                    for comp in entry.components:
                        component_entry: Optional[Entry] = self.pathway.get_entry_by_id(comp.id)

                        if component_entry is not None and \
                            component_entry.graphics is not None and \
                            component_entry.graphics.name is not None:

                            # Append to labels
                            labels.append(component_entry.graphics.name.split(", ")[0])


                    # Generate html table string from gene dict
                    # TODO: add cell spacing/padding
                    html_table_string: str = generate_embedded_html_table(
                        items=dict(zip(labels, ["#ffffff"] * len(labels))),
                    )

                    # Add dot node to graph
                    self.graph.add_node(Node(
                        name=entry.id,
                        label=f"<{html_table_string}>",
                        shape="plaintext",
                        style="filled",
                        color="#000000",
                        fillcolor="#ffffff",
                    ))


                elif entry.type == "compound":

                    # TODO: resolver compound with resolver


                    if entry.graphics is not None and entry.graphics.name is not None:
                        entry_label = entry.graphics.name.split(", ")[0]

                    self.graph.add_node(Node(
                        name=entry.id,
                        label=entry_label,
                        shape="oval",
                        style="filled",
                        color="#000000",
                        fillcolor="#ffffff",
                    ))


                elif entry.type == "reaction":

                    # TODO: implement reaction rendering

                    pass


        for rel in self.pathway.relations:


            relation_edge: Edge = Edge(
                src=rel.entry1,
                dst=rel.entry2,
            )

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
            arrowhead: str = "normal"

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
                if subtype.name in ("activation", "expression", "indirect effect", "binding/association"):
                    arrowhead = "normal"
                elif subtype.name in ("inhibition", "repression", "dissociation"):
                    arrowhead = "tee"

                if subtype.name == "state change":
                    arrowhead = "diamond"

                else:
                    arrowhead = "none"



            # set arrowhead to edge instance
            relation_edge.set(name="arrowhead", value=arrowhead)


            # Set label if molecular event is found in relation subtypes
            if edge_label is not None:
                relation_edge.set(name="label", value=edge_label)

            # Set line style to edge instance
            relation_edge.set(name="style", value=line_style)


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
        if not isinstance(render_string, str): # pragma: no cover
            raise TypeError("Object returned from pydot graph object is not a string.")

        return render_string



    def to_binary(self, extension: str) -> bytes:
        """
        Export pydot graph to binary data.

        :param str extension: Extension of file to export. Supported are "png", "svg", "pdf" and "jpeg".
        :return: File content are bytes object.
        :rtype: bytes
        :raises TypeError: If variable with generated dot graph is not type bytes.
        """

        # TODO: check supported file formats
        # if extension not in ("png", "svg", "pdf", "jpeg"):
        #     raise ValueError("Supported are only extensions 'png', 'svg', 'pdf' and 'jpeg'.")

        # TODO: direct save to file object

        # render with pydot to binary
        graph_data: Any = self.graph.create(prog="dot", format=extension)

        # Type check of return value
        if not isinstance(graph_data, bytes): # pragma: no cover
            raise TypeError("Failed to create binary file object from pydot graph instance.")

        return graph_data


    def to_file(self, filename: str, extension: str) -> None:
        """
        Export pydot graph to file.

        :param str filename: Filename to save file at.
        :param str extension: Extension of file to export. Supported are "png", "svg", "pdf" and "jpeg".
        """

        # TODO: get export format from filename

        # Get binary data from graph object
        binary_data: bytes = self.to_binary(extension=extension)

        # Save binary data to file object
        with open(filename, mode="wb") as file_obj:
            file_obj.write(binary_data)
