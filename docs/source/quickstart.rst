Quickstart
----------

Installation and Setup
^^^^^^^^^^^^^^^^^^^^^^^
1. Install rifle

    Before proceding further please ensure *pip* and *python* is installed and configured.

    You can check the python version by using 
    
    .. code-block:: bash

        python3 --version

    *Support exists for python versions > 3.7.0 only. Please ensure correct version before proceding further.*

    * Install using pip(For users-**WIP**):

    .. code-block:: bash

        pip3 install -r rifle


    * Clone from git(For developers):

    .. code-block:: bash

        git clone https://gitlab.com/incoresemi/rifle.git
        cd rifle
        pip3 install -r requirements.txt

Usage
^^^^^

* For users-**WIP**

.. code-block:: bash

    rifle [-h] --isa_spec YAML --platform_spec YAML [--verbose]

    RISC-V Feature Legalizer
    
    optional arguments:
      --isa_spec YAML, -ispec YAML
                            The YAML which contains the ISA specs.
      --platform_spec YAML, -pspec YAML
                            The YAML which contains the Platfrorm specs.
      --verbose             debug | info | warning | error
      -h, --help            show this help message and exit



* For developers

.. code-block:: bash

    cd rifle/

    python3 -m rifle.main -h
    usage: [-h] --isa_spec YAML --platform_spec YAML [--verbose]

    RISC-V Feature Legalizer

    optional arguments:
      --isa_spec YAML, -ispec YAML
                            The YAML which contains the ISA specs.
      --platform_spec YAML, -pspec YAML
                            The YAML which contains the Platfrorm specs.
      --verbose             debug | info | warning | error
      -h, --help            show this help message and exit



Example
^^^^^^^

    * For users-**WIP**

    .. code-block:: bash

        cd rifle/

        rifle -ispec ./Examples/template_isa.yaml -pspec ./Examples/templates_platform.yaml

    * For developers
    
    .. code-block:: bash

        python3 -m rifle.main -ispec ./Examples/template_isa.yaml -pspec ./Examples/templates_platform.yaml