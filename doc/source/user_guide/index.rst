.. _ref_user_guide:

.. currentmodule:: ansys.grantami.dataflow_extensions

User guide
##########

Introduction
------------

Granta MI Data Flow can trigger Python scripts at the beginning or end of a workflow step. These Python scripts can
execute custom business logic, including interacting with Granta MI systems using the Python Scripting Toolkit or
PyGranta suite of packages. Some typical use cases include:

- Populating attributes with values computed within the Python script
- Analyzing data
- Generating links to other records
- Interacting with external systems

The ``dataflow-extensions`` package includes the code required to process the state information from Data Flow, to pass
log information back to Data Flow, and to return execution to Data Flow once the script is complete.

It also includes :ref:`examples <ref_grantami_dataflow_extensions_examples>` which demonstrate use of the library.
These examples can be extended to incorporate business logic for specific use cases. In particular, the
:doc:`../examples/1_Standalone` gives a detailed description of the core components of a typical ``dataflow-extensions``
script.

The rest of this user guide provides more detail around specific aspects of the interaction with Data Flow.


Integration with MI Data Flow
-----------------------------

This package is designed to be used with Granta MI Data Flow. The integration works as follows:

#. At a defined point in a workflow MI Data Flow triggers a Python script and pauses the workflow until the script
   resumes the workflow.
#. The Python script executes, potentially utilizing additional Ansys or third-party Python packages.
#. At a defined point in the Python script (generally the end), the Python script instructs MI Data Flow to resume the
   workflow.
#. The Python script ends.

MI Data Flow payload
~~~~~~~~~~~~~~~~~~~~

.. currentmodule:: ansys.grantami.dataflow_extensions

When MI Data Flow triggers a Python script, it provides context about the current state of the workflow as a JSON-
formatted string. This string is referred to as the 'MI Data Flow payload', and an example is given below:

.. code-block:: json

   {
       "WorkflowId": "67eb55ff-363a-42c7-9793-df363f1ecc83",
       "WorkflowDefinitionId": "Example; Version=1.0.0.0",
       "TransitionName": "Python_83e51914-3752-40d0-8350-c096674873e2",
       "Record": {
           "Database": "MI_Training",
           "Table": "Metals Pedigree",
           "RecordHistoryGuid": "d2f51a3d-c274-4a1e-b7c9-8ba2976202cc",
       },
       "WorkflowUrl": "http://my_server_name/mi_dataflow",
       "AuthorizationHeader": "",
       "ClientCredentialType": "Windows",
       "Attributes": {
           "Record": {"Value": ["d2f51a3d-c274-4a1e-b7c9-8ba2976202cc+MI_Training"]},
           "TransitionId": {"Value": "9f1bf6e7-0b05-4cd3-ac61-1d2d11a1d351"},
       },
       "CustomValues": {},
   }

This payload includes the following information:

* Internal data flow identifiers, including:

  * Workflow ID
  * Workflow definition ID
  * Transition name

* Workflow record reference and table name
* MI Data flow web server URL
* Server authorization information
* Custom values defined in the workflow definition

.. note::
   If MI Data Flow is configured in Basic or OIDC authentication mode, the server authorization information contains an
   obfuscated username and password or an OIDC refresh token respectively. In these configurations, the payload should
   be treated as confidential.

When a ``dataflow-extensions``-based Python script is launched by MI Data Flow, the :class:`~.MIDataflowIntegration`
constructor automatically parses the payload from ``stdin``. However, when developing and debugging a
``dataflow-extensions``-based script, it is recommended to run and debug the script separate to Data Flow by first
generating a Data Flow payload, and then using it to instantiate the :class:`~.MIDataflowIntegration` class. These steps
are described in `Business logic development best practice`_.


Recommended script structure
----------------------------

These are the recommended components of a script that makes use of ``dataflow-extensions``:

Logging
~~~~~~~

This package supports two approaches to logging.

Stream logging
++++++++++++++

Recommended for simple, short-running scripts.

``stdout`` and ``stderr`` are collected by MI Data Flow and included in the central Data Flow log.

