# Copyright (C) 2024 ANSYS, Inc. and/or its affiliates.
# SPDX-License-Identifier: MIT
#
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""
MI Data Flow Toolkit module.

Provides generic functionality for parsing step information provided by Data Flow.
Allows direct access to this data or supports spawning a Scripting Toolkit session.
"""

import base64
import json
import logging
from pathlib import Path
import sys
from typing import Any, Literal, cast
from urllib.parse import urlparse

import requests  # type: ignore[import-untyped]
from requests_negotiate_sspi import HttpNegotiateAuth  # type: ignore[import-untyped]

try:
    from GRANTA_MIScriptingToolkit import granta as mpy  # type: ignore
except ImportError:
    pass


def _get_data_flow_logger(logger_level: int) -> logging.Logger:
    r"""
    Return a logger with an attached StreamHandler.

    Parameters
    ----------
    logger_level : int
        The level to use for the logger. See the documentation in the Python logging
        module for more details.

    Returns
    -------
    logging.Logger
        The logger with attached StreamHandler.

    Notes
    -----
    The StreamHandler is selected because it outputs the log to stdout. This means the
    log can be accessed in the following locations:

    - The console, when running in a testing mode
    - The Data Flow server: C:\windows\TEMP\{}\__stdout__
    - The Data Flow API, at http://my.server.name/mi_dataflow/api/logs (MI 2023R2+) or
       http://my.server.name/mi_workflow_2/api/logs (MI 2023R1 or earlier)
    """
    logger = logging.getLogger("MIDataFlowIntegration")
    logger.level = logger_level
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    if not bool(logger.handlers):
        ch = logging.StreamHandler()
        ch.setLevel(logger_level)
        ch.setFormatter(formatter)
        ch.setStream(sys.stdout)
        logger.addHandler(ch)
    return logger


class MIDataflowIntegration:
    """
    Represents a MI Data Flow session.

    When this class is instantiated, it parses the data provided by Data Flow, enabling Granta MI API client sessions
    to be created.

    Parameters
    ----------
    logging_level : int
        The logging level to apply to the logger.
    certificate_filename : str
        The filename of the CA certificate file. Generally required for HTTPS connections to
        internal resources.

    Notes
    -----
    When a workflow is configured to call a Python script, the workflow execution will be suspended whilst the Python
    script executes. To enable the workflow to continue, call the ``resume_bookmark`` method.
    """

    def __init__(self, logging_level: int = logging.DEBUG, certificate_filename: str = "") -> None:

        # Define properties:
        self._logging_level = logging_level
        self._certificate_filename = certificate_filename
        self._mi_session: mpy.Session | None = None

        # Logger
        self.logger = _get_data_flow_logger(self._logging_level)

        self.logger.debug("")
        self.logger.debug("---------- NEW RUN ----------")

        # Retrieve configuration data:
        if self._certificate_filename:
            self.logger.debug("Getting certificate data...")
            self.logger.debug(f"Certificate filename is '{self._certificate_filename}'")

        # Get data from workflow
        self.logger.debug("Getting data from dataflow API...")
        # self.df_data = self._get_standard_input()
        self.df_data = {
            "WorkflowUrl": "http://localhost/mi_dataflow",
            "ClientCredentialType": "Windows",
        }
        self.logger.debug(f"Workflow data received: {json.dumps(self.df_data)}")

        # Parse url
        self.logger.debug("Parsing url...")
        url = self.df_data["WorkflowUrl"]
        parsed_url = urlparse(url)
        self.service_layer_url = f"{parsed_url.scheme}://{parsed_url.netloc}/mi_servicelayer/"
        self.logger.debug(f"Service layer url: {self.service_layer_url}")

        # TODO: Add support for PyGranta sessions

    @property
    def mi_session(self) -> "mpy.Session":
        """
        An MI Scripting Toolkit session which can be used to interact with Granta MI.

        Requires a supported version of MI Scripting Toolkit to be installed.

        Returns
        -------
        mpy.Session
            MI Scripting Toolkit session.

        Raises
        ------
        MissingClientModule
            If Scripting Toolkit cannot be imported.
        """
        if self._mi_session is not None:
            return self._mi_session
        try:
            self._mi_session = self._start_stk_session_from_dataflow_credentials()
        except NameError as e:
            raise MissingClientModule(
                "Could not find Scripting Toolkit. Ensure Scripting Toolkit is installed "
                "and try again."
            ) from e
        return self._mi_session

    def _start_stk_session_from_dataflow_credentials(self) -> "mpy.Session":
        """
        Create a Scripting Toolkit session based on the Data Flow authentication.

        The credentials provided by Data Flow are re-used, and so explicit credentials are
        not required.

        Returns
        -------
        mpy.Session
            A Scripting Toolkit session object.
        """
        self.logger.debug("Starting MI STK session...")
        if self.df_data["ClientCredentialType"] == "Basic":
            # MI server setup: Basic authentication
            self.logger.debug("Basic auth selected...")
            auth_header = self.df_data["AuthorizationHeader"]
            decoded = base64.b64decode(auth_header[6:])
            index = decoded.find(b":")
            session = mpy.connect(
                self.service_layer_url,
                decoded[:index].decode(encoding="utf-8"),
                decoded[index + 1 :].decode(encoding="utf-8"),
                "",
            )

        elif self.df_data["ClientCredentialType"] == "None":
            # MI server setup: OIDC authentication
            self.logger.debug("OIDC auth selected...")
            auth_header = self.df_data["AuthorizationHeader"]
            access_token = auth_header[7:]
            session = mpy.connect(self.service_layer_url, oidc=True, auth_token=access_token)

        else:
            # MI server setup: Windows authentication
            self.logger.debug("Windows auth selected...")
            session = mpy.connect(self.service_layer_url, autologon=True)

        return session

    def _get_standard_input(self) -> dict[str, Any]:
        """
        Parse the data payload from Data Flow to a dictionary.

        Returns
        -------
        dict[str, Any]
            The parsed payload from Data Flow.
        """
        return cast(dict[str, Any], json.load(sys.stdin))

    def _get_workflow_id(self, data: dict[str, Any]) -> str:
        """
        Extract the workflow ID from the parsed data payload.

        Parameters
        ----------
        data : dict[str, Any]
            The parsed payload from Data Flow.

        Returns
        -------
        str
            The workflow ID.
        """
        return cast(str, data["WorkflowId"])

    def resume_bookmark(self, exit_code: str | int) -> None:
        """
        Call the Dataflow API to allow the MI Data Flow step to continue.

        Parameters
        ----------
        exit_code : str | int
            An exit code to inform Dataflow of success or otherwise of the business logic script.
        """
        self.logger.debug(f"Returning control to MI Data Flow with exit code:{exit_code}")
        headers = {"Content-Type": "application/json"}
        response_data = json.dumps(
            {
                "Values": {"ExitCode": exit_code},
                "WorkflowDefinitionName": self.df_data["WorkflowDefinitionId"],
                "TransitionName": self.df_data["TransitionName"],
            }
        ).encode("utf-8")

        verify_argument: Path | Literal[False]
        # Get path to certificate if one has been provided.
        if self._certificate_filename:
            verify_argument = Path(__file__).parent / self._certificate_filename
        else:
            # We have no certificate for verification, so cannot verify.
            verify_argument = False

        if verify_argument:
            dataflow_url = self.df_data["WorkflowUrl"]
        else:
            dataflow_url = f"http://localhost{urlparse(self.df_data['WorkflowUrl']).path}"
        self.logger.debug(f"Resuming bookmark using URL {dataflow_url}")

        if (
            self.df_data["ClientCredentialType"] == "Basic"
            or self.df_data["ClientCredentialType"] == "None"
        ):
            # MI server setup: Basic authentication or OIDC authentication
            headers["Authorization"] = self.df_data["AuthorizationHeader"]
            response = requests.post(
                url=f"{dataflow_url}/api/workflows/{self._get_workflow_id(self.df_data)}",
                data=response_data,
                headers=headers,
                verify=verify_argument,
            )
        else:
            # MI server setup: Windows authentication
            response = requests.post(
                url=f"{dataflow_url}/api/workflows/{self._get_workflow_id(self.df_data)}",
                data=response_data,
                auth=HttpNegotiateAuth(),
                headers=headers,
                verify=verify_argument,
            )
        response.raise_for_status()


class MissingClientModule(ImportError):
    """Raised when a client API module is expected but could not be imported."""

    pass
