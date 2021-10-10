
.. Licensed under the MIT License

.. _graphviz: https://www.graphviz.org/download/

.. _install:


============
Installation
============

.. highlight:: console
.. _setuptools: https://pypi.org/project/setuptools/

Dependencies
------------

The ``keggtools`` package only supports ``python>=3.6``.

The dependencies used for this package are ``pydot``, ``requests``, ``scipy``  and ``tqdm``.

To install ``pydot`` you need to install ``graphviz`` first. This dependency is required to render pathways.
Install graphviz on `Ubuntu`. More graphviz install options graphviz_.

.. code-block:: bash

    sudo apt install graphviz

For installation of the remaining ``python`` dependencies, you can simply use ``pip``

.. code-block:: bash

    python3 -m pip install pydot requests scipy tqdm


Package Installation
--------------------

The easiest way to install ``keggtools`` is ``pip``

.. code-block:: bash

    python3 -m pip install keggtools


Alternativ Installation Methods
-------------------------------

Install from Github repo

.. code-block:: bash

    python3 -m pip install git+https://github.com/harryhaller001/keggtools


Or install package from local source files

.. code-block:: python


    # Clone repo
    git clone https://github.com/harryhaller001/keggtools.git
    cd keggtools

    # Install dependencies and package
    python3 -m pip install -r requirements.txt
    python3 setup.py install