Use the built-in Python logging module to create a logger and write to ``stderr``, which is collected by MI Data Flow
and logged centrally on the Granta MI server once the script execution has completed::

   # Create an instance of the root logger
   logger = logging.getLogger()
   logger.setLevel(logging.INFO)

   # Add a StreamHandler to write the output to stderr
   ch = logging.StreamHandler()
   formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
   ch.setFormatter(formatter)
   logger.addHandler(ch)

Direct logging via API
++++++++++++++++++++++

Recommended for scripts expected to run for a few minutes or more.

Log messages can be sent directly to MI Data Flow via :meth:`~.MIDataflowIntegration.log_msg_to_instance`. In this case,
log messages are immediately visible for the workflow instance via the Dashboard and are also logged in the
central Data Flow logs. This can be useful to report progress during long-running scripts. For example::

   dataflow_integration = MIDataflowIntegration()
   dataflow_integration.log_msg_to_instance("Script started", level="Info")

``main()``
~~~~~~~~~~

Instantiates the :class:`~.MIDataflowIntegration` class directly, which parses the data passed into this script via
``stdin`` by MI Data Flow. Executes the business logic in ``step_logic()``, and resumes the workflow once the business
logic has completed::

   def main():
       """
       Initializes the Data Flow integration module, runs the business logic,
       and cleans up once execution has completed.
       """
       dataflow_integration = MIDataflowIntegration()

       try:
           step_logic(dataflow_integration)
           exit_code = 0
       except Exception:
           traceback.print_exc()
           exit_code = 1
       dataflow_integration.resume_bookmark(exit_code)


``testing()``
~~~~~~~~~~~~~

Instantiates the :class:`~.MIDataflowIntegration` class from a static payload defined within the function. Executes the
business logic in ``step_logic()``::

   def testing():
     """Contains a static copy of an MI Data Flow data payload for testing purposes"""

     dataflow_payload = { ... }

     dataflow_integration = MIDataflowIntegration.from_dict_payload(
       dataflow_payload=dataflow_payload,
       use_https=False,
     )
     step_logic(dataflow_integration)


``step_logic()``
~~~~~~~~~~~~~~~~

Contains the actual business logic for the step. In the initial example, the business logic just logs the payload::

   def step_logic(dataflow_integration):
       """Contains the business logic to be executed as part of the workflow.

       Replace the code in this module with your custom business logic."""

       payload = dataflow_integration.get_payload_as_string(
           include_credentials=False,
       )
       logger.info("Writing dataflow payload.")
       logger.info(payload)


Either ``main()`` or ``testing()`` should be executed when running the script. Python best practice is to use an
``if __name__ == "main"`` block, such as::

   if __name__ == "__main__":
       # main()  # Used when running the script as part of a workflow
       testing()  # Used when testing the script manually

In this state, the script runs the ``testing()`` function for testing separately to MI Data Flow. To switch the code to run
the ``main()`` function, un-comment the ``main()`` line and comment the ``testing()`` line::

   if __name__ == "__main__":
       main()  # Used when running the script as part of a workflow
       # testing()  # Used when testing the script manually

This code now expects the payload to be provided via ``stdin``.

To see all these script components together as a single example, see :doc:`../examples/1_Standalone`.


Business logic development best practice
----------------------------------------

The steps below assume you are proficient in the use of MI Data Flow Designer and MI Data Flow Manager, and already have
a workflow fully defined with all required features apart from Python script execution. For more information on working
with MI Data Flow Designer, see the `Granta MI Data Flow Designer documentation
<https://ansyshelp.ansys.com/account/secured?returnurl=/Views/Secured/Granta/v251/en/mi_data_flow_designer/index.html>`_.


Obtaining an MI Data Flow payload for a workflow step
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Copy one of the example scripts and using it to obtain a JSON-formatted Data Flow payload,
which makes development much more straightforward. The steps to obtain the payload are described below:

1. Copy the code block from the :doc:`../examples/1_Standalone` or :doc:`../examples/2_Scripting_Toolkit` to a local
   ``.py`` file.

   * If you are starting from the Scripting Toolkit example, you **must** make sure that Scripting Toolkit is installed.
   * If you plan to develop PyGranta-based business logic, start from the Standalone example.

