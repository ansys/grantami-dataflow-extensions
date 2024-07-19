.. _ref_user_guide:

.. currentmodule:: ansys.grantami.dataflow-toolkit

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

1. Create a backup copy of the ``web.config`` file. By default, this file will be in ``C:\inetpub\wwwroot\mi_dataflow``,
   but the location can be changed during installation.
2. Open the ``web.config`` file in a text editor, and find the line ``<add key="PythonPath" value="python.exe" />``
3. Replace the string ``python.exe`` with ``C:\path\to\my\venv\Scripts\python.exe``, where ``C:\path\to\my\venv`` is the
   path to the virtual environment specified above.
4. Save the modified ``web.config`` file. If you see a permissions error, you may need to open the text editor with
   administrator privileges.
5. Reload the Data Flow worker process in IIS Manager. Warning: This will terminate any actively running Workflow
   processes.


Best practice for developing your own business logic
----------------------------------------------------

TODO - Update once examples are finalized

To implement your business logic, you can start from the dataflow_example_script.py script, ``step_logic`` function.
The best practice for developing your own business logic script is described as follows:

1. Design your workflow in MI Data Flow Designer with all Expected and Auto Attribute Patterns. Add the
   dataflow_example_script.py in the Start or End Script sections.
2. Run the workflow step once in MI Data Flow Manager. Obtain the ``workflow_stream`` JSON response from the
   logs page or the TODO FILL IN ATTRIBUTE NAME in Granta MI.
3. Paste the ``workflow_stream`` JSON in the corresponding variable within the ``testing()`` function. This
   will allow you to debug the ``step_logic`` without re-running the workflow.
4. Edit the ``service_layer_url`` and credentials to connect to the MI session in the testing() function.
5. Switch to 'testing' mode by commenting ``main()`` in the ``if __name__ == "__main__":`` function and
   uncommenting ``testing()``.
6. Modify the ``step_logic`` function with your specific logic and test it by running the file locally.
7. Once the business logic is implemented, switch back to ``main()`` in the in the ``if __name__ == "__main__":``
   function and reload the file ``dataflow_example_script.py`` into MI Data Flow Designer, re-selecting it in the
   Start or End Script sections.
8.  Delete the previous workflow, publish the new one and test from within MI Data Flow Manager.

For more information on working with Data Flow Designer, see the
`Granta MI Data Flow Designer documentation
<https://ansyshelp.ansys.com/account/secured?returnurl=/Views/Secured/Granta/v242/en/mi_data_flow_designer/index.html>`_.

Troubleshooting
---------------

This package logs to the MI Data Flow logs page available in either of the URLs below:

- MI 2023 R2 or later: ``http://my.server.name/mi_dataflow/api/logs``
- MI 2023 R1 or earlier: ``http://my.server.name/mi_workflow_2/api/logs``

A working directory is created at the server in ``C:\windows\TEMP\`` which contains the two files
``__stderr__`` and ``__stdout__``. These will contain Python's console outputs that can be useful
when investigating Python failures during workflow execution.
