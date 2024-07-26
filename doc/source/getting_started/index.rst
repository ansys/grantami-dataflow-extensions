.. _ref_getting_started:

Getting started
###############

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
To verify that you can import the PyGranta Data Flow Toolkit in Python, run this code:

.. code:: python

    >>> from ansys.grantami import dataflow_toolkit
    >>> print(dataflow_toolkit.__version__)

    0.0.1

If you see a version number, you have successfully installed PyGranta Data Flow Toolkit. For
best practice around developing scripts that interact with Data Flow, see :ref:`ref_user_guide`.
For examples, see :ref:`ref_grantami_dataflow_toolkit_examples`. For comprehensive information
on the API, see :ref:`ref_grantami_dataflow_toolkit_api_reference`.
