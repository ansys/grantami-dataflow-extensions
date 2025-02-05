.. _ref_getting_started:

Getting started
===============

.. _ref_software_requirements:

Software requirements
~~~~~~~~~~~~~~~~~~~~~~
.. include:: ../../../README.rst
      :start-after: readme_software_requirements
      :end-before: readme_software_requirements_end


Installation
~~~~~~~~~~~~
.. include:: ../../../README.rst
      :start-after: readme_installation
      :end-before: readme_installation_end


Verify your installation
~~~~~~~~~~~~~~~~~~~~~~~~
To verify that your installation has been successful, run this code:

.. code:: python

    >>> from ansys.grantami import dataflow_extensions
    >>> print(dataflow_extensions.__version__)

    0.0.1

If you see a version number, your PyGranta Data Flow Extensions is installed.

Useful links
* For best practice around developing scripts that interact with Data Flow, see the :ref:`ref_user_guide`.
* For examples, see the :ref:`ref_grantami_dataflow_extensions_examples`.
* For comprehensive information on the API, see :ref:`ref_grantami_dataflow_extensions_api_reference`.
