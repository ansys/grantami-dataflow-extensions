|pyansys| |python| |pypi| |GH-CI| |codecov| |MIT| |ruff|

.. |pyansys| image:: https://img.shields.io/badge/Py-Ansys-ffc107.svg?labelColor=black&logo=data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAIAAACQkWg2AAABDklEQVQ4jWNgoDfg5mD8vE7q/3bpVyskbW0sMRUwofHD7Dh5OBkZGBgW7/3W2tZpa2tLQEOyOzeEsfumlK2tbVpaGj4N6jIs1lpsDAwMJ278sveMY2BgCA0NFRISwqkhyQ1q/Nyd3zg4OBgYGNjZ2ePi4rB5loGBhZnhxTLJ/9ulv26Q4uVk1NXV/f///////69du4Zdg78lx//t0v+3S88rFISInD59GqIH2esIJ8G9O2/XVwhjzpw5EAam1xkkBJn/bJX+v1365hxxuCAfH9+3b9/+////48cPuNehNsS7cDEzMTAwMMzb+Q2u4dOnT2vWrMHu9ZtzxP9vl/69RVpCkBlZ3N7enoDXBwEAAA+YYitOilMVAAAAAElFTkSuQmCC
   :target: https://docs.pyansys.com/
   :alt: PyAnsys

.. |python| image:: https://img.shields.io/pypi/pyversions/ansys-grantami-dataflow-toolkit?logo=pypi
   :target: https://pypi.org/project/ansys-grantami-dataflow-toolkit/
   :alt: Python

.. |pypi| image:: https://img.shields.io/pypi/v/ansys-grantami-dataflow-toolkit.svg?logo=python&logoColor=white
   :target: https://pypi.org/project/ansys-grantami-dataflow-toolkit
   :alt: PyPI

.. |codecov| image:: https://codecov.io/gh/ansys/grantami-dataflow-toolkit/branch/main/graph/badge.svg
   :target: https://codecov.io/gh/ansys/grantami-dataflow-toolkit
   :alt: Codecov

.. |GH-CI| image:: https://github.com/ansys/grantami-dataflow-toolkit/actions/workflows/ci_cd.yml/badge.svg
   :target: https://github.com/ansys/grantami-dataflow-toolkit/actions/workflows/ci_cd.yml
   :alt: GH-CI

.. |MIT| image:: https://img.shields.io/badge/License-MIT-yellow.svg
   :target: https://opensource.org/licenses/MIT
   :alt: MIT

.. |ruff| image:: https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json
   :target: https://github.com/astral-sh/ruff
   :alt: Ruff

PyGranta Data Flow Toolkit
==========================

..
   _after-badges


PyGranta Data Flow Toolkit provides easy interoperability between Granta MI Data Flow and Python scripts that implement
custom business logic. This package streamlines the interaction with Granta MI using other PyGranta packages and with
Granta MI Scripting Toolkit.


Dependencies
------------
.. readme_software_requirements

To use PyGranta Data Flow Toolkit, you must have access to a Granta MI 2023 R2 deployment or later. Additionally, you
must have an MI Data Flow Advanced edition license to be able to use Python scripts with Data Flow.

Python must be installed system-wide, as opposed to a per-user installation. This option is available during
installation, and can only be modified by uninstalling and reinstalling Python.

.. readme_software_requirements_end


Installation
------------
.. readme_installation


System-wide
~~~~~~~~~~~

This package should be installed system-wide on the Data Flow server for production or for integration testing. To
install the latest PyGranta Data Flow Toolkit release from
`PyPI <https://pypi.org/project/ansys-grantami-dataflow-toolkit/>`_ as a system-wide package, run this command as an
administrator::

   python -m pip install ansys-grantami-dataflow-toolkit

.. note::

   To install packages into the system-wide Python installation directly, you **must** run the preceding command with
   administrator rights. Otherwise, ``pip install`` will install the package for the current user only and will
   display the warning:

      Defaulting to user installation because normal site-packages is not writeable

   A common symptom of this issue is a script that works when testing outside of Data Flow, but fails with an import
   error when running from within Data Flow.

   There are three options to address this issue:

   - Re-run the command above as a user with administrator privileges. This will ensure the package is installed
     system-wide.
   - Run the command ``python -m pip install --user ansys-grantami-dataflow-toolkit`` as the same user that runs MI Data
     Flow. This will install the package such that the Data Flow user can access it, and will suppress the user
     installation warning.
   - Follow the instructions in the Virtual environment to use a `Virtual environment`_.

Virtual environment
~~~~~~~~~~~~~~~~~~~

This package should be installed in a virtual environment in the following situations:

* On a local development environment, for script development and debugging separate to Data Flow
* On the Data Flow server, when it is not possible to install system-wide packages

To install the package in a virtual environment, first create a new virtual environment::

   python -m venv C:\path\to\my\venv

Where ``C:\path\to\my\venv`` is the path to the location where you would like the venv to be located. This should be a
location that all users can access.

Then activate the virtual environment and install the packages::

   C:\path\to\my\venv\Scripts\activate
   pip install ansys-grantami-dataflow-toolkit

If installing in a virtual environment on the Data Flow server, Data Flow must be configured with details of the
virtual environment to be used:

#. Create a backup copy of the ``web.config`` file. By default, this file is located at
   ``C:\inetpub\wwwroot\mi_dataflow``.
#. Open the ``web.config`` file in a text editor, and find the line ``<add key="PythonPath" value="python.exe" />``
#. Replace the string ``python.exe`` with ``C:\path\to\my\venv\Scripts\python.exe``, where ``C:\path\to\my\venv`` is the
   path to the virtual environment specified above.
#. Save the modified ``web.config`` file. If you see a permissions error, you may need to open the text editor with
   administrator privileges.
#. Reload the Data Flow worker process in IIS Manager. Warning: This stops any actively running Workflow processes.

Installing a development version
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To install the latest release from the
`PyGranta Data Flow Toolkit repository <https://github.com/ansys/grantami-dataflow-toolkit>`_, run this command::

   python -m pip install git+https://github.com/ansys/grantami-dataflow-toolkit.git

To install a local *development* version with Git and Poetry, run these commands::

   git clone https://github.com/ansys/grantami-dataflow-toolkit
   cd grantami-dataflow-toolkit
   poetry install

The preceding commands install the package in development mode so that you can modify
it locally. Your changes are reflected in your Python setup after restarting the Python kernel.
This option should only be used when making changes to this package, and should not be used
when developing code based on this package.

.. readme_installation_end
