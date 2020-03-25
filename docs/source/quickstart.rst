##########
Quickstart
##########

This doc is meant to serve as a quick-guide to setup RISCOF and perform a sample compliance check
between ``spike`` (DUT in this case) and ``riscvOVPsim`` (Golden model in this case).

Install Python Dependencies
===========================

RISCOF requires `pip` and `python` (>=3.7) to be available on your system. If you have issues, instead of
installing either of these directly on your system, we suggest using a virtual environment
like `pyenv` to make things easy.

Installing Pyenv [optional]
---------------------------

If you are working on Ubuntu/Debian systems make sure you have the following libraries installed:

.. code-block:: bash

  $ sudo apt-get install -y make build-essential libssl-dev zlib1g-dev libbz2-dev \
      libreadline-dev libsqlite3-dev wget curl llvm libncurses5-dev libncursesw5-dev \
      xz-utils tk-dev libffi-dev liblzma-dev python-openssl git

Download and install pyenv:

.. code-block:: bash

  $ curl -L https://raw.githubusercontent.com/yyuu/pyenv-installer/master/bin/pyenv-installer | bash

Add the following lines to your .bashrc:

.. code-block:: bash

  $ export PATH="/home/<username>/.pyenv/bin:$PATH"
  $ eval "$(pyenv init -)"
  $ eval "$(pyenv virtualenv-init -)"

Open a new terminal and create a virtual environment using the following

.. code-block:: bash

  $ pyenv install 3.7.0
  $ pyenv virtualenv 3.7.0 riscof_env


Now you can activate this virtual environment using the following command:

.. code-block:: bash

  $ pyenv activate riscof_env
  $ python ==version

Install via PIP [users]
=======================

**NOTE**: If you are using `pyenv` as mentioned above, make sure to enable that environment before
performing the following steps.

.. code-block:: bash

  $ pip install riscv_config

To update an already installed version of RISCOF to the latest version:

.. code-block:: bash

  $ pip install -U riscv_config

To checkout a specific version of riscof:

.. code-block:: bash

  $ pip install riscv_config==1.x.x

Once you have RISCV_CONFIG installed, executing ``riscv_config ==help`` should print the following on the terminal:

.. code-block:: bash

    riscv-config [-h] ==isa_spec YAML ==platform_spec YAML [==verbose]

    RISC-V Configuration Validator 
    
    optional arguments:
      ==isa_spec YAML, -ispec YAML
                            The YAML which contains the ISA specs.
      ==platform_spec YAML, -pspec YAML
                            The YAML which contains the Platfrorm specs.
      ==verbose             debug | info | warning | error
      -h, ==help            show this help message and exit



RISCV_CONFIG for Developers
===========================

Clone the repository from git and install required dependencies. Note, you will still need
python-3.7.0 and pip. If you are using `pyenv` as mentioned above, make sure to enable that environment before
performing the following steps.

.. code-block:: bash

  $ git clone https://github.com/riscv/riscv-config.git
  $ cd riscv_config
  $ pip3 install -r requirements.txt

Executing ``python -m riscv_config.main ==help`` should display the same help message as above.

Usage Example
=============

.. code-block:: bash

    $ riscv_config -ispec examples/rv32i_isa.yaml -pspec examples/rv32i_platform.yaml

Executing the above command should display the following on the terminal:

.. code-block:: bash

  [INFO]    : Input-ISA file
  [INFO]    : Loading input file: /scratch/git-repo/github/riscv-config/examples/rv32i_isa.yaml
  [INFO]    : Load Schema /scratch/git-repo/github/riscv-config/riscv_config/schemas/schema_isa.yaml
  [INFO]    : Initiating Validation
  [INFO]    : No Syntax errors in Input ISA Yaml. :)
  [INFO]    : Initiating post processing and reset value checks.
  [INFO]    : Dumping out Normalized Checked YAML: /scratch/git-repo/github/riscv-config/riscv_config_work/rv32i_isa_checked.yaml
  [INFO]    : Input-Platform file
  [INFO]    : Loading input file: /scratch/git-repo/github/riscv-config/examples/rv32i_platform.yaml
  [INFO]    : Load Schema /scratch/git-repo/github/riscv-config/riscv_config/schemas/schema_platform.yaml
  [INFO]    : Initiating Validation
  [INFO]    : No Syntax errors in Input Platform Yaml. :)
  [INFO]    : Dumping out Normalized Checked YAML: /scratch/git-repo/github/riscv-config/riscv_config_work/rv32i_platform_checked.yaml
  

