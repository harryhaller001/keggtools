""" Render pipeline """

import logging
import pydot
from .models import KEGGPathway
from .resolver import KEGGPathwayResolver
from .utils import ColorGradient
from typing import Any, Dict, Optional, List

class KEGGPathwayRenderer:
    """
    Renderer for KEGG Pathway
    """
    def __init__(self, kegg_pathway: KEGGPathway):
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

        self.components = KEGGPathwayResolver.get_components()

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

    def _get_gene_color(self, gene_id: int):
        if gene_id not in self.overlay:
            return "#ffffff"
        else:
            if self.overlay[gene_id] < 0:
                return self.cmap_downreg[abs(int(self.overlay[gene_id] / self.exp_min * 100))]
            else:
                return self.cmap_upreg[abs(int(self.overlay[gene_id] / self.exp_max * 100))]

    def group_render(self):
        stringBuilder = []
        stringBuilder.append("digraph pathway{CODE} {{".format(CODE=self.pathway.number))
        stringBuilder.append("\tnode [shape=rectangle arrowhead=normal];")
        stringBuilder.append("\tlabel=\"{TITLE}\";".format(TITLE=self.pathway.title))
        stringBuilder.append("\tfontsize=25;\n\tlabelloc=\"t\";")

        # search for "path:<...>"
        # TODO : divide entries in relation groups [[<entry>, ...], [...]]

        entry_groups = []
        genes_of_interest = []

        for rel in self.pathway.relations:
            if len(entry_groups) == 0:
                entry_groups.append([int(rel.entry1), int(rel.entry2)])
            else:
                conn = []
                for n in range(0, len(entry_groups)):
                    if int(rel.entry1) in entry_groups[n] or int(rel.entry2) in entry_groups[n]:
                        conn.append(n)
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

        for n in range(0, len(entry_groups)):
            stringBuilder.append("\tsubgraph cluster{N} {{".format(N=n))
            stringBuilder.append("\tlabel=\"\";\n\tcolor=blue;\n\tstyle=dashed;")

            for group_item in entry_groups[n]:
                for entry in self.pathway.entries:
                    # TODO : shape=oval for components --> get comp name
                    if int(entry.id) == group_item:
                        """stringBuilder.append("\tnode [label=\"{LABEL}\"]; entry{ID};"
                                             .format(LABEL=entry.graphics.name.split(", ")[0], ID=entry.id))"""
                        if entry.type == "gene":
                            # shape=rectangle, style=filled, fillcolor=\"#cccccc\"
                            stringBuilder.append("\tnode [label=\"{LABEL}\", shape=rectangle,"
                                                 " style=filled, fillcolor=\"#ffffff\"]; entry{ID};"
                                                 .format(LABEL=entry.graphics.name.split(", ")[0], ID=entry.id))
                        elif entry.type == "group":
                            # shape=rectangle, color="black" label=<<table border='0' cellborder='1'>
                            # <tr><td>comp 1</td></tr><tr><td>comp 2</td></tr></table>>];
                            labels = [self.pathway.get_entry_by_id(comp.id).graphics.name.split(", ")[0] for comp in
                                      entry.components]
                            s_label = ["<tr><td>{LABEL}</td></tr>".format(LABEL=l) for l in labels]
                            stringBuilder.append("\tnode [label=<<table border='0' cellborder='1'>{LABELS}</table>>,"
                                                 " shape=rectangle,"
                                                 " style=filled, color=black, fillcolor=\"#ffffff\"]; entry{ID};"
                                                 .format(LABELS="".join(s_label), ID=entry.id))
                        elif entry.type == "compound":
                            stringBuilder.append("\tnode [label=\"{LABEL}\", shape=oval,"
                                                 " style=filled, fillcolor=\"#ffffff\"]; entry{ID};"
                                                 .format(LABEL=entry.graphics.name.split(", ")[0], ID=entry.id))
                        genes_of_interest.append(entry.id)

            stringBuilder.append("\t}")

        for rel in self.pathway.relations:
            # TODO : adjust arrowhead
            if rel.entry1 in genes_of_interest and rel.entry2 in genes_of_interest:
                stringBuilder.append("\tentry{ID1} -> entry{ID2};".format(ID1=rel.entry1, ID2=rel.entry2))

        stringBuilder.append("}")
        self.render_string = "\n".join(stringBuilder)
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
        stringBuilder = []
        stringBuilder.append("digraph pathway{CODE} {{".format(CODE=self.pathway.number))
        stringBuilder.append("\tnode [shape=rectangle arrowhead=normal];")
        stringBuilder.append("\tlabel=\"{TITLE}\";".format(TITLE=self.pathway.title))
        stringBuilder.append("\tfontsize=25;\n\tlabelloc=\"t\";")

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
                    stringBuilder.append("\tnode [label=\"{LABEL}\", shape=rectangle,"
                                         " style=filled, fillcolor=\"#ffffff\"]; entry{ID};"
                                         .format(LABEL=entry.graphics.name.split(", ")[0], ID=entry.id))
                elif entry.type == "group":
                    # shape=rectangle, color="black" label=<<table border='0' cellborder='1'>
                    # <tr><td>comp 1</td></tr><tr><td>comp 2</td></tr></table>>];
                    labels = [self.pathway.get_entry_by_id(comp.id).graphics.name.split(", ")[0] for comp in entry.components]
                    s_label = ["<tr><td>{LABEL}</td></tr>".format(LABEL=l) for l in labels]
                    stringBuilder.append("\tnode [label=<<table border='0' cellborder='1'>{LABELS}</table>>,"
                                         " shape=rectangle,"
                                         " style=filled, color=black, fillcolor=\"#ffffff\"]; entry{ID};"
                                         .format(LABELS="".join(s_label), ID=entry.id))
                elif entry.type == "compound":
                    stringBuilder.append("\tnode [label=\"{LABEL}\", shape=oval,"
                                         " style=filled, fillcolor=\"#ffffff\"]; entry{ID};"
                                         .format(LABEL=entry.graphics.name.split(", ")[0], ID=entry.id))

        for rel in self.pathway.relations:
            # TODO : adjust arrowhead
            stringBuilder.append("\tentry{ID1} -> entry{ID2};".format(ID1=rel.entry1, ID2=rel.entry2))
        stringBuilder.append("}")

        self.render_string = "\n".join(stringBuilder)

        return self.render_string

    def raw_render(self):
        stringBuilder = []
        stringBuilder.append("digraph pathway{CODE} {{".format(CODE=self.pathway.number))

        stringBuilder.append("\tgraph [fontname = \"arial\"];\n\tnode [fontname = \"arial\"];")
        stringBuilder.append("\tedge [fontname = \"arial\"];")

        stringBuilder.append("\tnode [shape=rectangle arrowhead=normal];")
        stringBuilder.append("\tlabel=\"{TITLE}\";".format(TITLE=self.pathway.title))
        stringBuilder.append("\tfontsize=25;\n\tlabelloc=\"t\";")

        related_entries = [int(p.entry1) for p in self.pathway.relations]
        related_entries.extend([int(p.entry2) for p in self.pathway.relations])

        for entry in self.pathway.entries:
            # only render genes with at least 1 relation
            if int(entry.id) in related_entries:
                if entry.type == "gene":
                    stringBuilder.append("\tnode [label=\"{LABEL}\", shape=rectangle,"
                                         " style=filled, fillcolor=\"{COLOR}\"]; entry{ID};"
                                         .format(LABEL=entry.graphics.name.split(", ")[0], ID=entry.id,
                                                 COLOR=self._get_gene_color(entry.get_gene_id())))
                elif entry.type == "group":
                    labels = [self.pathway.get_entry_by_id(comp.id).graphics.name.split(", ")[0] for comp in
                              entry.components]
                    s_label = ["<tr><td>{LABEL}</td></tr>".format(LABEL=l) for l in labels]
                    stringBuilder.append("\tnode [label=<<table border='0' cellborder='1'>{LABELS}</table>>,"
                                         " shape=rectangle,"
                                         " style=filled, color=black, fillcolor=\"#ffffff\"]; entry{ID};"
                                         .format(LABELS="".join(s_label), ID=entry.id))
                elif entry.type == "compound":
                    name = entry.graphics.name.split(", ")[0]
                    if name in self.components:
                        name = self.components.get(name)
                    stringBuilder.append("\tnode [label=\"{LABEL}\", shape=oval,"
                                         " style=filled, fillcolor=\"#ffffff\"]; entry{ID};"
                                         .format(LABEL=name, ID=entry.id))

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

            stringBuilder.append("\tentry{ID1} -> entry{ID2} [arrowhead=\"{ARROW}\" label=\"{LABEL}\"];".format(ID1=rel.entry1, ID2=rel.entry2, ARROW=arrowhead, LABEL=label))

        stringBuilder.append("}")
        self.render_string = "\n".join(stringBuilder)
        return self.render_string

    def to_dot(self):
        return pydot.graph_from_dot_data(self.render_string)[0]

    def export(self, extension: str):
        # render with pydot to png|svg|pdf|
        if not self.render_string:
            self.render()
        return self.to_dot().create(format=extension)

    def render_legend(self):
        return """<?xml version="1.0" standalone="no"?>
                    <svg height="200" width="300" version="1.1" baseProfile="full" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns:ev="http://www.w3.org/2001/xml-events">
                    <defs>
                        <linearGradient id="cmap" x1="0%" y1="0%" x2="0%" y2="100%">
                            <stop offset="0%" style="stop-color:{COLOR_UP};stop-opacity:1" />
                            <stop offset="50%" style="stop-color:rgb(255,255,255);stop-opacity:1" />
                            <stop offset="100%" style="stop-color:{COLOR_DOWN};stop-opacity:1" />
                        </linearGradient>
                    </defs>
                    <g>
                        <rect x="20" y="50" width="20" height="100" fill="url(#cmap)" />
                        <rect x="20" y="50" width="20" height="100" style="stroke:black;stroke-width:2;fill-opacity:0;stroke-opacity:1" />
                        <text x="55" y="150" fill="black" alignment-baseline="central">{LOWER}</text>
                        <text x="55" y="100" fill="black" alignment-baseline="central">0</text>
                        <text x="55" y="50" fill="black" alignment-baseline="central">{UPPER}</text>

                        <line x1="40" y1="50" x2="50" y2="50" style="stroke:rgb(0,0,0);stroke-width:2" />
                        <line x1="40" y1="100" x2="50" y2="100" style="stroke:rgb(0,0,0);stroke-width:2" />
                        <line x1="40" y1="150" x2="50" y2="150" style="stroke:rgb(0,0,0);stroke-width:2" />
                    </g>
                    </svg>""".format(LOWER=self.exp_min, UPPER=self.exp_max,
                                     COLOR_UP=ColorGradient.to_css(color=self.upper_color),
                                     COLOR_DOWN=ColorGradient.to_css(color=self.lower_color))


if __name__ == "__main__":
    pathway = KEGGPathwayResolver(org="mmu").get_pathway("04659")

    renderer = KEGGPathwayRenderer(kegg_pathway=pathway)
    # print(renderer.group_render())
    # print(renderer.render())
    print(renderer.raw_render())


