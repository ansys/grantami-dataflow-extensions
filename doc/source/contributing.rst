.. _ref_contributing:

Contribute
##########

General guidelines
==================
Overall guidance on contributing to a PyAnsys library appears in the
`Contributing <https://dev.docs.pyansys.com/how-to/contributing.html>`_ topic
in the *PyAnsys developer's guide*. Ensure that you are thoroughly familiar
with this guide before attempting to contribute to PyGranta Data Flow Extensions.

The following contribution information is specific to PyGranta Data Flow Extensions.

Developer environment setup
===========================

PyGranta Data Flow Extensions uses `Poetry`_ for packaging and dependency management.
Installation information is available in the Poetry documentation.

Installing PyGranta Data Flow Extensions in developer mode allows you to modify and
enhance the source.

Clone the source repository
---------------------------

Run the following commands to clone and install the latest version of PyGranta Data Flow
Extensions in editable mode, which ensures changes to the code are immediately visible in the
environment. Running these commands also installs the required development dependencies to
run the tests, build the documentation, and build the package.

.. code:: bash

    git clone https://github.com/ansys/grantami-dataflow-extensions
    cd grantami-dataflow-extensions
    poetry install --with doc

Additional tools
-----------------

.. _ref_precommit:

Pre-commit
~~~~~~~~~~

The style checks take advantage of `pre-commit`_. Developers are not forced but
encouraged to install this tool with this command:

.. code:: bash

    python -m pip install pre-commit && pre-commit install


Code formatting and styling
===========================

This project adheres to PyAnsys styling and formatting recommendations. The easiest way to
validate changes are compliant is to run this command:

.. code:: bash

    pre-commit run --all-files


.. _ref_documenting:

Documenting
===========

As per PyAnsys guidelines, the documentation is generated using `Sphinx`_.

For building documentation, use the Sphinx Makefile:

.. code:: bash

    make -C doc/ html && your_browser_name doc/build/html/index.html

If any changes have been made to the documentation, you should run
Sphinx directly with the following extra arguments:

.. code:: bash

    sphinx-build -b html source build -W -n --keep-going

The extra arguments ensure that all references are valid and turn warnings
into errors. CI uses the same configuration, so you should resolve any
warnings and errors locally before pushing changes.

Example notebooks
=================
Examples are included in the documentation to give you more context around
the core capabilities described in :ref:`ref_grantami_dataflow_extensions_api_reference`.
Additional examples are welcomed, especially if they cover a key use case of the
package that has not yet been covered.

The example scripts are placed in the ``examples`` directory and are included
in the documentation build if the environment variable ``BUILD_EXAMPLES`` is set
to ``True``. Otherwise, a different set of examples is run to validate the process.

Examples are checked in as scripts using the ``light`` format. For more information,
see the `Jupytext documentation <jupytext_>`_. As part of the documentation-building
process, the Python files are converted back into Jupyter notebooks and the output
cells are populated by running the notebooks against a Granta MI™ instance.

This conversion between Jupyter notebooks and Python files is performed by
`nb-convert`_. Installation information is available in the ``nb-convert`` documentation.

Post issues
===========
Use the `PyGranta Data Flow Extensions Issues <https://github.com/pyansys/grantami-dataflow-extensions/issues>`_
page to report bugs and request new features. When possible, use the issue templates provided. If
your issue does not fit into one of these templates, click the link for opening a blank issue.

If you have general questions about the PyAnsys ecosystem, email `pyansys.core@ansys.com <pyansys.core@ansys.com>`_.
If your question is specific to PyGranta Data Flow Extensions, ask your question in an issue as described in
the previous paragraph.

.. _Poetry: https://python-poetry.org/
.. _pre-commit: https://pre-commit.com/
.. _Sphinx: https://www.sphinx-doc.org/en/master/
.. _jupytext: https://jupytext.readthedocs.io/en/latest/
.. _nb-convert: https://nbconvert.readthedocs.io/en/latest/
