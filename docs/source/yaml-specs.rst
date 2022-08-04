###################
YAML Specifications
###################

This section provides details of the ISA and Platform spec YAML files that need to be provided by the user.

.. _isa_yaml_spec:

ISA YAML Spec
=============

**NOTE**:

  1. All integer fields accept values as integers or hexadecimals(can be used interchangeably) unless specified otherwise.
  2. Different examples of the input yamls and the generated checked YAMLs can be found here : `Examples <https://github.com/riscv/riscv-config/tree/master/examples>`_

.. include:: schema_isa.rst

CSR Template
============
All csrs are defined using a common template. Two variants are available: csrs with subfields and
those without

CSRs with sub-fields
--------------------

.. code-block:: yaml

  <name>:                                   # name of the csr
    description: <text>                     # textual description of the csr
    address: <hex>                          # address of the CSR
    priv_mode: <D/M/H/S/U>                  # privilege mode that owns the register
    reset-val: <hex>                        # Reset value of the register. This an accumulation 
                                            # of the all reset values of the sub-fields 
    rv32:                                   # this node and its subsequent fields can exist 
                                            # if [M/S/U]XL value can be 1
      accessible: <boolean>                 # indicates if the csr is accessible in rv32 mode or not. 
                                            # When False, all fields below will be trimmed off 
                                            # in the checked yaml. False also indicates that 
                                            # access-exception should be generated. 
      fields:                               # a quick summary of the list of all fields of the 
                                            # csr including a list of WPRI fields of the csr.
        - <field_name1>
        - <field_name2>
        - - [23,30]                         # A list which contains a squashed pair 
          - 6                               # (of form [lsb,msb]) of all WPRI bits within the 
                                            # csr. Does not exist if there are no WPRI bits
  
      <field_name1>:                        # name of the field
        description: <text>                 # textual description of the csr
        shadow: <csr-name>::<field>         # which this field shadows,'none' indicates that
                                            # this field does not shadow anything.
        msb: <integer>                      # msb index of the field. max: 31, min:0
        lsb: <integer>                      # lsb index of the field. max: 31, min:0
        implemented: <boolean>              # indicates if the user has implemented this field 
                                            # or not. When False, all 
                                            # fields below this will be trimmed.
        type:                               # type of field. Can be only one of the following
          wlrl: [list of value-descriptors] # field is wlrl and the set of legal values.
          ro_constant: <hex>                # field is readonly and will return the same value.
          ro_variable: True                 # field is readonly but the value returned depends 
                                            # on other arch-states
          warl:                             # field is warl type. Refer to WARL section
            dependency_fields: [list]    
            legal: [list of warl-string]
            wr_illegal: [list of warl-string]           
    rv64:                                   # this node and its subsequent fields can exist 
                                            # if [M/S/U]XL value can be 2
      accessible: <boolean>                 # indicates if this register exists in rv64 mode 
                                            # or not. Same definition as for rv32 node.
    rv128:                                  # this node and its subsequent fields can exist if 
                                            # [M/S/U]XL value can be 3
      accessible: <boolean>                 # indicates if this register exists in rv128 mode 
                                            # or not. Same definition as for rv32 node.                          

CSRs without sub-fields
-----------------------

