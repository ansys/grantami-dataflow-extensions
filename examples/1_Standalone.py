# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.16.3
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# # Standalone example

# This notebook provides a best-practice example for using Data Flow Toolkit to interact with a non-Granta MI resource
# as part of a Data Flow operation.

# The cell below contains an example script that simply logs the record identifying information which is received from
# Data Flow. However, this could be replaced with any other business logic which can make use of the data provided by
# Data Flow. To perform operations that rely on additional information from Granta MI, see the other examples in this
# package.

# The example script sets up logging (see [Logging and debugging](../user_guide/index.rst#logging-and-debugging) for
# more details) and includes the following functions:
#
# * `main()`: Instantiates the `MIDataflowIntegration` class, which parses the data passed into this script by Data
#   Flow. Executes the business logic, and resumes the workflow once the business logic has completed.
# * `testing()`: Includes a static payload which can be provided to the business logic in place of real data for testing
#   purposes.
# * `step_logic()`: Contains the actual business logic for the step. Uses the data provided by Data Flow (or defined
#   statically).
#
# Finally, the `if __name__ == "__main__":` block is the entry point for the script. It should be set to call the
# `testing()` function whenever executed outside of Data Flow, but switched to `main()` when added to the workflow
# definition in Data Flow Designer.

# <div class="alert alert-warning">
#
# **Warning:**
#
# The `step_logic()` function generates the dataflow payload, and explicitly calls the `get_payload_as_str()` method
# with `include_credentials=False` to avoid logging credentials to the Data Flow log. If you are using Basic or OIDC
# Authentication and require these credentials for your business logic, you should inject these credentials into the
# `dataflow_payload["AuthorizationHeader"]` value in the `testing()` function directly, for example via an environment
# variable.
# </div>

# ## Additional notes

# This script can be used to generate new Data Flow payloads for testing. Add this script to an existing Data Flow job,
# run the workflow, and the payload will be output to the Data Flow log file. Then copy the payload into a local copy
# of the script, and use that payload when adding functionality to the `step_logic()` function.

# ## Example script

# +
import json
import logging
import traceback

from ansys.grantami.dataflow_toolkit import MIDataflowIntegration

# Create an instance of the root logger
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Add a StreamHandler to write the output to stdout
ch = logging.StreamHandler()
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
ch.setFormatter(formatter)
logger.addHandler(ch)


def main():
    """
    Initializes the Data Flow integration module, runs the business logic,
    and cleans up once execution has completed.
    """

    # It is strongly recommended to use HTTPS in production
    # If you are using an internal certificate, you should specify the
    # CA certificate with certificate_filename=my_cert_file.crt and add the
    # certificate to the workflow as a supporting file, or use an absolute
    # pathlib.Path object to the file on disk.
    dataflow_integration = MIDataflowIntegration(use_https=False)

    try:
        step_logic(dataflow_integration)
        exit_code = 0
    except Exception:
        traceback.print_exc()
        exit_code = 1
    dataflow_integration.resume_bookmark(exit_code)


def testing():
    """Contains a static copy of a Data Flow data payload for testing purposes"""

    dataflow_payload = {
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

    # Call MIDataflowIntegration constructor with "dataflow_payload" argument
    # instead of reading data from Data Flow.
    dataflow_integration = MIDataflowIntegration.from_dict_payload(
        dataflow_payload=dataflow_payload,
        use_https=False,
    )
    step_logic(dataflow_integration)


def step_logic(dataflow_integration):
    """Contains the business logic to be executed as part of the workflow.

    Replace the code in this module with your custom business logic."""

    # Get the poayload from the integration option. Enable indenting
    # to make the result easier to read.
    payload = dataflow_integration.get_payload_as_string(
        indent=True,
        include_credentials=False,
    )

    # Print the payload. This will appear in the Data Flow log.
    data = json.dumps(payload, indent=4)
    logger.info("Writing dataflow payload.")  # This output will be visible in the api/logs page
    logger.info(data)


if __name__ == "__main__":
    # main()  # Used when running the script as part of a workflow
    testing()  # Used when testing the script manually
