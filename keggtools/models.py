""" KEGG pathway models to parse object relational """

import logging
from xml.etree import ElementTree as ElementTree
from xml.etree.ElementTree import Element, SubElement
from typing import Type, Union
import pydot


class Relation:
    """

    """
    def __init__(self):
        # REQUIRED
        self.entry1 = None
        self.entry2 = None
        self.type = None

        self.subtypes = {}

    @staticmethod
    def parse(item: Element):
        """
        Parse xml ElementTree into KEGG Relation
        :param item: ElementTree
        :return: Relation
        """
        relation = Relation()
        relation.entry1 = item.attrib["entry1"]
        relation.entry2 = item.attrib["entry2"]
        relation.type = item.attrib["type"]

        for child in item:
            if child.tag == "subtype":
                relation.subtypes[child.attrib["name"]] = child.attrib["value"]

        return relation

    def __str__(self):
        return "<Relation {ENTRY1}->{ENTRY2} type='{TYPE}'".format(ENTRY1=self.entry1, ENTRY2=self.entry2,
                                                                   TYPE=self.type)


class Component:
    """
    The component element is a subelement of the entry element, and is used when the entry element is a complex node;
    namely, when the type attribute value of the entry element is "group". The nodes that constitute the complex are
    specified by recurrent calls. For example, when the complex is composed of two nodes, two component elements are
    specified. The attribute of this element is as follows.
    """
    def __init__(self):
        self.id = ""

    @staticmethod
    def parse(item: Element):
        """
        Parsing ElementTree into Component
        :param item: ElementTree
        :return: Component
        """
        c = Component()
        c.id = item.attrib["id"]
        return c


class Graphics:
    """
    Graphics information for rendering
    """
    def __init__(self):
        self.attrib = {"x": 0,
                       "y": 0,
                       "width": 0,
                       "height": 0,
                       "name": "",
                       "type": "",
                       "fgcolor": "",
                       "bgcolor": ""}

    def __str__(self):
        return "<Graphics {STR}".format(STR=" ".join(["%s='%s'" % (key, val) for key, val in self.attrib.items()]))

    def __getattr__(self, item):
        return self.attrib[item]

    @staticmethod
    def parse(item: Element):
        """
        Parse xml ElementTree into KEGG Graphics
        :param item: ElementTree
        :return: Graphics
        """
        g = Graphics()
        for key, val in item.attrib.items():
            if key in g.attrib:
                g.attrib[key] = val
        return g


class Entry:
    """
    KEGG Entry
    """
    def __init__(self):
        # REQUIRED
        self.id = ""
        self.name = ""
        self.type = ""

        # IMPLIED
        self.link = ""
        self.reaction = ""
        self.graphics = None
        self.components = []

    def get_gene_id(self):
        """
        Parse variable 'name' into KEGG ID
        :return: int
        """
        return int(self.name.split(":")[1])

    def get_id(self):
        """
        Parse variable 'name' into KEGG ID
        :return: int
        """
        # TODO : remove
        return int(self.name.split(":")[1])

    @staticmethod
    def parse(item: Element):
        """
        Parsing xml ElementTree into KEGG Entry
        :param item: ElementTree
        :return: Entry
        """
        entry = Entry()
        entry.id = item.attrib["id"]
        entry.name = item.attrib["name"].split(" ")[0]
        entry.type = item.attrib["type"]

        entry.link = item.attrib.get("link", "")
        entry.reaction = item.attrib.get("reaction", "")

        for child in item:
            if child.tag == "graphics":
                entry.graphics = Graphics.parse(child)
            elif child.tag == "component":
                entry.components.append(Component.parse(child))

        return entry

    def __str__(self):
        return "<Entry id={ID} name='{NAME}' type='{TYPE}'>".format(ID=self.id, NAME=self.name, TYPE=self.type)


class KEGGPathway:
    """
    KEGG Pathway
    """
    def __init__(self):
        # REQUIRED
        self.name = ""
        self.org = ""
        self.number = ""

        # IMPLIED
        self.title = ""
        self.image = ""
        self.link = ""

        # Children
        self.relations = []
        self.entries = []
        self.reactions = []

    def get_entry_by_id(self, entry_id: Union[str, int]):
        for item in self.entries:
            if int(item.id) == int(entry_id):
                return item
        return None

    def matches(self, gene_id_list: list):
        """
        Return percent value for matching genes. [int(<gene_id>), ...]
        :param gene_id_list: list
        :return: float
        """
        # run over entry:gene_id -> return count / len(entry)

        count = 0
        for entry in self.entries:
            if entry in gene_id_list:
                count += 1
        return count / len(self.entries)

    def get_genes(self):
        """
        List all genes from pathway {<gene_id>: <gene_name>}
        :return: dict
        """
        result = {}
        for entry in self.entries:
            if entry.type == "gene":
                result[entry.get_id()] = entry.graphics.name
        logging.debug("Get {N} unique genes from pathway".format(N=len(result.keys())))
        return result

    def __str__(self):
        return "<KEGGPathway path:{ORG}{CODE} title='{TITLE}'>".format(ORG=self.org, CODE=self.number, TITLE=self.title)

    def summarize(self):
        """
        Verbose all components of pathway
        :return: None
        """
        print(self.__str__())
        for r in self.relations:
            print(r)
        for e in self.entries:
            print(e)

    @staticmethod
    def parse(data: str):
        """
        Parsing xml String in KEGG Pathway
        :param data: str
        :return: KEGGPathway
        """
        pathw = KEGGPathway()

        root = ElementTree.fromstring(data)

        pathw.name = root.attrib["name"]
        pathw.org = root.attrib["org"]
        pathw.number = root.attrib["number"]

        pathw.title = root.attrib.get("title", "")
        pathw.image = root.attrib.get("image", "")
        pathw.link = root.attrib.get("link", "")

        for child in root:
            if child.tag == "entry":
                pathw.entries.append(Entry.parse(child))
            elif child.tag == "relation":
                pathw.relations.append(Relation.parse(child))
            elif child.tag == "reaction":
                # TODO: implement parsing
                pass
            else:
                logging.debug(child.tag)

        return pathw


if __name__ == "__main__":
    pass