.. code-block:: yaml

  <name>:                                 # name of the csr
    description: <text>                   # textual description of the csr
    address: <hex>                        # address of the CSR
    priv_mode: <D/M/H/S/U>                # privilege mode that owns the register
    reset-val: <hex>                      # Reset value of the register. This an accumulation 
                                          # of the all reset values of the sub-fields 
    rv32:                                 # this node and its subsequent fields can exist 
                                          # if [M/S/U]XL value can be 1
      accessible: <boolean>               # indicates if the csr is accessible in rv32 mode or not. 
                                          # When False, all fields below will be trimmed off 
                                          # in the checked yaml. False also indicates that 
                                          # access-exception should be generated
      fields: []                          # This should be empty always.
      shadow: <csr-name>::<register>      # which this register shadows,'none' indicates that 
                                          # this register does not shadow anything.
      msb: <int>                          # msb index of the csr. max: 31, min:0
      lsb: <int>                          # lsb index of the csr. max: 31, min:0
      type:                               # type of field. Can be only one of the following
        wlrl: [list of value-descriptors] # field is wlrl and the set of legal values.
        ro_constant: <hex>                # field is readonly and will return the same value.
        ro_variable: True                 # field is readonly but the value returned depends 
                                          # on other arch-states
        warl:                             # field is warl type. Refer to WARL section
          dependency_fields: [list]    
          legal: [list of warl-string]
          wr_illegal: [list of warl-string]           
    rv64:                                 # this node and its subsequent fields can exist 
                                          # if [M/S/U]XL value can be 2
      accessible: <boolean>               # indicates if this register exists in rv64 mode 
                                          # or not. Same definition as for rv32 node.
    rv128:                                # this node and its subsequent fields can exist if 
                                          # [M/S/U]XL value can be 3
      accessible: <boolean>              # indicates if this register exists in rv128 mode 

Indexed CSRs
------------

.. code-block:: yaml

  <name>:                                 # name of the csr
    description: <text>                   # textual description of the csr
    address: <hex>                        # address of the CSR
    priv_mode: <D/M/H/S/U>                # privilege mode that owns the register
    rv32:                                 # this node and its subsequent fields can exist 
                                          # if [M/S/U]XL value can be 1
      accessible: <boolean>               # indicates if the csr is accessible in rv32 mode or not. 
                                          # When False, all fields below will be trimmed off 
                                          # in the checked yaml. False also indicates that 
                                          # access-exception should be generated
      indexing_reg: <csr-name>            # which csr is being used as index for this register.
                                          # Cannot be none.
      index_list:                         # list of dictionaries, containing the details of possible
                                          # indexing_reg values
        - index_val: <hex/int>            # value of the indexing_reg that indicates this index is
                                          # to be chosen
          msb: <integer>                  # msb index of the field. max- 31, min-0
          lsb: <integer>                  # lsb index of the field. max- 31, min-0
          reset-val: <hex>                # Reset value of this indexed register. 
          fields: []                      # This should be empty always.
          shadow: <csr-name>::<register>  # which this register shadows,'none' indicates that 
                                          # this register does not shadow anything.
          type:                           # type of field. Can be only one of the following
            wlrl:                         # same as previous wlrl definition above
            ro_constant: <hex>            # same as previous ro_constant definition above  
            ro_variable: True             # same as previous ro_variable definition above 
            warl:                         # same as previous warl definition above 
        - index_val: <hex/int>            # The next entry in the list for indexed registers having
                                          # the same fields as described above
          ...                             #
    rv64:                                 # this node and its subsequent fields can exist 
                                          # if [M/S/U]XL value can be 2
      accessible: <boolean>               # indicates if this register exists in rv64 mode 
                                          # or not. Same definition as for rv32 node.
    rv128:                                # this node and its subsequent fields can exist if 
                                          # [M/S/U]XL value can be 3
      accessible: <boolean>              # indicates if this register exists in rv128 mode 

Constraints
-----------

Each CSR undergoes the following checks:

  1. All implemented fields at the csr-level, if set to True, are checked if
     they comply with the supported_xlen field of the ISA yaml.
  2. The reset-val is checked against compliance with the type field specified
     by the user. All unimplemented fields are considered to be hardwired to 0.

