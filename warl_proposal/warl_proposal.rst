###################
WARL field Proposal
###################

Since the RISC-V privilege spec indicates several CSRs and sub-fields of CSRs to be WARL (Write-Any-Read-Legal), 
it is necessary to provide a common scheme of representation which can precisely 
define the functionality of any such WARL field/register. 

This document provides a proposal for one such scheme.

**Authors**: Allen, Pawan, Neel


Value Descriptors
=================

This is a list which describes a set of values. Each entry can either represent a single distinct value or a range of values. 

- *distinct-values* - This specifies that only the particular value should be added to the set.
    
  .. code-block:: python
      
    val
    
- *range* - This specifies that all the values greater than or equal to lower and less than or equal to upper is to be included in the set.
       
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
      
YAML WARL Node definition (*warl*)
=================================

A WARL csr/field has the following skeleton in the riscv-config:

.. code-block:: yaml

   WARL:   
      dependency_fields: [list]
      legal: [list of warl-string]
      wr_illegal: [list of warl-string]

- **dependency_fields** : A list of other csrs/fields whose values define the set of legal values the 
  csr/field under question can take. We use `::` as a hierarchy separator. This field can be empty as well indicating 
  no other state affects this csr/field. The fields within csrs can be specified as follows:

  ..  code-block:: yaml

    dependency_fields: [mtvec::mode]
                 OR 
    dependency_fields: [misa::mxl, mepc]
    

- **legal** : This field takes in a list of strings which define the WARL functions. Each string needs to adhere to the
  following syntax:

  .. code-block:: yaml

    [dependency-vals] -> field-name[index-hi:index-lo] in [legal-values]
    
                                  OR
    
    [dependency-vals] -> field-name[index-hi:index-lo] bitmask [mask, fixedval]
    
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

Restrictions on the WARL YAML node:

    1. No legal value must exceed the maximum value which can be supported(based on the width of the field). 
    2. Functions should be exhaustive with respect to every possible combination of the dependency values.
    3. within a string for `legal` all bits of the csr/field should be covered. No bits must be left undefined.

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
        - "[0] -> unchanged"
        - "[1] wr_val in [0x2000000:0x4000000] -> 0x2000000" # predefined value if write value is
        - "[1] wr_val in [0x4000001:0x3FFFFFFF] -> unchanged"

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
