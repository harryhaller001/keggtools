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
    ) -> str:
    """
    Generate HTML table in insert into label of dot node.

    `generate_embedded_html_table({"gene1": "#ffffff", "gene2": "#454545"})`

    :param List[Dict[str, str]] items: Items are dicts with have format `{name: hex_color}`.
    :param int border: Thickness of table border.
    :param int cellborder: Thickness of cell border within the table.
    :return: Returns html string of table.
    :rtype: str
    """

    # TODO: implement more suppored html attributes in table, tr and td elements

    element_table: Element = Element("table", attrib={"border": str(border), "cellborder": str(cellborder)})


    # TODO: implement multiple cols for longer lists (square format)
    for key, value in items.items():

        element_row: Element = SubElement(element_table, "tr")
        element_col: Element = SubElement(element_row, "td", attrib={"bgcolor": value})

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
        :param Optional[Dict[str, float]] gene_dict: Dict to specify overlay color gradient to rendered entries.
        :param Optional[Union[Storage, str]] cache: Specify cache to resolver compound data needed for rendering.
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
            splines="ortho", # "normal"
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
        self.resolver: Resolver = Resolver(organism=self.pathway.org, cache=cache)


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


                    # TODO: add node name
                    if entry.graphics is not None and entry.graphics.name is not None:
                        entry_label = entry.graphics.name.split(", ")[0]


                    # TODO Check if node has multiple names
                    # if len(entry.name.split(" ")) > 1:
                    #     entry_label += " - " + str(len(entry.name.split(" ")))
                    # TODO: generate list from entry name items
                    # TODO: resolve all names "\l".join()


                    self.graph.add_node(Node(
                        name=entry.id,
                        label=entry_label,
                        shape="rectangle",
                        style="filled",
                        color="#000000",
                        fillcolor="#ffffff",
                        # fillcolor="#ff00ff" if len(entry.name.split(" ")) > 1 else "#ffffff",
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
                        shape="rectangle", # plaintext
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


        for rel in self.pathway.relations:

            # TODO: add arrowhead and label

            self.graph.add_edge(Edge(
                src=rel.entry1,
                dst=rel.entry2,
                arrowhead="tee",
                label="+p",
            ))

            # label = ""
            # arrowhead = "normal"
            # if "inhibition" in rel.subtypes or "repression" in rel.subtypes:
            #     arrowhead = "tee"
            # elif "binding/association" in rel.subtypes:
            #     arrowhead = "none"

            # if "phosphorylation" in rel.subtypes:
            #     label = "+p"

            # string_builder.append(
            #     f"\tentry{rel.entry1} -> entry{rel.entry2} [arrowhead=\"{arrowhead}\" label=\"{label}\"];"
            # )




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
        Export pydot graph to file.

        :param str extension: Extension of file to export. Supported are "png", "svg", "pdf" and "jpeg".
        :return: File content are bytes object.
        :rtype: bytes
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
