
.. Licensed under the MIT License

.. _kgml:

====================
KEGG Markup Language
====================

Schema
======

.. image:: media/kgml-schema.png
    :width: 400
    :alt: KGML schema


Data types
==========

.. list-table:: Types
    :widths: 30 40 30
    :header-rows: 1

    * - Name
      - Description
      - Pattern

    * - string.type
      - Simple string type.
      - :code:`^$`

    * - url.type
      - String of url to locate web resource.
      - :code:`^$`

    * - keggid.type
      - 
      - :code:`^$`

    * - maporg.type
      - 
      - :code:`^$`

    * - mapnumber.type
      - 
      - :code:`^$`

    * - id.type
      - 
      - :code:`^$`

    * - entry-type.type
      - 
      - See list of valid entry types.

    * - number.type
      - Simple digit string type. Must be at least one digit.
      - :code:`^([0-9]+)$`

    * - graphics.type
      - 
      - See list of valid graphics types.

    * - graphics-color.type
      - String of hexadecimal color.
      - :code:`^#([0-9a-fA-F]{6})$`

    * - idref.type
      - 
      - :code:`^$`

    * - relation-type.type
      - 
      - See list of valid relation types.

    * - subtype-name.type
      - 
      - See list of valid subtype names.

    * - subtype-value.type
      -
      - See list of valid subtype values.

    * - reaction-type.type
      - 
      - See list of valid reaction types.



.. list-table:: Entry type
    :widths: 30 70
    :header-rows: 1

    * - Value
      - Description


    * - ortholog
      - Ortholog entry (KO entry).

    * - enzyme
      - Enzyme entry.

    * - reaction
      - Reaction entry.

    * - gene
      - Gene product entry (Protein).

    * - group
      - Protein complex entry.

    * - compound
      - Compound entry (molecule, glycan).

    * - map
      - Linked pathway entry.

    * - brite
      - Brite hierarchy entry.

    * - other
      - Unclassified type of entry.


.. list-table:: Graphics type
    :widths: 30 70
    :header-rows: 1

    * - Value
      - Description


    * - rectangle
      - Gene products and complexes are represented with a rectangle shape.

    * - circle
      - Molecules, compounds and glycans are represented with a circle shape.

    * - roundrectangle
      - Linked pathways are represented with a rounded rectangle shape.

    * - line
      - Reactions and relations are represented with a line.



.. list-table:: Relation type
    :widths: 30 70
    :header-rows: 1

    * - Value
      - Description


    * - ECrel
      - Enzyme-enzyme relation.

    * - PPrel
      - Protein-protein relation.

    * - GErel
      - Transcription factor and target gene relation.

    * - PCrel
      - Protein-compound relation.

    * - maplink
      - Link to other pathway.



.. list-table:: Reaction type
    :widths: 30 70
    :header-rows: 1

    * - Value
      - Description


    * - reversible
      - Reversible reaction.

    * - irreversible
      - Irreversible reaction.


Elements
========

pathway
-------

The pathway element is the root element in the KGML file. All other elements are children of the element.

.. list-table:: Attributes
    :widths: 20 40 20 20
    :header-rows: 1

    * - Name
      - Description
      - Type
      - Required/Optional

    * - name
      - KEGG id of pathway.
      - keggid.type
      - Required

    * - org
      - KEGG organism identifier.
      - maporg.type
      - Required

    * - number
      - Map number of pathway.
      - mapnumber.type
      - Required

    * - title
      - Title of pathway.
      - string.type
      - Optional

    * - image
      - Url to image of pathway.
      - url.type
      - Optional

    * - link
      - Url to information of pathway.
      - url.type
      - Optional



entry
-----


.. list-table:: Attributes
    :widths: 20 40 20 20
    :header-rows: 1

    * - Name
      - Description
      - Type
      - Required/Optional

    * - id
      - Identifier of entry in pathway.
      - id.type
      - Required

    * - name
      - KEGG identifier of entry.
      - keggid.type
      - Required

    * - type
      - Type of entry.
      - entry_type.type
      - Required

    * - link
      - Url to information of this entry.
      - url.type
      - Optional

    * - reaction
      - KEGG identifier of corresponding reaction.
      - keggid.type
      - Optional


graphics
--------

.. list-table:: Attributes
    :widths: 20 40 20 20
    :header-rows: 1

    * - Name
      - Description
      - Type
      - Required/Optional

    * - name
      - Label of graphics element.
      - string.type
      - Optional

    * - x
      - X position of graphics element.
      - number.type
      - Optional

    * - y
      - Y position of graphics element.
      - number.type
      - Optional

    * - width
      - Width of graphics element.
      - number.type
      - Optional

    * - height
      - Height of graphics element.
      - number.type
      - Optional

    * - coords
      - Coordinates of a line object in graphics element. Komma-seperated list of numbers (x1,y1,x2,y2).
      - string.type
      - Optional

    * - type
      - Type of graphics element
      - graphics.type
      - Optional

    * - fgcolor
      - Foreground color used by graphics element.
      - graphics-color.type
      - Optional

    * - bgcolor
      - Background color used by graphics element.
      - graphics-color.type
      - Optional


component
---------


.. list-table:: Attributes
    :widths: 20 40 20 20
    :header-rows: 1

    * - Name
      - Description
      - Type
      - Required/Optional

    * - id
      - Identifier referencing entry in pathway.
      - idref.type
      - Required


relation
--------

.. list-table:: Attributes
    :widths: 20 40 20 20
    :header-rows: 1

    * - Name
      - Description
      - Type
      - Required/Optional

    * - entry1
      - Identifier referencing first entry in pathway.
      - idref.type
      - Required

    * - entry2
      - Identifier referencing second entry in pathway.
      - idref.type
      - Required

    * - type
      - Type of relation.
      - relation-type.type
      - Required


subtype
-------

.. list-table:: Attributes
    :widths: 20 40 20 20
    :header-rows: 1

    * - Name
      - Description
      - Type
      - Required/Optional

    * - name
      - Name of subtype.
      - subtype-name.type
      - Required

    * - value
      - Value of subtype.
      - subtype-value.type
      - Required

reaction
--------


.. list-table:: Attributes
    :widths: 20 40 20 20
    :header-rows: 1

    * - Name
      - Description
      - Type
      - Required/Optional

    * - id
      - Identifier referencing reaction in pathway.
      - idref.type
      - Required

    * - name
      - KEGG identifier of reaction.
      - keggid.type
      - Required

    * - type
      - Type of reaction.
      - reaction-type.type
      - Required


substrate
---------

.. list-table:: Attributes
    :widths: 20 40 20 20
    :header-rows: 1

    * - Name
      - Description
      - Type
      - Required/Optional

    * - id
      - Identifier of substrate.
      - idref.type
      - Required

    * - name
      - KEGG identifier of substrate.
      - keggid.type
      - Required

product
-------

.. list-table:: Attributes
    :widths: 20 40 20 20
    :header-rows: 1

    * - Name
      - Description
      - Type
      - Required/Optional

    * - id
      - Identifier of product.
      - idref.type
      - Required

    * - name
      - KEGG identifier of product.
      - keggid.type
      - Required

alt
---

.. list-table:: Attributes
    :widths: 20 40 20 20
    :header-rows: 1

    * - Name
      - Description
      - Type
      - Required/Optional

    * - name
      - Alternative name of parent element as KEGG identifier.
      - keggid.type
      - Required