2. Switch the script to 'main' mode by commenting ``testing()`` in the ``if __name__ == "__main__":`` block and
   un-commenting ``main()``::

      if __name__ == "__main__":
          main()  # Used when running the script as part of a workflow
          # testing()  # Used when testing the script manually

3. Upload the script into MI Data Flow Designer, and add it to the Start or End Script sections for the relevant step.
4. Run the workflow step once in MI Data Flow Manager.
5. Obtain the payload:

   * If you started from the Standalone example, obtain the payload from the Data Flow log. See
     :ref:`ref_user_guide_logging` for log file locations.
   * If you started from the Scripting Toolkit example, obtain the payload from the ``Additional Processing Notes``
     attribute.

You should now have a JSON-formatted string which contains information specific to your deployment of Granta MI,
including the Data Flow web server URL and internal workflow identifiers.


Developing business logic
~~~~~~~~~~~~~~~~~~~~~~~~~

Now the MI Data Flow payload has been obtained, it can be used to test your custom business logic separate to the
workflow. This makes it much faster to re-run the script, and allows running and debugging the script in an IDE. The
steps to use this payload to develop your custom business logic are described below:

1. Optional: If you are planning to develop a PyGranta-based script, replace the code you copied previously with the
   :doc:`../examples/3_RecordLists`, and modify the PyGranta library as required.
2. Paste the payload JSON into the ``testing()`` function::

      def testing():
        """Contains a static copy of an MI Data Flow data payload for testing purposes"""

        # Paste payload below
        dataflow_payload = { ... }

        # Call MIDataflowIntegration constructor with "dataflow_payload" argument
        # instead of reading data from MI Data Flow.
        dataflow_integration = MIDataflowIntegration.from_dict_payload(
          dataflow_payload=dataflow_payload,
          use_https=False,
        )
        step_logic(dataflow_integration)

   See the documentation for the :meth:`~.MIDataflowIntegration.get_payload_as_string` and
   :meth:`~.MIDataflowIntegration.get_payload_as_dict` methods for more information, including how to handle Basic and
   OIDC authentication.
3. Switch back to 'testing' mode by commenting ``main()`` in the ``if __name__ == "__main__":`` block and
   un-commenting ``testing()``::

      if __name__ == "__main__":
          # main()  # Used when running the script as part of a workflow
          testing()  # Used when testing the script manually

4. Add your specific logic to the ``step_logic`` function and test locally.
5. Once the business logic is implemented, switch back to ``main()`` in the in the ``if __name__ == "__main__":``
   block, re-upload the file into MI Data Flow Designer, and re-add it to the Start or End Script sections.
6. Update the workflow and test from within MI Data Flow Manager.

Repeat steps 3 to 6 as required.


.. _ref_user_guide_logging:

.. currentmodule:: logging


Logging and debugging
---------------------

It is generally required to log outputs from scripts to help with debugging and to understand the inner state of the
script. These use cases apply to this package as well, but because the script is executed as part of MI Data Flow, the
recommended best practices are different to those of a conventional Python script.

A very simple approach to logging the output of a script is to use the ``print()`` function to write text to the
terminal. This approach can be used with this package, and any printed messages are visible in the central Data Flow
log, available at ``http://my.server.name/mi_dataflow/api/logs``.

However, using the ``print()`` function offers limited control around log format and message filtering. Instead, the
recommended approach is to use the Python logging module. For more information, see the Python documentation:

* `logging API documentation`_
* `Logging HOWTO`_.

The internal operations of this package are logged to a logger with the name ``ansys.grantami.dataflow_extensions``. By
default, these messages are not output. To output the messages generated by this package and to add your own log
messages, you should:

#. Create a logger for your script.
#. Attach a handler to the logger.

The following sub-sections provide simple best practice for logging with this package.

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

.. note::

   Until a log handler is attached, no log messages are emitted.


Attach a handler
~~~~~~~~~~~~~~~~

