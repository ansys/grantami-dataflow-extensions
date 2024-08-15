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

#. Create a backup copy of the ``web.config`` file. By default, this file is located at
   ``C:\inetpub\wwwroot\mi_dataflow``.
#. Open the ``web.config`` file in a text editor, and find the line ``<add key="PythonPath" value="python.exe" />``
#. Replace the string ``python.exe`` with ``C:\path\to\my\venv\Scripts\python.exe``, where ``C:\path\to\my\venv`` is the
   path to the virtual environment specified above.
#. Save the modified ``web.config`` file. If you see a permissions error, you may need to open the text editor with
   administrator privileges.
#. Reload the Data Flow worker process in IIS Manager. Warning: This stops any actively running Workflow processes.


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

.. currentmodule:: pathlib

If the file is stored externally (for example in a folder C:\DataflowFiles), then you should use the
:class:`Path` class to ensure you are using an absolute path, which is independent of the Python working
directory. For example::

   my_path = pathlib.Path("C:\DataflowFiles\my_data.csv")


.. currentmodule:: ansys.grantami.dataflow_toolkit

Or in the case of providing a custom CA certificate to the :class:`~.MIDataflowIntegration` constructor::

  my_cert = pathlib.Path(C"\DataflowFiles\my_cert.crt")
  dataflow = MIDataflowIntegration(certificate_file=my_cert)

The advantage of this approach is that files can easily be shared across workflow definitions, and do not need to be
uploaded to each one separately. However, the disadvantage is that the files are stored outside of the workflow
definition, and so does not automatically upload/download these files from the server when using Data Flow Manager.


Store files within the workflow definition
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If the file is stored within the workflow definition, then Data Flow makes these files are available on disk at
script runtime in a Data Flow-managed location. To access files in this location, use the
:attr:`~.MIDataflowIntegration.supporting_files_dir` property. For example, to access a CSV file which was uploaded as a
supporting file to Data Flow::

   dataflow = MIDataflowIntegration()
   my_path = dataflow.supporting_files_dir \ "my_data.csv"


In the case of providing a custom CA certificate to the :class:`~.MIDataflowIntegration` constructor, the filename can
be provided as a string, and the Data Flow Toolkit automatically looks for the file in this location::

  my_cert = "my_cert.crt"
  dataflow = MIDataflowIntegration(certificate_file=my_cert)

The advantage of this approach is that files are managed by Data Flow Designer and are automatically included in the
workflow definition if it is uploaded/downloaded and transferred to a different system. However, the disadvantage is
that each workflow definition tracks the supporting files separately, and so every workflow needs to be modified
separately if a commonly used supporting file is changed.

.. warning::
   This property depends on the use of the ``sys.path`` property, specifically that ``sys.path[0]`` refers
   to the location of the executing script. If you intend to use supporting files with your Python scripts, you must
   not prepend additional paths to the ``sys.path`` property.


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
   :meth:`~.MIDataflowIntegration.get_payload_as_string` and :meth:`~.MIDataflowIntegration.get_payload_as_dict` methods
   for more information, including how to handle Basic and OIDC authentication.
6. Switch back to 'testing' mode by commenting ``main()`` in the ``if __name__ == "__main__":`` block and
   un-commenting ``testing()``.
7. Modify the ``step_logic`` function with your specific logic and test locally.
8. Once the business logic is implemented, switch back to ``main()`` in the in the ``if __name__ == "__main__":``
   block (see step 1), re-upload the file into MI Data Flow Designer, and re-add it to the Start or End Script
   sections.
9. Update the workflow and test from within MI Data Flow Manager.

Repeat steps 7 to 9 as required.


.. _ref_user_guide_logging:

.. currentmodule:: logging


Logging and debugging
---------------------

It is generally required to log outputs from scripts to help with debugging and to understand the inner state of the
script. These use cases apply to this package as well, but because the script is executed as part of Data Flow, the
recommended best practices are different to those of a conventional Python script.

A very simple approach to logging the output of a script is to use the ``print()`` function to write text to the
terminal. This approach can be used with this package, and any printed messages are visible in the central Data Flow
log, available at one of the URLs below depending on your Granta MI version:

