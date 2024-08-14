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


Supporting files
----------------

It is common for Python scripts to depend on additional supporting files, for example:

* Additional Python submodules
* Data files, such as JSON or CSV files
* Certificate Authority (CA) certificate files

These files can either be stored in a known location on disk and referred to explicitly via an absolute path, or they
can be added to the workflow definition in Data Flow Designer. There are pros and cons to each method.

Store files externally
~~~~~~~~~~~~~~~~~~~~~~

If the file is stored externally (for example in a folder C:\DataflowFiles), then you should use the
:class:`pathlib.Path` class to ensure you are using an absolute path, which is independent of the Python working
directory. For example::

   my_path = pathlib.Path("C:\DataflowFiles\my_data.csv")

Or in the case of providing a custom CA certificate to the :class:`~.MIDataflowIntegration` constructor::

  my_cert = pathlib.Path(C"\DataflowFiles\my_cert.crt")
  dataflow = MIDataflowIntegration(certificate_file=my_cert)

The advantage of this approach is that files can easily be shared across workflow definitions, and do not need to be
uploaded to each one separately. However, the disadvantage is that the files are stored outside of the workflow
definition, and so will not automatically be uploaded to/downloaded from the server when using Data Flow Manager.


Store files within the workflow definition
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If the file is stored within the workflow definition, then Data Flow will ensure these files are available on disk at
script runtime in a Data Flow-managed location. To access files in this location, use the
:attr:`~.MIDataflowIntegration.supporting_files_dir` property. For example, to access a CSV file which was uploaded as a
supporting file to Data Flow::

   dataflow = MIDataflowIntegration()
   my_path = dataflow.supporting_files_dir \ "my_data.csv"


In the case of providing a custom CA certificate to the :class:`~.MIDataflowIntegration` constructor, the filename can
be provided as a string, and the Data Flow Toolkit will automatically look for the file in this location::

  my_cert = "my_cert.crt"
  dataflow = MIDataflowIntegration(certificate_file=my_cert)

The advantage of this approach is that files are managed by Data Flow Designer and are automatically included in the
workflow definition if it is uploaded/downloaded and transferred to a different system. However, the disadvantage is
that each workflow definition tracks the supporting files separately, and so every workflow needs to be modified
separately if a commonly used supporting file is changed.

.. warning::
   This functionality depends on the use of the ``sys.path`` property, specifically that ``sys.path[0]`` refers
   to the location of the executing script. If you intend to use supporting files with your Python scripts, you must
   not prepend additional paths to the ``sys.path`` property.


Business logic development best practice
----------------------------------------

The steps below assume you are proficient in the use of Data Flow Designer and Data Flow Manager, and already have a
workflow fully defined with all required features apart from Python script execution. For more information on working
with Data Flow Designer, see the `Granta MI Data Flow Designer documentation
<https://ansyshelp.ansys.com/account/secured?returnurl=/Views/Secured/Granta/v242/en/mi_data_flow_designer/index.html>`_.

To implement your business logic, you should start from one of the :ref:`ref_grantami_dataflow_toolkit_examples`, and
follow the steps listed below:

1. Copy the code block from one of the examples to a local ``.py`` file.
2. Switch the script to 'main' mode by commenting ``testing()`` in the ``if __name__ == "__main__":`` block and
   un-commenting ``main()``.
3. Upload the script into MI Data Flow Designer, and add it to the Start or End Script sections.
4. Run the workflow step once in MI Data Flow Manager. Obtain the ``dataflow_payload`` JSON response from the
   logs page or the ``Additional Processing Notes`` attribute in Granta MI.
5. Paste the ``dataflow_payload`` JSON in the corresponding variable within the ``testing()`` function. This
   allows you to debug the ``step_logic`` without re-running the workflow.
6. Edit the ``service_layer_url`` and credentials to connect to the MI session in the ``testing()`` function.
7. Switch back to 'testing' mode by commenting ``main()`` in the ``if __name__ == "__main__":`` block and
   un-commenting ``testing()``.
8. Modify the ``step_logic`` function with your specific logic and test locally.
9. Once the business logic is implemented, switch back to ``main()`` in the in the ``if __name__ == "__main__":``
   block (see step 1), re-upload the file into MI Data Flow Designer, and re-add it to the Start or End Script
   sections.
10. Update the workflow and test from within MI Data Flow Manager.

Repeat steps 8 to 10 as required.

Troubleshooting
---------------

This package logs to the MI Data Flow logs page available in either of the URLs below:

- MI 2023 R2 or later: ``http://my.server.name/mi_dataflow/api/logs``
- MI 2023 R1 or earlier: ``http://my.server.name/mi_workflow_2/api/logs``

A working directory is created at the server in ``C:\windows\TEMP\`` which contains the two files ``__stderr__`` and
``__stdout__``. These contain Python's console outputs that are useful when investigating Python failures during
workflow execution.
