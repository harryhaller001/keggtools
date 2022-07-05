""" Render pipeline """
# pylint: disable=line-too-long

# import logging
from typing import Any, Dict, List
import pydot
from .models import Pathway
from .resolver import Resolver
from .utils import ColorGradient


class Renderer:
    """
    Renderer for KEGG Pathway
    """
    # pylint: disable=too-many-instance-attributes

    def __init__(self, kegg_pathway: Pathway):
        """
        Init renderer for KEGG Pathway
        :param kegg_pathway: KEGGPathway
        """

        self.pathway = kegg_pathway
        self.overlay: Dict[int, Any] = {}
        self.exp_min = 0
        self.exp_max = 0
        self.render_string = None

        # TODO: fix any typing
        self.cmap_upreg: List[Any] = []
        self.cmap_downreg: List[Any] = []

        self.upper_color = (255, 0, 0)
        self.lower_color = (0, 0, 255)

        self.components = Resolver.get_components()


    def set_overlay(self, gene_dict: dict):
        """
        Overlay dot rendering with differential expression data. {<gene-id>: <fold-exp>}
        :param gene_dict: dict
        :return:
        """
        self.cmap_downreg = ColorGradient(start=(255, 255, 255), stop=self.lower_color, steps=100).get_list()
        self.cmap_upreg = ColorGradient(start=(255, 255, 255), stop=self.upper_color, steps=100).get_list()
        self.overlay = gene_dict
        self.exp_min = min(gene_dict.values())
        self.exp_max = max(gene_dict.values())

        # Clip log fold expression
        # if self.exp_min > 0:
        #     self.exp_min = 0
        # if self.exp_max < 0:
        #     self.exp_max = 0
        self.exp_min = min(self.exp_min, 0)
        self.exp_max = max(self.exp_max, 0)


    def _get_gene_color(self, gene_id: int):
        """
        Get overlay color
        :param gene_id: int
        :return: str
        """

        if gene_id not in self.overlay:
            return "#ffffff"

        if self.overlay[gene_id] < 0:
            return self.cmap_downreg[abs(int(self.overlay[gene_id] / self.exp_min * 100))]

        return self.cmap_upreg[abs(int(self.overlay[gene_id] / self.exp_max * 100))]


    def group_render(self):
        """
        Group render
        :return: str
        """

        # TODO: fix rendering
        # pylint: disable=too-many-branches

        string_builder = []
        string_builder.append(f"digraph pathway{self.pathway.number} {{")
        string_builder.append("\tnode [shape=rectangle arrowhead=normal];")
        string_builder.append(f"\tlabel=\"{self.pathway.title}\";")
        string_builder.append("\tfontsize=25;\n\tlabelloc=\"t\";")

        # search for "path:<...>"
        # TODO : divide entries in relation groups [[<entry>, ...], [...]]

        entry_groups = []
        genes_of_interest = []

        for rel in self.pathway.relations:
            if len(entry_groups) == 0:
                entry_groups.append([int(rel.entry1), int(rel.entry2)])
            else:
                conn = []
                # for n in range(0, len(entry_groups)):
                #     if int(rel.entry1) in entry_groups[n] or int(rel.entry2) in entry_groups[n]:
                #         conn.append(n)

                for entry_index, entry_item in enumerate(entry_groups):
                    if int(rel.entry1) in entry_item or int(rel.entry2) in entry_item:
                        conn.append(entry_index)

                if len(conn) == 0:
                    entry_groups.append([int(rel.entry1), int(rel.entry2)])
                elif len(conn) == 1:
                    entry_groups[conn[0]].extend([int(rel.entry1), int(rel.entry2)])
                else:
                    # more then 1 match -> merge groups
                    entry_groups[conn[0]].extend(entry_groups[conn[1]])
                    del entry_groups[conn[1]]
                    entry_groups[conn[0]].extend([int(rel.entry1), int(rel.entry2)])
        # print(entry_groups)

        # TODO : entry group in cluster (subgraph) --> annotate cluster with pathway

        # for n in range(0, len(entry_groups)):
        for entry_index, entry_item in enumerate(entry_groups):
            string_builder.append(f"\tsubgraph cluster{entry_index} {{")
            string_builder.append("\tlabel=\"\";\n\tcolor=blue;\n\tstyle=dashed;")

            for group_item in entry_item:
                for entry in self.pathway.entries:
                    # TODO : shape=oval for components --> get comp name
                    if int(entry.id) == group_item:
                        # stringBuilder.append("\tnode [label=\"{LABEL}\"]; entry{ID};"
                        #                      .format(LABEL=entry.graphics.name.split(", ")[0], ID=entry.id))
                        if entry.type == "gene":
                            # shape=rectangle, style=filled, fillcolor=\"#cccccc\"
                            entry_label = entry.graphics.name.split(", ")[0]
                            string_builder.append(f"\tnode [label=\"{entry_label}\", shape=rectangle,"
                                                  f" style=filled, fillcolor=\"#ffffff\"]; entry{entry.id};")

                        elif entry.type == "group":
                            # shape=rectangle, color="black" label=<<table border='0' cellborder='1'>
                            # <tr><td>comp 1</td></tr><tr><td>comp 2</td></tr></table>>];
                            labels = [self.pathway.get_entry_by_id(comp.id).graphics.name.split(", ")[0] for comp in
                                      entry.components]
                            s_label = "".join([f"<tr><td>{l}</td></tr>" for l in labels])
                            string_builder.append(f"\tnode [label=<<table border='0' cellborder='1'>{s_label}</table>>,"
                                                  " shape=rectangle,"
                                                  f" style=filled, color=black, fillcolor=\"#ffffff\"]; entry{entry.id};")

                        elif entry.type == "compound":

                            entry_label = entry.graphics.name.split(", ")[0]
                            string_builder.append(f"\tnode [label=\"{entry_label}\", shape=oval,"
                                                  f" style=filled, fillcolor=\"#ffffff\"]; entry{entry.id};")
                        genes_of_interest.append(entry.id)

            string_builder.append("\t}")

        for rel in self.pathway.relations:
            # TODO : adjust arrowhead
            if rel.entry1 in genes_of_interest and rel.entry2 in genes_of_interest:
                string_builder.append(f"\tentry{rel.entry1} -> entry{rel.entry2};")

        string_builder.append("}")
        self.render_string = "\n".join(string_builder)
        return self.render_string


    def render(self):
        """
        digraph G {
            labelloc="t";
            label="Inflammatory bowel disease (IBD)";
            fontsize=25;
            node [shape=rectangle arrowhead=normal];
            node [label="Tlr2"]; entry1;
            node [label="Nfkb1"]; entry2;
            node [label="Nod2"]; entry3;
            entry1 -> entry2;
            entry1 -> entry3 [arrowhead="tee"];
        }
        """
        string_builder = []
        string_builder.append(f"digraph pathway{self.pathway.number} {{")
        string_builder.append("\tnode [shape=rectangle arrowhead=normal];")
        string_builder.append(f"\tlabel=\"{self.pathway.title}\";")
        string_builder.append("\tfontsize=25;\n\tlabelloc=\"t\";")

        # TODO : specifiy for each node: shape=circle|rectangle|oval|ellipse, style=filled, fillcolor=red|green|#cccccc

        # search for "path:<...>"

        # TODO : parse entry::type[group]

        related_entries = [int(p.entry1) for p in self.pathway.relations]
        related_entries.extend([int(p.entry2) for p in self.pathway.relations])

        for entry in self.pathway.entries:
            # only render genes with at least 1 relation
            if int(entry.id) in related_entries:  # and entry.type == "gene"
                # case select for types gene, comp, group, ...
                if entry.type == "gene":
                    # shape=rectangle, style=filled, fillcolor=\"#cccccc\"
                    entry_label = entry.graphics.name.split(", ")[0]
                    string_builder.append(f"\tnode [label=\"{entry_label}\", shape=rectangle,"
                                          f" style=filled, fillcolor=\"#ffffff\"]; entry{entry.id};")

                elif entry.type == "group":
                    # shape=rectangle, color="black" label=<<table border='0' cellborder='1'>
                    # <tr><td>comp 1</td></tr><tr><td>comp 2</td></tr></table>>];
                    labels = [self.pathway.get_entry_by_id(comp.id).graphics.name.split(", ")[0] for comp in entry.components]
                    s_label = "".join([f"<tr><td>{l}</td></tr>" for l in labels])
                    string_builder.append(f"\tnode [label=<<table border='0' cellborder='1'>{s_label}</table>>,"
                                          " shape=rectangle,"
                                          f" style=filled, color=black, fillcolor=\"#ffffff\"]; entry{entry.id};")

                elif entry.type == "compound":

                    entry_label = entry.graphics.name.split(", ")[0]
                    string_builder.append(f"\tnode [label=\"{entry_label}\", shape=oval,"
                                          f" style=filled, fillcolor=\"#ffffff\"]; entry{entry.id};")

        for rel in self.pathway.relations:
            # TODO : adjust arrowhead
            string_builder.append(f"\tentry{rel.entry1} -> entry{rel.entry2};")
        string_builder.append("}")

        self.render_string = "\n".join(string_builder)

        return self.render_string


    def raw_render(self):
        """
        Render pydot graph
        :return: str
        """

        string_builder = []
        string_builder.append(f"digraph pathway{self.pathway.number} {{")

        string_builder.append("\tgraph [fontname = \"arial\"];\n\tnode [fontname = \"arial\"];")
        string_builder.append("\tedge [fontname = \"arial\"];")

        string_builder.append("\tnode [shape=rectangle arrowhead=normal];")
        string_builder.append(f"\tlabel=\"{self.pathway.title}\";")
        string_builder.append("\tfontsize=25;\n\tlabelloc=\"t\";")

        related_entries = [int(p.entry1) for p in self.pathway.relations]
        related_entries.extend([int(p.entry2) for p in self.pathway.relations])

        for entry in self.pathway.entries:
            # only render genes with at least 1 relation
            if int(entry.id) in related_entries:
                if entry.type == "gene":

                    entry_label = entry.graphics.name.split(", ")[0]
                    string_builder.append(f"\tnode [label=\"{entry_label}\", shape=rectangle,"
                                          f" style=filled, fillcolor=\"{self._get_gene_color(entry.get_gene_id())}\"]; entry{entry.id};")

                elif entry.type == "group":
                    labels = [self.pathway.get_entry_by_id(comp.id).graphics.name.split(", ")[0] for comp in
                              entry.components]
                    s_label = "".join([f"<tr><td>{l}</td></tr>" for l in labels])
                    string_builder.append(f"\tnode [label=<<table border='0' cellborder='1'>{s_label}</table>>,"
                                          " shape=rectangle,"
                                          f" style=filled, color=black, fillcolor=\"#ffffff\"]; entry{entry.id};")
                elif entry.type == "compound":
                    name = entry.graphics.name.split(", ")[0]
                    if name in self.components:
                        name = self.components.get(name)
                    string_builder.append(f"\tnode [label=\"{name}\", shape=oval,"
                                          f" style=filled, fillcolor=\"#ffffff\"]; entry{entry.id};")

        for rel in self.pathway.relations:
            # adjust arrowhead
            label = ""
            arrowhead = "normal"
            if "inhibition" in rel.subtypes or "repression" in rel.subtypes:
                arrowhead = "tee"
            elif "binding/association" in rel.subtypes:
                arrowhead = "none"

            if "phosphorylation" in rel.subtypes:
                label = "+p"

            string_builder.append(f"\tentry{rel.entry1} -> entry{rel.entry2} [arrowhead=\"{arrowhead}\" label=\"{label}\"];")

        string_builder.append("}")
        self.render_string = "\n".join(string_builder)
        return self.render_string


    def to_dot(self):
        """
        Convert rendered string to pydot graph
        :return: pydot.Graph
        """
        return pydot.graph_from_dot_data(self.render_string)[0]


    def export(self, extension: str):
        """
        Export pydot graph
        :param extension: str
        :return: Any
        """
        # render with pydot to png|svg|pdf|
        if not self.render_string:
            self.render()
        return self.to_dot().create(format=extension)


    def render_legend(self):
        """
        Render svg label
        :return: str
        """
        # Dont fix linting here, maybe this function will be removed
        # pylint: disable=line-too-long
        return f"""<?xml version="1.0" standalone="no"?>
                    <svg height="200" width="300" version="1.1" baseProfile="full" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns:ev="http://www.w3.org/2001/xml-events">
                    <defs>
                        <linearGradient id="cmap" x1="0%" y1="0%" x2="0%" y2="100%">
                            <stop offset="0%" style="stop-color:{ColorGradient.to_css(color=self.upper_color)};stop-opacity:1" />
                            <stop offset="50%" style="stop-color:rgb(255,255,255);stop-opacity:1" />
                            <stop offset="100%" style="stop-color:{ColorGradient.to_css(color=self.lower_color)};stop-opacity:1" />
                        </linearGradient>
                    </defs>
                    <g>
                        <rect x="20" y="50" width="20" height="100" fill="url(#cmap)" />
                        <rect x="20" y="50" width="20" height="100" style="stroke:black;stroke-width:2;fill-opacity:0;stroke-opacity:1" />
                        <text x="55" y="150" fill="black" alignment-baseline="central">{self.exp_min}</text>
                        <text x="55" y="100" fill="black" alignment-baseline="central">0</text>
                        <text x="55" y="50" fill="black" alignment-baseline="central">{self.exp_max}</text>

                        <line x1="40" y1="50" x2="50" y2="50" style="stroke:rgb(0,0,0);stroke-width:2" />
                        <line x1="40" y1="100" x2="50" y2="100" style="stroke:rgb(0,0,0);stroke-width:2" />
                        <line x1="40" y1="150" x2="50" y2="150" style="stroke:rgb(0,0,0);stroke-width:2" />
                    </g>
                    </svg>"""