* MI 2023 R2 or later: ``http://my.server.name/mi_dataflow/api/logs``
* MI 2023 R1 or earlier: ``http://my.server.name/mi_workflow_2/api/logs``

However, using the ``print()`` function offers limited control around log format, and message filtering. Instead, the
recommended approach is to use the Python logging module. See the provided links for the Python
`logging API documentation`_ and `Logging HOWTO`_.

The internal operations of this package are logged to a logger with the name ``ansys.grantami.dataflow_toolkit``. By
default, these messages are not output. To output the messages generated by this package and to add your own log
messages, you should:

#. Create a logger for your script.
#. Attach a handler to the logger.

The following sub-sections provide simple best practice for logging with this package. However, Python logging is
extremely versatile and it is possible to construct complex logging implementations for your use case. Consult the
Python API documentation and user guides referenced earlier in this section for a more complete review of the
capabilities of Python logging.

Create a logger
~~~~~~~~~~~~~~~

Python ``logger`` objects are hierarchical, and messages are passed from lower level ``logger`` objects to higher level
ones. The root of the logger hierarchy is the *root logger*, and contains all messages logged by all loggers in a Python
instance.

For single-module scripts generally used with this script, it is recommended to use the root logger directly to ensure
that all log messages are included in the output. To create an instance of the root logger and have it capture log
messages of ``logging.DEBUG`` level and higher, use the following code::

   import logging
   logger = logging.getLogger()
   logger.setLevel(logging.DEBUG)

You can then add log statements to the logger at a certain log level as follows::

   logger.debug("This is a debug message")
   logger.info("This is an info message")

Note that until a log handler is attached, no log messages are emitted.


Attach a handler
~~~~~~~~~~~~~~~~

There are two main types of handlers provided by the Python logging library: :class:`FileHandler` handlers and
:class:`StreamHandler` handlers. A :class:`FileHandler` is used to write log messages to a file on disk, and a
:class:`StreamHandler` is used to write log messages to ``stderr`` or ``stdout``.

For code using this package, it is best practice to log to ``stderr``, which is collected by Data Flow toolkit and
included in the central Data Flow log. To add a :class:`StreamHandler` handler to the root logger from the previous
section, use the following code::

    ch = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    logger.addHandler(ch)

It is possible to also log files to disk by using a :class:`FileHandler`. The following example shows creating a
:class:`FileHandler` handler with a filename based on the current timestamp with 1 second precision::

    import datetime

    now = datetime.datetime.now()
    filename = now.strftime("log-%Y%m%d-%H%M%S.log")
    fh = logging.FileHandler(filename=filename)
    fh.setFormatter(formatter)
    # fh.setLevel(logging.DEBUG)

    logger.addHandler(fh)

.. warning::

   If you use a :class:`FileHandler` you **must** ensure that each instance of the script writes the logs to different
   file or you may encounter a ``PermissionError``. In certain authentication modes the script executes as the active
   Data Flow user, and so either multiple users could run the same script concurrently, or may try to append to a file
   created by a different user.


Additional debugging
~~~~~~~~~~~~~~~~~~~~

Additionally, Data Flow creates a working directory on the server in ``C:\windows\TEMP\{workflow id}_{8.3}``, where
``{workflow_id}`` is the workflow ID provided in Data Flow Designer when uploading the workflow, and ``{8.3}`` is a
random set of 8 alphanumeric characters, a period, and 3 alphanumeric characters. This can be found by right-clicking
the active workflow in Data Flow Manager and selecting 'View Log'.

This directory includes the two files ``__stderr__`` and ``__stdout__``, which contain the Python stdout and stderr
streams and are useful when investigating Python failures during workflow execution before the logger has been
initialized.

It would be possible to create a :class:`FileHandler` to create a log file in this directory. To access this directory,
use the following code::

   import os
   working_dir = os.getcwd()

However, note that once the workflow is successfully resumed, this folder and all its contents are deleted. They are
only persisted if the workflow is manually cancelled in Data Flow Manager.

.. _logging API documentation: https://docs.python.org/3/library/logging.html
.. _Logging HOWTO: https://docs.python.org/3/howto/logging.html
