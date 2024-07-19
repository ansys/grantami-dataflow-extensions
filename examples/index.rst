.. _ref_grantami_jobqueue_examples:

Examples
========

The following examples demonstrate key aspects of Granta MI Data Flow Toolkit.

To run these examples, install dependencies with this command:

.. code::

   pip install ansys-grantami-dataflow-toolkit[examples]

.. jinja:: examples

    {% if build_examples %}

    .. toctree::
       :maxdepth: 2

       1_Standalone
       2_Scripting_Toolkit

    {% else %}

    .. toctree::
       :maxdepth: 2

       test_example

    {% endif %}
