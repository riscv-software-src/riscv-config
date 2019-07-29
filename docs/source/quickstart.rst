##########
Quickstart
##########

Installation and Setup
^^^^^^^^^^^^^^^^^^^^^^^
1. Install rifle

    Before proceding further please ensure *pip* and *python (>3.7.0)* is installed and configured.

    In case you have issues installing python-3.7, we recommend using `pyenv`. 
    
    Installing instructions for pyenv:

    .. code-block:: bash

        #!/bin/sh
        curl -L https://raw.githubusercontent.com/yyuu/pyenv-installer/master/bin/pyenv-installer | bash
        echo "export PATH=\"/home/$USER/.pyenv/bin:$PATH\"" >> ~/.bashrc
        pyenv install 3.7.0
        pyenv global 3.7.0
        pip install --upgrade pip
        
    You can simply use pip and python for 3.7 by default.

    *Support exists for python versions > 3.7.0 only. Please ensure correct version before proceding further.*

    * Install using pip(For users):

    .. code-block:: bash

        pip3 install rifle


    * Clone from git(For developers):

    .. code-block:: bash

        git clone https://gitlab.com/incoresemi/rifle.git
        cd rifle
        pip3 install -r requirements.txt

Usage
^^^^^

* For users

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

    * For users

    .. code-block:: bash

        git clone https://gitlab.com/incoresemi/rifle.git

        cd rifle/

        rifle -ispec ./examples/template_isa.yaml -pspec ./examples/template_platform.yaml

    * For developers
    
    .. code-block:: bash

        cd rifle/

        python3 -m rifle.main -ispec ./examples/template_isa.yaml -pspec ./examples/template_platform.yaml
