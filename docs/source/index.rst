
Welcome to RIFLE 
=================


**RIFLE** (RISC-V Feature Leagalizer) is a YAML based framework which can be used to validate the specifications of a RISC-V implementation against the RISC-V privileged and unprivileged ISA spec and generate standard specification yaml file. 

**Caution**: This is still a work in progress and non-backward compatible changes are expected to happen. 

For more information on the official RISC-V spec please visit: `RISC-V Specs <https://riscv.org/specifications/>`_

RIFLE [`Repository <https://gitlab.com/incoresemi/rifle>`_]


Overview
-------------------

The following diagram captures the overall-flow of RIFLE.

.. image:: rifle-flow.png
    :width: 800px
    :align: center
    :height: 500px
    :alt: riscof-flow

The user is required to provide 2 YAML files as input:

1. **ISA Spec**: This YAML file is meant to capture the ISA related features implemented by the user. Details of this input file can be found here : :ref:`isa_yaml_spec`. 
2. **Platform Spec**: This YAML file is meant to capture the platform specific features implemented by the user. Details of this input file can be found here : :ref:`platform_yaml_spec`.

Working:
^^^^^^^^^
The ISA and Platform spec are first checked by the validator for any inconsistencies. Checks like 'F' to exist for 'D' are performed by the validator. The validator exits with an error if any illegal configuration for the spec is provided. Once the validator checks pass, two separate standard yaml files are generated, one for each input type. These standard yaml files contain all fields elaborated and additional info for each node. While the user need not specify all the fields in the input yaml files, the validator will assign defaults to those fields and generate a standard exhaustive yaml for both ISA and Platform spec.

.. toctree::
   :hidden:
   :glob:
   
   quickstart
   yaml-specs
   code-doc

Indices and tables
------------------

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

