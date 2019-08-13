###################
WARL field Proposal
###################

Since the RISC-V privilege spec indicates several CSRs and sub-fields of CSRs to be WARL (Write-Any-Read-Legal), it is now necessary to provide a scheme of WARL functions which can be used to precisely define the functionality of any such WARL field/register. This document provides a proposal to generalize these definitions.

**Authors**: Allen, Pawan, Neel


WARL-FUNC(*warl-func*)
======================

The WARL function can be defined in two ways:
    - a list of single-value-tuples explicitly specifying the distinct legal values that the field/register can take. 
    - a list of four-value-tuples defining a specific range of legal values that the field/register can take.

1. Single-Value-Tuple Description:
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
These can simply be enumerated as [ [0], [3], [19], ...]. 
This means that the respective csr can only take legal values: 0, 3, 19, ....

2. Four-Value-Tuple Description:
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

  Here the legal values of the field/register is defined using 4 fields:

    .. code-block:: python

      [ mask, fixedval, lower, upper]


  - **mask** : A bit with value 1 indicates that the bit is writable. A bit value of 0  indicates the bit is hardwired to a value corresponding to the same bit in the fixedval field.  
  - **fixedval** : For all the bits that are 0s in mask, the corresponding bits in this field indicate the hardwired value (can be 0 or 1).
  - **lower**: This defines the lower-bound of legal values.
  - **upper**: This defines the upper-bound of legal values.

  The *base* and *bound* values are defined as :
    .. code-block:: python

      base  = (lower & mask) | (fixedval & ~mask)
      bound = (upper & mask) | (fixedval & ~mask)

  The value (val) to be written to the csr/register is defined as:
    .. code-block:: python

      val = (write-val & mask) | (fixedval & ~mask)

  This value is legal only if it lies within the base and bound values:

    .. code-block:: python
   
      base <= val >= bound


  Now if val is an illegal value, the field/register should resort to a known legal value. There are multiple options possible and they defined using the **mode** field which can be any of the following:
    - **unchanged**: The value remains unchanged
    - **nextup**: ceiling(*val*) i.e. the next larger or the largest element of the list
    - **nextdown**: floor(*val*) i.e. the next smallest or the smallest element of the list
    - **nearup**: celing(*val*) i.e. the closest element in the list, with the larger element being chosen in case of a tie.
    - **neardown**: floor(*val*) i.e. the closes element in the list, with the smaller element being chosen in case of a tie
    - **largest**: maximum of all legal values
    - **smallest**: minimum of all legal values
    - **addr**: 
      
        .. code-block:: python
    
          if ( val < base || val > bound)
             return Flip-MSB of field
    
    - **bitmask**: The write for the register is masked with the mask specified in the set. This is a valid mode when only one set of 4 elements exists in the description.

        .. code-block:: python

            return val
        
    Example definitions:

    .. code-block:: yaml

        # when it is 256 byte aligned and can lie between 
        # 0x80000000 to 0x40000000
        warl-func:
            mode: unchanged
            legal: [0xFFFFFF00, 0x0, 0x40000000, 0x80000000]
        
        # For complete bitmask type implementation
        # (like for extensions in misa for RV64IMFADCSUZicsr_Zifencei)
        warl-func:
            mode: bitmask
            legal: [0x214102D, 0x100, 0x0, 0x3FFFFFF]
        
        # For normal range type applications for a 24 bit 
        # field with a valid range of 0x500000 to 0x300000
        warl-func:
            mode: smallest
            legal: [0xFFFFFF, 0x0, 0x300000, 0x500000]

YAML WARL Node definition(*warl*)
=================================

    This provides the structure for describing the WARL fields in riscv-config YAML

    - **dependency_variables** : A list of fields/registers on whose value this particular WARL field depends. (Can be empty indicating no dependencies). The sub-fields within csrs can be specified as follows:

       ..  code-block:: python

           csr::field

    - **behaviour** : A list of dictionaries where each dictionary describes the value of the dependency_variables under which the field exhibts the corresponding *warl-func*. Each dictionary is structured as follows.

       .. code-block:: yaml

         func:
            dependency_values: A list of values which corresponding to each variable within the 
                               dependency_variables list.          
            warl-func:  A function conforming to the above warl-func definition above.
    
     No legal value must exceed the maximum value which can be supported(based on the width of the field). Functions should be exhaustive with respect to all possible allowed values of dependencies i.e For each allowed value for a dependency variable any one of the functions defined should match and more than one function must not match for any possible combination of allowed values for the dependency variables.

    Examples:

    .. code-block:: yaml

        # When base of mtvec depends on the mode field.
        WARL: 
          dependency_variables: [mtvec::mode]
          behavior:
            func1:
              dependency_values: [0]                 # use this warl_func when mtvec:mode == 0
              warl_func: 
                mode: "Unchanged"
                legal: [[0x20000000], [0x20004000]]  # can take only 2 fixed values in direct mode.
            func2:
              dependency_values: [1]                 # use this warl_func when mtvec:mode == 1
              warl_func: 
                mode: "Unchanged"
                legal: [[0xFFFFFF00, 0x0, 0x00000000,0x20000000]] # 256 byte aligned values.
    
        # no dependencies. Mode field of mtvec can take only 2 legal values using four-value-tuples
        WARL:
          dependency_variables: []
          behavior:
            func1: 
              dependency_values: []
              warl_func:
                mode: "Unchanged"
                legal: [[0x3,0x0,0x0,0x1]]

        # no dependencies. using single-value-tuples
        WARL:
          dependency_variables: []
          behavior:
            func1: 
              dependency_values: []
              warl_func:
                mode: "Unchanged"
                legal: [[0x0], [0x1]]

        # multi-field dependencies. A random example
        WARL:
            dependency_variables: [mtvec::mode,misa::extensions]
            behaviour:
                - func1:
                    dependency_values: [x, [0x4,0x0]] # x is for dont care. 
                    warl-func: 
                        mode: Unchanged
                        legal: [0x80000000]
                - func2:
                    dependency_values: [0, [0x3FFFFFF,0x4]]
                    warl-func:
                        mode: Unchanged
                        legal: [[0x4000,0x0]]
                - func3:
                    dependency_values: [1, [0x3FFFFFF,0x4]]
                    warl-func:
                        mode: Unchanged
                        legal: [0x0,0xFFFFFFF0,0x80000000,0x40000000]