There are two main types of handlers provided by the Python logging library: :class:`FileHandler` handlers and
:class:`StreamHandler` handlers. A :class:`FileHandler` is used to write log messages to a file on disk, and a
:class:`StreamHandler` is used to write log messages to ``stderr`` or ``stdout``.

For code using this package, it is best practice to log to ``stderr``, which is collected by ``dataflow-extensions`` and
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
   Data Flow user, and so either multiple users could run the same script concurrently, or a user may try to append to a
   file created by a different user.


Additional debugging
~~~~~~~~~~~~~~~~~~~~

MI Data Flow creates a working directory on the server in ``%WINDIR%\TEMP\{workflow id}_{8.3}``, where
``{workflow_id}`` is the workflow ID provided in MI Data Flow Designer when uploading the workflow, and ``{8.3}`` is a
random set of 8 alphanumeric characters, a period, and 3 alphanumeric characters. This can be found by right-clicking
the active workflow in MI Data Flow Manager and selecting 'View Log'.

This directory includes the two files ``__stderr__`` and ``__stdout__``, which contain the Python stdout and stderr
streams and are useful when investigating Python failures during workflow execution before the logger has been
initialized.

You can create a :class:`FileHandler` to create a log file in this directory. To access this directory,
use the following code::

   import os
   working_dir = os.getcwd()

.. note::

  When the workflow resumes, this folder and all its contents are deleted. They are only persisted if the workflow is
  manually cancelled.

.. _logging API documentation: https://docs.python.org/3/library/logging.html
.. _Logging HOWTO: https://docs.python.org/3/howto/logging.html


Supporting files
----------------

It is common for Python scripts to depend on additional supporting files, for example:

* Additional Python submodules
* Data files, such as JSON or CSV files
* Certificate Authority (CA) certificate files

These files can either be stored in a known location on disk and referred to explicitly via an absolute path, or they
can be added to the workflow definition in MI Data Flow Designer:

Storing files externally
~~~~~~~~~~~~~~~~~~~~~~~~

.. currentmodule:: pathlib

If the file is stored externally (for example in a folder ``C:\DataflowFiles``), then you should use the :class:`Path`
class to ensure you are using an absolute path, which is independent of the Python working directory. For example::

   my_path = pathlib.Path(r"C:\DataflowFiles\my_data.csv")


.. currentmodule:: ansys.grantami.dataflow_extensions

Or in the case of providing a custom CA certificate to the :class:`~.MIDataflowIntegration` constructor::

  my_cert = pathlib.Path(r"C:\DataflowFiles\my_cert.crt")
  dataflow = MIDataflowIntegration(certificate_file=my_cert)

* The advantage of this approach is that files can easily be shared across workflow definitions, and do not need to be
  uploaded to each one separately.
* The disadvantage is that the files are stored outside of the workflow definition, and do not get automatically
  uploaded or downloaded from the server when using MI Data Flow Manager.


Storing files within the workflow definition
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If the file is stored within the workflow definition, then MI Data Flow makes these files available on disk at
script runtime. To access these files, use the :attr:`~.MIDataflowIntegration.supporting_files_dir` property. For
example, to access a CSV file which was uploaded as a supporting file to MI Data Flow::

   dataflow = MIDataflowIntegration()
   my_path = dataflow.supporting_files_dir \ "my_data.csv"


If you are providing a custom CA certificate to the :class:`~.MIDataflowIntegration` constructor, the filename can
be provided as a string, and ``dataflow-extensions`` automatically looks for the file in this location::

  my_cert = "my_cert.crt"
  dataflow = MIDataflowIntegration(certificate_file=my_cert)

The advantage of this approach is that files are managed by MI Data Flow Designer and are automatically included in the
workflow definition if it is uploaded or downloaded and transferred to a different system. However, the disadvantage is
that each workflow definition tracks the supporting files separately, and so every workflow needs to be modified
separately if a commonly used supporting file is changed.

.. warning::
   This property depends on the use of the ``sys.path`` property, specifically that ``sys.path[0]`` refers
   to the location of the executing script. If you intend to use supporting files with your Python scripts, you must
   not prepend additional paths to the ``sys.path`` property.
