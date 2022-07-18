""" Render object """

from typing import Any, Dict, List, Optional
from pydot import Dot, Node, Edge

from .models import Pathway, Entry
# from .resolver import Resolver
from .utils import ColorGradient


class Renderer:
    """
    Renderer for KEGG Pathway.
    """
    # pylint: disable=too-many-instance-attributes

    def __init__(
        self,
        kegg_pathway: Pathway,
        gene_dict: Dict[str, float],
        # resolver: Resolver
    ) -> None:
        """
        Init renderer for KEGG Pathway.
        :param kegg_pathway: Pathway
        :param resolver: Resolver instance.
        """

        # Pathway instance to render
        self.pathway: Pathway = kegg_pathway

        # Generate pydot Graph instance
        self.graph: Dot = Dot(
            'pathway',
            graph_type='graph',
            bgcolor='#ffffff',
            labelloc="t",
            label=self.pathway.title,
            fontsize=25,
        )

        # overlay vars
        self.overlay: Dict[str, float] = gene_dict


        # TODO: move to render function ??
        # Generate color map
        self.upper_color: tuple = (255, 0, 0)
        self.lower_color: tuple = (0, 0, 255)
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


        # TODO check if broken ?
        # self.exp_min = min(gene_dict.values())
        # self.exp_max = max(gene_dict.values())

        # # Clip log fold expression
        # self.exp_min = min(self.exp_min, 0)
        # self.exp_max = max(self.exp_max, 0)


        # TODO: get compounds without a resolver instance ? or remove organism from resolver
        # self.resolver: Resolver = resolver
        # TODO: self.components: Dict[str, str] = resolver.get_compounds()



    # TODO: fix because its broken
    # def _get_gene_color(self, gene_id: str) -> str:
    #     """
    #     Get overlay color
    #     :param gene_id: int
    #     :return: str
    #     """

    #     if gene_id not in self.overlay:
    #         return "#ffffff"

    #     if self.overlay[gene_id] < 0:
    #         return self.cmap_downreg[abs(int(self.overlay[gene_id] / self.exp_min * 100))]

    #     return self.cmap_upreg[abs(int(self.overlay[gene_id] / self.exp_max * 100))]



    def render(
        self,
        # with_overlay: bool = True,
    ) -> None:
        """
        Render KEGG pathway.
        """

        # add all nodes and edges

        related_entries = [int(p.entry1) for p in self.pathway.relations]
        related_entries.extend([int(p.entry2) for p in self.pathway.relations])

        for entry in self.pathway.entries:
            # only render genes with at least 1 relation
            if int(entry.id) in related_entries:
                # case select for types gene, comp, group, ...
                if entry.type == "gene":

                    # TODO: add node name
                    # if entry.graphics is not None:
                    #     entry_label = entry.graphics.name.split(", ")[0]

                    self.graph.add_node(Node(
                        name=entry.id,
                        label=entry.id,
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


                    # TODO: update table rendering with bgcolor attr (use XML element)
                    s_label = "".join([f"<tr><td>{l}</td></tr>" for l in labels])


                    self.graph.add_node(Node(
                        name=entry.id,
                        label=f"<<table border='0' cellborder='1'>{s_label}</table>>",
                        shape="rectangle",
                        style="filled",
                        color="#000000",
                        fillcolor="#ffffff",
                    ))

                elif entry.type == "compound":

                    entry_label: str = ""

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

            self.graph.add_edge(Edge(src=rel.entry1, dst=rel.entry2))

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
        """

        # Generate dot string from pydot graph object
        render_string: Any = self.graph.to_string()


        # Check correct type of dot string
        if not isinstance(render_string, str):
            raise TypeError("Object returned from pydot graph object is not a string.")

        return render_string



    def export(self, extension: str) -> bytes:
        """
        Export pydot graph to file
        :param extension: str
        :return: Any
        """

        # TODO: direct save to file object
        # TODO: check supported file formats

        # render with pydot to binary
        graph_data: Any = self.graph.create(prog="dot", format=extension)

        # Type check of return value
        if not isinstance(graph_data, bytes):
            raise TypeError("Failed to create binary file object from pydot graph instance.")

        return graph_data


    # def render_legend(self):
    #     """
    #     Render svg label
    #     :return: str
    #     """
    #     # Dont fix linting here, maybe this function will be removed
    #     # pylint: disable=line-too-long
    #     return f"""<?xml version="1.0" standalone="no"?>
    #                 <svg height="200" width="300" version="1.1" baseProfile="full" xmlns="http://www.w3.org/2000/svg"
    # xmlns:xlink="http://www.w3.org/1999/xlink" xmlns:ev="http://www.w3.org/2001/xml-events">
    #                 <defs>
    # <linearGradient id="cmap" x1="0%" y1="0%" x2="0%" y2="100%">
    #     <stop offset="0%" style="stop-color:{ColorGradient.to_css(color=self.upper_color)};stop-opacity:1" />
    #     <stop offset="50%" style="stop-color:rgb(255,255,255);stop-opacity:1" />
    #     <stop offset="100%" style="stop-color:{ColorGradient.to_css(color=self.lower_color)};stop-opacity:1" />
    # </linearGradient>
    #                 </defs>
    #                 <g>
    #                     <rect x="20" y="50" width="20" height="100" fill="url(#cmap)" />
    #                     <rect x="20" y="50" width="20" height="100"
    # style="stroke:black;stroke-width:2;fill-opacity:0;stroke-opacity:1" />
    #                     <text x="55" y="150" fill="black" alignment-baseline="central">{self.exp_min}</text>
    #                     <text x="55" y="100" fill="black" alignment-baseline="central">0</text>
    #                     <text x="55" y="50" fill="black" alignment-baseline="central">{self.exp_max}</text>

    #                     <line x1="40" y1="50" x2="50" y2="50" style="stroke:rgb(0,0,0);stroke-width:2" />
    #                     <line x1="40" y1="100" x2="50" y2="100" style="stroke:rgb(0,0,0);stroke-width:2" />
    #                     <line x1="40" y1="150" x2="50" y2="150" style="stroke:rgb(0,0,0);stroke-width:2" />
    #                 </g>
    #                 </svg>"""



