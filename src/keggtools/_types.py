from typing import Literal, TypeAlias

RelationSubtypeAlias: TypeAlias = Literal[
    "compound",
    "hidden compound",
    "activation",
    "inhibition",
    "expression",
    "repression",
    "indirect effect",
    "state change",
    "binding/association",
    "dissociation",
    "missing interaction",
    "phosphorylation",
    "dephosphorylation",
    "glycosylation",
    "ubiquitination",
    "methylation",
]

RelationTypeAlias: TypeAlias = Literal[
    "ECrel",
    "PPrel",
    "GErel",
    "PCrel",
    "maplink",
]

GraphicTypeAlias: TypeAlias = Literal["rectangle", "circle", "roundrectangle", "line"]

EntryTypeAlias: TypeAlias = Literal[
    "ortholog",
    "enzyme",
    "reaction",
    "gene",
    "group",
    "compound",
    "map",
    "brite",
    "other",
]


ReactionTypeAlias: TypeAlias = Literal[
    "reversible",
    "irreversible",
]
