"""Sphinx documentation configuration file."""

import datetime
import os
from pathlib import Path
import shutil

from ansys_sphinx_theme import ansys_favicon, get_version_match
import jupytext

from ansys.grantami.dataflow_extensions import __version__

# Project information
project = "ansys-grantami-dataflow_extensions"
now = datetime.datetime.now()
project_copyright = f"(c) {now.year} ANSYS, Inc. All rights reserved"
author = "ANSYS, Inc."
release = version = __version__

# Select desired logo, theme, and declare the html title
html_theme = "ansys_sphinx_theme"
html_short_title = html_title = "PyGranta Data Flow Extensions"
html_favicon = ansys_favicon

cname = os.getenv("DOCUMENTATION_CNAME", "dataflow_extensions.grantami.docs.pyansys.com")
"""The canonical name of the webpage hosting the documentation."""

# specify the location of your github repo
html_theme_options = {
    "github_url": "https://github.com/ansys/grantami-dataflow-extensions",
    "show_prev_next": False,
    "show_breadcrumbs": True,
    "additional_breadcrumbs": [
        ("PyAnsys", "https://docs.pyansys.com/"),
        ("PyGranta", "https://grantami.docs.pyansys.com/"),
    ],
    "switcher": {
        "json_url": f"https://{cname}/versions.json",
        "version_match": get_version_match(__version__),
    },
    "check_switcher": False,
    "logo": "pyansys",
}

# Sphinx extensions
extensions = [
    "numpydoc",
    "sphinx.ext.intersphinx",
    "sphinx_copybutton",
    "sphinx_jinja",
    "nbsphinx",
    "sphinx_design",
    "enum_tools.autoenum",
]

nitpick_ignore_regex = {
    ("py:(class|obj)", r"mi\.Session"),
    ("py:(class|obj)", r"mpy\.Session"),
    ("py:obj", "PyGranta_Connection_Class"),
}

# numpydoc configuration
numpydoc_show_class_members = False
numpydoc_xref_param_type = True
numpydoc_xref_ignore = {"of", "optional", "or", "default"}

# Consider enabling numpydoc validation. See:
# https://numpydoc.readthedocs.io/en/latest/validation.html#
numpydoc_validate = True
numpydoc_validation_checks = {
    "GL06",  # Found unknown section
    "GL07",  # Sections are in the wrong order.
    "GL08",  # The object does not have a docstring
    "GL09",  # Deprecation warning should precede extended summary
    "GL10",  # reST directives {directives} must be followed by two colons
    "SS01",  # No summary found
    "SS02",  # Summary does not start with a capital letter
    # "SS03", # Summary does not end with a period
    "SS04",  # Summary contains heading whitespaces
    # "SS05", # Summary must start with infinitive verb, not third person
    "RT02",  # The first line of the Returns section should contain only the
    # type, unless multiple values are being returned"
}

# sphinx
add_module_names = False

# sphinx.ext.autodoc
autodoc_typehints = "description"  # Remove typehints from signatures in docs
autodoc_typehints_description_target = "documented"
autodoc_member_order = "bysource"

# Intersphinx mapping
intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "openapi-common": ("https://openapi.docs.pyansys.com/version/stable", None),
    "requests": ("https://requests.readthedocs.io/en/latest/", None),
    # kept here as an example
    # "scipy": ("https://docs.scipy.org/doc/scipy/reference", None),
    # "numpy": ("https://numpy.org/devdocs", None),
    # "matplotlib": ("https://matplotlib.org/stable", None),
    # "pandas": ("https://pandas.pydata.org/pandas-docs/stable", None),
    # "pyvista": ("https://docs.pyvista.org/", None),
    # "grpc": ("https://grpc.github.io/grpc/python/", None),
}

# static path
html_static_path = ["_static"]

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# The suffix(es) of source filenames.
source_suffix = ".rst"

# The master toctree document.
master_doc = "index"

# Generate section labels up to four levels deep
autosectionlabel_maxdepth = 4


# -- Examples configuration --------------------------------------------------
def _copy_examples_and_convert_to_notebooks(source_dir, output_dir):
    """
    Recursively copies all files from the source directory to the output directory.

    Creates any necessary subfolders in the process. Python scripts with the ".py" extension
    are also converted to Jupyter notebooks with the ".ipynb" extension using Jupytext.

    Parameters
    ----------
    source_dir : Path
        The source directory to copy files from.
    output_dir : Path
        The output directory to copy files to and convert Python scripts.

    Raises
    ------
    RuntimeError
        If the output directory or any necessary subfolders cannot be created.

    Notes
    -----
    - This function uses pathlib.Path methods for working with file paths.
    - Any existing files in the output directory will be overwritten.
    - If a Python script cannot be converted to a Jupyter notebook, an exception is raised.

    Examples
    --------
    >>> _copy_examples_and_convert_to_notebooks("my_project/examples", "docs/notebooks")

    """
    if not source_dir.exists():
        raise ValueError(f"Source directory {source_dir.name} does not exist.")
    if not output_dir.exists():
        output_dir.mkdir(parents=True)

    for file_source_path in source_dir.rglob("*"):
        if not file_source_path.is_file():
            continue

        rel_path = file_source_path.relative_to(source_dir)
        file_output_path = output_dir / rel_path

        file_output_path.parent.mkdir(parents=True, exist_ok=True)
        print(f"Copying {file_source_path.name}")
        shutil.copy(file_source_path, file_output_path)

        if file_source_path.suffix == ".py":
            try:
                ntbk = jupytext.read(file_source_path)
                jupytext.write(ntbk, file_output_path.with_suffix(".ipynb"))
            except Exception as e:
                raise RuntimeError(f"Failed to convert {file_source_path} to notebook: {e}")


EXAMPLES_SOURCE_DIR = Path(__file__).parent.parent.parent.absolute() / "examples"
EXAMPLES_OUTPUT_DIR = Path(__file__).parent.absolute() / "examples"
ipython_dir = Path("../../.ipython").absolute()
os.environ["IPYTHONDIR"] = str(ipython_dir)

_copy_examples_and_convert_to_notebooks(
    EXAMPLES_SOURCE_DIR,
    EXAMPLES_OUTPUT_DIR,
)

nbsphinx_prolog = """
Download this example as a :download:`Jupyter notebook </{{ env.docname }}.ipynb>` or a
:download:`Python script </{{ env.docname }}.py>`.

----
"""
