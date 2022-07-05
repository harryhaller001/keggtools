""" Global constants """


# Example list for immune system pathways
# TODO: complete list of all pathways by groups

IMMUNE_SYSTEM_PATHWAYS = {
    "04640": "Hematopoietic cell lineage",
    "04610": "Complement and coagulation cascades",
    "04611": "Platelet activation",
    "04620": "Toll-like receptor signaling pathway",
    "04621": "NOD-like receptor signaling pathway",
    "04622": "RIG-I-like receptor signaling pathway",
    "04623": "Cytosolic DNA-sensing pathway",
    "04625": "C-type lectin receptor signaling pathway",
    "04650": "Natural killer cell mediated cytotoxicity",
    "04612": "Antigen processing and presentation",
    "04660": "T cell receptor signaling pathway",
    "04658": "Th1 and Th2 cell differentiation",
    "04659": "Th17 cell differentiation",
    "04657": "IL-17 signaling pathway",
    "04662": "B cell receptor signaling pathway",
    "04664": "Fc epsilon RI signaling pathway",
    "04666": "Fc gamma R-mediated phagocytosis",
    "04670": "Leukocyte transendothelial migration",
    "04672": "Intestinal immune network for IgA production",
    "04062": "Chemokine signaling pathway"
}


# Constant element types in the KGML format
# Details at KGML manual https://www.kegg.jp/kegg/xml/docs/

RELATION_SUBTYPES = {
    "activation": "-->",
    "inhibition": "--|",
    "expression": "-->",
    "repression": "--|",
    "indirect effect": "..>"
}


RELATION_TYPES = {
    "ECrel": "enzyme-enzyme relation",
    "PPrel": "protein-protein interaction",
    "GErel": "gene expression interaction",
    "PCrel": "protein-compound interaction",
    "maplink": "link to another map"
}

GRAPHICS_TYPE = [
    "rectangle",
    "circle",
    "roundrectangle",
    "line"
]

ENTRY_TYPE = [
    "ortholog",
    "enzyme",
    "reaction",
    "gene",
    "group",
    "compound",
    "map",
    "brite",
    "other"
]


