.. _ref_user_guide:

.. currentmodule:: ansys.grantami.dataflow_toolkit

User guide
##########

Introduction
------------

Granta MI Data Flow can trigger Python scripts at the beginning or end of a workflow step.
These Python scripts can execute custom business logic, including interacting with Granta MI
using the Python Scripting Toolkit or PyGranta suite of packages. Some typical use cases
include:

- Populating attributes with values computed within the Python script
- Analyzing data
- Generating links to other records
- Interacting with external systems

This package includes the code required to process the state information from Data Flow,
to pass log information back to Data Flow, and to return execution to Data Flow once the
script is complete.

It also includes some examples which demonstrate use of the library. These examples can be
extended to incorporated business logic for specific use cases.

.. _ref_installation_venv:

Installing in a virtual environment
-----------------------------------

In general, Python packages should always be installed in virtual environments to avoid package version conflicts.
However, MI Data Flow runs outside of a virtual environment, and so if one is used, Data Flow must be configured with
details of the virtual environment to be used.

To install the package in a virtual environment, first create a new virtual environment::

   python -m venv C:\path\to\my\venv

Where ``C:\path\to\my\venv`` is the path to the location where you would like the venv to be located. This should be a
location that all users can access.

Then activate the virtual environment and install the packages::

   C:\path\to\my\venv\Scripts\activate
   pip install ansys-grantami-dataflow-toolkit

Finally, modify Data Flow to use the virtual environment:

1. Create a backup copy of the ``web.config`` file. By default, this file is located at
   ``C:\inetpub\wwwroot\mi_dataflow``.
2. Open the ``web.config`` file in a text editor, and find the line ``<add key="PythonPath" value="python.exe" />``
3. Replace the string ``python.exe`` with ``C:\path\to\my\venv\Scripts\python.exe``, where ``C:\path\to\my\venv`` is the
   path to the virtual environment specified above.
4. Save the modified ``web.config`` file. If you see a permissions error, you may need to open the text editor with
   administrator privileges.
5. Reload the Data Flow worker process in IIS Manager. Warning: This stops any actively running Workflow processes.


Business logic development best practice
----------------------------------------

The steps below assume you are proficient in the use of Data Flow Designer and Data Flow Manager, and already have a
workflow fully defined with all required features apart from Python script execution. For more information on working
with Data Flow Designer, see the `Granta MI Data Flow Designer documentation
<https://ansyshelp.ansys.com/account/secured?returnurl=/Views/Secured/Granta/v242/en/mi_data_flow_designer/index.html>`_.

To implement your business logic, you should start from one of the :ref:`ref_grantami_dataflow_toolkit_examples` and
follow the steps listed below:

1. Copy the code block from one of the examples to a local ``.py`` file.
2. Switch the script to 'main' mode by commenting ``testing()`` in the ``if __name__ == "__main__":`` block and
   un-commenting ``main()``.
3. Upload the script into MI Data Flow Designer, and add it to the Start or End Script sections.
4. Run the workflow step once in MI Data Flow Manager. Obtain the ``dataflow_payload`` JSON response from the
   logs page or the ``Additional Processing Notes`` attribute in Granta MI (only available when using the
   'Standalone example' or 'Scripting Toolkit Example' notebooks).
5. Paste the ``dataflow_payload`` JSON in the corresponding variable within the ``testing()`` function. This
   allows you to debug the ``step_logic`` without re-running the workflow. See the documentation for the
   :class:`~.MIDataFlowIntegration.get_payload_as_str` and :class:`~.MIDataFlowIntegration.get_payload_as_dict` methods
   for more information, including how to handle Basic and OIDC authentication.
6. Switch back to 'testing' mode by commenting ``main()`` in the ``if __name__ == "__main__":`` block and
   un-commenting ``testing()``.
7. Modify the ``step_logic`` function with your specific logic and test locally.
8. Once the business logic is implemented, switch back to ``main()`` in the in the ``if __name__ == "__main__":``
   block (see step 1), re-upload the file into MI Data Flow Designer, and re-add it to the Start or End Script
   sections.
9. Update the workflow and test from within MI Data Flow Manager.

Repeat steps 7 to 9 as required.

Troubleshooting
---------------

This package logs to the MI Data Flow logs page available in either of the URLs below:

- MI 2023 R2 or later: ``http://my.server.name/mi_dataflow/api/logs``
- MI 2023 R1 or earlier: ``http://my.server.name/mi_workflow_2/api/logs``

A working directory is created at the server in ``C:\windows\TEMP\`` which contains the two files ``__stderr__`` and
``__stdout__``. These contain Python's console outputs that are useful when investigating Python failures during
workflow execution.