In addition to the above, the Indexed-CSRs undergo the following checks:
  
  1. The CSR mentioned in the `indexing_reg` is indeed implemented and accessible.
  2. The index values (i.e. `index_val` under the index_list are indeed legal values for the csr
     mentioned in the `indexing_reg` field.

For each of the above templates the following fields for all standard CSRs
defined by the spec are frozen and **CANNOT** be modified by the user.

* description
* address
* priv_mode
* fields
* shadow
* msb
* lsb
* The type field for certain CSRs (like readonly) is also constrained.
* fields names also cannot be modified for standard CSRs

Only the following fields can be modified by the user:

* reset-value
* type
* implemented

Example of CSR with sub-fields
------------------------------

Following is an example of how a user can define the mtvec csr in the input ISA YAML for a 
32-bit core:

.. code-block:: yaml

  mtvec:
  reset-val: 0x80010000
  rv32:
    accessible: true
    base:
      implemented: true
      type:                             
        warl: 
          dependency_fields: [mtvec::mode]
          legal:
            - "mode[1:0] in [0] -> base[29:0] in [0x20000000, 0x20004000]"             # can take only 2 fixed values in direct mode.
            - "mode[1:0] in [1] -> base[29:6] in [0x000000:0xF00000] base[5:0] in [0x00]" # 256 byte aligned values only in vectored mode.
          wr_illegal:
            - "mode[1:0] in [0] -> Unchanged"
            - "mode[1:0] in [1] and wr_val in [0x2000000:0x4000000] -> 0x2000000"
            - "mode[1:0] in [1] and wr_val in [0x4000001:0x3FFFFFFF] -> Unchanged"
    mode:
      implemented: true
      type:                             
        warl:
          dependency_fields: []
          legal: 
            - "mode[1:0] in [0x0:0x1] # Range of 0 to 1 (inclusive)"
          wr_illegal:
            - "Unchanged"

The following is what the riscv-config will output after performing relevant checks on the 
above user-input:

.. code-block:: yaml

    mtvec:
      description: MXLEN-bit read/write register that holds trap vector configuration.
      address: 773
      priv_mode: M
      reset-val: 0x80010000
      rv32:
        accessible: true
        base:
          implemented: true
          type:
            warl:
              dependency_fields: [mtvec::mode]
              legal:
              - 'mode[1:0] in [0] -> base[29:0] in [0x20000000, 0x20004000]'               # can take only 2 fixed values in direct mode.
              - 'mode[1:0] in [1] -> base[29:6] in [0x000000:0xF00000] base[5:0] in [0x00]'   # 256 byte aligned values only in vectored mode.
              wr_illegal:
              - 'mode[1:0] in [0] -> Unchanged'
              - 'mode[1:0] in [1] and wr_val in [0x2000000:0x4000000] -> 0x2000000'
              - 'mode[1:0] in [1] and wr_val in [0x4000001:0x3FFFFFFF] -> Unchanged'
          description: Vector base address.
          shadow: none
          msb: 31
          lsb: 2
        mode:
          implemented: true
          type:
            warl:
              dependency_fields: []
              legal:
              - 'mode[1:0] in [0x0:0x1] # Range of 0 to 1 (inclusive)'
              wr_illegal:
              - Unchanged
    
          description: Vector mode.
          shadow: none
          msb: 1
          lsb: 0
        fields:
        - mode
        - base 
      rv64:
        accessible: false

Example of an Indexed CSR
-------------------------

.. code-block:: yaml

   tdata1:
      rv32:
        accessible: true
        indexing_reg: tselect
        index_list:
          - index_val: 0 # this trigger is always disabled.
            fields: []
            shadow:
            shadow_type: 
            msb: 31
            lsb: 0
            type:
              ro_constant: 0x0 
            reset-val: 0x0
          - index_val: 1  # this trigger is either disabled or an icount trigger.
            reset-val: 0x400 # count reset value is 1 by the spec.
            fields: []
            shadow_type:
            shadow:
            msb: 31
            lsb: 0
            type:
              warl:
                dependency_fields: [tdata1::indexval_1]
                legal: 
                  - indexval_1[31:28] in [0, 3] -> indexval_1[26:0] in [0x0:0x7ffffff]
                wr_illegal:
                  - Unchanged
          - index_val: 2  # this trigger is either disabled or an icount or an itrigger.
            fields: []
            shadow_type:
            shadow:
            msb: 31
            lsb: 0
            type:
              warl:
                dependency_fields: [tdata1::indexval_2]
                legal: 
                  - indexval_2[31:28] in [0, 3] -> indexval_2[26:0] in [0x0:0x7ffffff]
                  - indexval_2[31:28] in [4] -> indexval_2[12:0] in [0x0:0x1fff] indexval_2[25:13] in [0] indexval_2[26] in [0,1]
                wr_illegal:
                  - Unchanged


WARL field Definition
=====================

Since the RISC-V privilege spec indicates several CSRs and sub-fields of CSRs to be WARL (Write-Any-Read-Legal), 
it is necessary to provide a common scheme of representation which can precisely 
define the functionality of any such WARL field/register. 


Value Descriptors
-----------------

This is a list which describes a set of values. Each entry can either represent a single distinct value or a range of values. 

* **distinct-values** - This specifies that only the particular value should be added to the set.
    
  .. code-block:: python
      
    val
    
* **range** - This specifies that all the values greater than or equal to lower and less than or equal to upper is to be included in the set.
       
  .. code-block:: python
       
    lower:upper
    
Example:
     
.. code-block:: python

  # To represent the set {0, 1, 2, 3, 4, 5}
    [0:5]

  # To represent the set {5, 10, 31}
    [5, 10, 31]

  # To represent the set {2, 3, 4, 5, 10}
    [2:5, 10]
      
WARL Node definition
--------------------

A WARL csr/field has the following skeleton in the riscv-config:

.. code-block:: yaml

   WARL:   
      dependency_fields: [list]
      legal: [list of warl-string]
      wr_illegal: [list of warl-string]

- **dependency_fields** : A list of other csrs/fields whose values define the set of legal values the 
  csr/field under question can take. We use ``::`` as a hierarchy separator. This field can be empty as well indicating 
  no other state affects this csr/field. The fields within csrs can be specified as follows:

  ..  code-block:: yaml

      - dependency_fields: [mtvec::mode]
      - dependency_fields: [misa::mxl, mepc]
    

- **legal** : This field takes in a list of strings which define the WARL functions. Each string needs to adhere to the
  following syntax:

  .. code-block:: yaml

    - [dependency-vals] -> field-name[index-hi:index-lo] in [legal-values]
    - [dependency-vals] -> field-name[index-hi:index-lo] bitmask [mask, fixedval]
    
    # if no dependency_fields exists then following is also allowed:
    
    field-name[index-hi:index-lo] bitmask [mask, fixedval]
    
  In short it means that under certain values of the dependency_fields the warl-field can take only the legal values 
  defined by either `[legal-values]` or by the `bitmask` function. 
  
  - **dependency-vals** : A comma separated list of value-descriptors indicating the values the corresponding fields in the
    dependency_fields take. 

  - **->**: represents "imply".
  
  - **field-name**: should be the same as the csr/field-name for which this WARL function is being described.
  
  - **index-**: These are unsigned integers not exceeding the size of field. Sometimes it easier to define the WARL 
    function by splitting the fields. Thus the following is also a legal form:
    
    .. code-block:: yaml
    
      [dependency-vals] -> field-name[index-hi:index-lo] in [legal-values1] & field-name[index-lo-1:0] in [legal-values2]
    
  - **in**: key-word indicating that `field-name[index-hi:index-lo]` should takes values defined within `[legal_values]`.

  - **bitmask**: keyword indicating that the legal values are defined using a mask and fixedval variables. The fixedval variable defines the default value of the masked bits.

  - **legal-values**: a list of value-descriptors indicating the set of legal values `field-name[index-hi:index-lo]` can 
    take.
    
    **Restrictions**:
    
    1. No legal value must exceed the maximum value which can be supported (based on the width of the field). 
    2. Functions should be exhaustive with respect to every possible combination of the dependency values.
    3. within a string for `legal` all bits of the csr/field should be covered. No bits must be left undefined.
    4. A legal string should be a combination of ranges split into parts or a simple bitmask function for the entire field. Mixing bitmask and ranges is not allowed. The following example is an invalid spec:

    .. code-block:: yaml

      [0] -> field[31:6] in [0x10000000: 0x3FFFFFF] & field[5:0] bitmask [0x30, 0x0F]
  
  
- **wr_illegal** : This field takes in a list of strings which define the next legal value of the field when an illegal
  value is written. Each string needs to adhere to the following syntax:

  .. code-block:: yaml

      [dependency-vals] wr_val in [illegal-values] -> update_mode
                          OR
      [dependency-vals] -> update_mode

  In short this means that under certain values of the dependency_fields when an illegal write happens (either defined by 
  the wr_val or for all illegal values) the next legal value is defined by the `update_mode`.

  - **dependency-vals** : A comma separated list of value-descriptors indicating the values the corresponding fields in the
    dependency_fields take. 
    
  - **wr_val**: key-word indicating the illegal write-value

  - **in**: same meaning as the before.
  
  - **illegal-values**: a list of value-descriptors indicating the set of illegal values for the csr/field under question.
  
  - **update_mode** : This field dictates what the next legal read value is when an illegal write happens:

      - **unchanged**: The value remains unchanged to the current legal value.
      - **<val>**: A single value can also be specified
      - **nextup**: ceiling(*wr_val*) i.e. the next larger or the largest element of the legal list
      - **nextdown**: floor(*wr_val*) i.e. the next smallest or the smallest element of the legal list
      - **nearup**: celing(*wr_val*) i.e. the closest element in the list, with the larger element being chosen in case of a tie.
      - **neardown**: floor(*wr_val*) i.e. the closes element in the list, with the smaller element being chosen in case of a tie
      - **max**: maximum of all legal values
      - **min**: minimum of all legal values
      - **addr**: 

        .. code-block:: python

          if ( val < base || val > bound)
              return Flip-MSB of field

    **Restrictions**:
      
      1. wr_illegal will not exists for a legal list defined as a bitmask.



Example:
  
.. code-block:: yaml

    # When base of mtvec depends on the mode field.
    WARL: 
      dependency_fields: [mtvec::mode]
      legal:
        - "[0] -> base[29:0] in [0x20000000, 0x20004000]"  # can take only 2 fixed values when mode==0.
        - "[1] -> base[29:6] in [0x000000:0xF00000] base[5:0] in [0x00]" # 256 byte aligned when mode==1
      wr_illegal:
        - "[0] -> unchanged"
        - "[1] wr_val in [0x2000000:0x4000000] -> 0x2000000" # predefined value if write value is
        - "[1] wr_val in [0x4000001:0x3FFFFFFF] -> unchanged"

    # When base of mtvec depends on the mode field. Using bitmask instead of range
    WARL: 
      dependency_fields: [mtvec::mode]
      legal:
        - "[0] -> base[29:0] in [0x20000000, 0x20004000]"  # can take only 2 fixed values when mode==0.
        - "[1] -> base[29:0] bitmask [0x3FFFFFC0, 0x00000000]" # 256 byte aligned when mode==1
      wr_illegal:
        - "[0] -> unchanged" # no illegal for bitmask defined legal strings.
        

    # no dependencies. Mode field of mtvec can take only 2 legal values using range-descriptor
    WARL:
      dependency_fields:
      legal: 
        - "mode[1:0] in [0x0:0x1] # Range of 0 to 1 (inclusive)"
      wr_illegal:
        - "0x00"

    # no dependencies. using single-value-descriptors
    WARL:
      dependency_fields:
      legal: 
        - "mode[1:0] in [0x0,0x1] # Range of 0 to 1 (inclusive)"
      wr_illegal:
        - "0x00"

.. _platform_yaml_spec:

Platform YAML Spec
==================

This section describes each node of the PLATFORM-YAML. For each node, we have identified the fields required from the user and also the various constraints involved.

.. include:: schema_platform.rst

Debug YAML Spec
===============

.. include:: schema_debug.rst
