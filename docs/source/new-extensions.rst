#################################
Adding support for new Extensions
#################################

Adding support for a new ISA extension or an adjoining spec to RISCV-CONFIG could entail one or more of the following updates:

1. Updating the ISA string and its constraints to recognize valid configurations of the new
   extension
2. Updating the schema_isa.yaml with new CSRs defined by the new ISA extension
3. Adding new schemas and a new cli argument for supporting adjoining RISC-V specs like debug, trace, etc.

This chapter will descrive how one can go about RISC-V achieving the above tasks.

Updates to the ISA string
=========================

Modifications in Schema_isa.yaml
----------------------------------------

As shown in the example below, any new extensions and sub extensions have to be enabled by adding them in 
the regex expression of the `ISA <https://github.com/riscv/riscv-config/blob/master/riscv_config/schemas/schema_isa.yaml>`_ node. Following is an instance of the node
for reference:

.. code-block:: yaml
   
   
   
   ISA: { type: string, required: true, check_with: capture_isa_specifics, 
           regex: "^RV(32|64|128)[IE]+[ABCDEFGIJKLMNPQSTUVX]*(Zicsr|Zifencei|Zihintpause|Zam|Ztso|Zkne|Zknd|Zknh|Zkse|Zksh|Zkg|Zkb|Zkr|Zks|Zkn|Zbc|Zbb|Zbp|Zbm|Zbe|Zbf){,1}(_Zicsr){,1}(_Zifencei){,1}(_Zihintpause){,1}(_Zam){,1}(_Ztso){,1}(_Zkne){,1}(_Zknd){,1}(_Zknh){,1}(_Zkse){,1}(_Zksh){,1}(_Zkg){,1}(_Zkb){,1}(_Zkr){,1}(_Zks){,1}(_Zkn){,1}(_Zbc){,1}(_Zbb){,1}(_Zbp){,1}(_Zbm){,1}(_Zbe){,1}(_Zbf){,1}$" }

    
.. note:: If you are adding a new Z extension, note that it must be added in 2 places in the regex.
   The first immediately after the standard extension in the format `|Zgargle`. This is to support
   that fact that the new Z extension could start immediately after the standard extensions which an
   underscore. The second will be after the first set of Z extensions in the format `{,1}(_Zgargle)`.


Adding constraints in the SchemaValidator.py file
---------------------------------------------------------

While adding a new extension, there can be certain legal and illegal combinations which cannot be
easily expressed using the regex above. To facilitate defining illegal conditions, riscv-config
allows user to define specific checks via custom python functions.

For the ISA field riscv-config uses the
`_check_with_capture_isa_specifics <https://github.com/riscv/riscv-config/blob/master/riscv_config/schemaValidator.py#L46>`_
function to return an error if an illegal combination of the extesions (or subextension) is found.


Following is an example of the constraints imposed by the K extesion and its subset.
Within the K (Crypto-Scalar extension), subextensions Zkn, Zks, K are supersets of other Zk* abbreviations. 
Thus, if the superset extension exists in the ISA, none of the corresponding subset ZK* should be present in the ISA at the same time.


**Constraints used here** : 

   1.If Zkn is present , its subset extensions Zkne, Zknh, Zknd, Zkg and Zkb cannot be present in the ISA string.  

   2.If Zks is present , its subset extensions Zkse, Zksh, Zkg and Zkb cannot be present in the ISA string.


   3.If K extension is present , its subset extensions Zkn, Zkr, Zkne, Zknh, Zknd, Zkg and Zkb cannot be present in the ISA string.
   
   4. If **B extension** Zbp is present , its subset extensions  Zkb cannot be present in the ISA string. Cross-checking across two different extensions can also be done. Zkb contains instructions from other subextensions in B extension like Zbm, Zbe, Zbf and Zbb , but unlike Zbp is not a proper superset.
   
   5. If **B extension** Zbc is present , its subset extensions Zkg cannot be present in the ISA string.


.. code-block:: python

        (...)
        if 'Zkg' in extension_list and 'Zbc' in extension_list:
            self._error(field, "Zkg being a proper subset of Zbc (from B extension) should be ommitted from the ISA string")
        if 'Zkb' in extension_list and 'Zbp' in extension_list :
            self._error(field, "Zkb being a proper subset of Zbp (from B extension) should be ommitted from the ISA string")
        if 'Zks' in extension_list and ( set(['Zkse', 'Zksh','Zkg','Zkb']) & set(extension_list) ):
            self._error(field, "Zks is a superset of Zkse, Zksh, Zkg and Zkb. In presence of Zks the subsets must be ignored in the ISA string.")
        if 'Zkn' in extension_list and ( set(['Zkne','Zknd','Zknh','Zkg','Zkb']) & set(extension_list) ):
            self._error(field, "Zkn is a superset of Zkne, Zknd, Zknh, Zkg and Zkb, In presence of Zkn the subsets must be ignored in the ISA string")
        if 'K' in extension_list and ( set(['Zkn','Zkr','Zkne','Zknd','Zknh','Zkg','Zkb']) & set(extension_list) ) :
            self._error(field, "K is a superset of Zkn and Zkr , In presence of K the subsets must be ignored in the ISA string")
        (...)


Assing new CSR definitions
===========================

There are two parts to addition of a new csr definition to riscv-config

Addition of new csrs to schema
------------------------------

The first step is to add the schema of the new csr in the `schema_isa.yaml
<https://github.com/riscv/riscv-config/blob/master/riscv_config/schemas/schema_isa.yaml>`_ file.
Following is an example of how the `stval` csr of the "S" extension is a added to the schema.

.. note:: for each csr the user is free to define and re-use existing check_with functions to impose
   further legal conditions. In the example below, the stval should only be implemented if the "S"
   extension in the ISA field is set. This is checked using the `s_check` function. Any new
   check_with functions must be defined in the `schemaValidator.py
   <https://github.com/riscv/riscv-config/blob/master/riscv_config/schemaValidator.py>`_ file


.. code-block:: yaml

   stval:
      type: dict
      schema:
        description:
          type: string
          default: The stval is a warl register that holds the address of the instruction
            which caused the exception.
        address: {type: integer, default: 0x143, allowed: [0x143]}
        priv_mode: {type: string, default: S, allowed: [S]}
        reset-val:
          type: integer
          default: 0
          check_with: max_length
        rv32:
          type: dict
          check_with: s_check
          schema:
            fields: {type: list, default: []}
            shadow: {type: string, default: , nullable: True}
            msb: {type: integer, default: 31, allowed: [31]}
            lsb: {type: integer, default: 0, allowed: [0]}
            type:
              type: dict
              check_with: wr_illegal
              schema: { warl: *ref_warl }
              default:
                warl:
                  dependency_fields: []
                  legal:
                  - stval[31:0] in [0x00000000:0xFFFFFFFF]
                  wr_illegal:
                  - unchanged
    
            accessible:
              type: boolean
              default: true
              check_with: rv32_check
          default: {accessible: false}
        rv64:
          type: dict
          check_with: s_check
          schema:
            fields: {type: list, default: []}
            shadow: {type: string, default: , nullable: True}
            msb: {type: integer, default: 63, allowed: [63]}
            lsb: {type: integer, default: 0, allowed: [0]}
            type:
              type: dict
              check_with: wr_illegal
              schema: { warl: *ref_warl }
              default:
                warl:
                  dependency_fields: []
                  legal:
                  - stval[63:0] in [0x00000000:0xFFFFFFFFFFFFFFFF]
                  wr_illegal:
                  - unchanged
    
            accessible:
              default: true
              check_with: rv64_check
          default: {accessible: false}
          
          
Adding default setters in checker.py
------------------------------------

The next step in adding a new csr definition if to add its default values. This is done in
`checker.py <https://github.com/riscv/riscv-config/blob/master/riscv_config/checker.py>`_

Example of adding a default setter for `stval` is show below. This code basically makes the stval
csr accessible by default when the "S" extension is enabled in the ISA string.

.. code-block:: python
   
   schema_yaml['stval']['default_setter'] = sregsetter
   
.. code-block:: python
  
   def sregset():
    '''Function to set defaults based on presence of 'S' extension.'''
    global inp_yaml
    temp = {'rv32': {'accessible': False}, 'rv64': {'accessible': False}}
    if 'S' in inp_yaml['ISA']:
      if 32 in inp_yaml['supported_xlen']:
        temp['rv32']['accessible'] = True
      if 64 in inp_yaml['supported_xlen']:
        temp['rv64']['accessible'] = True
    return temp

          

Adding support for Adjoining RISC-V specs
=========================================

Adding new CLI
--------------

For supporting any new adjoining specs, they need to be supplied via a new cli (command line
interface) argument. This new argument needs to be added in the to the parser module in 
`Utils.py <https://github.com/riscv/riscv-config/blob/d969b7dc5b2b308bb43b0aa65932fe2e7f8c756c/riscv_config/utils.py#L106>`.

The code below shows an example of how the debug spec is added as an argument to the cli parser
module:

.. code-block:: python

   parser.add_argument('--debug_spec', '-dspec', type=str, metavar='YAML', default=None, help='The YAML which contains the debug csr specs.') 


Adding a new schema
-------------------

Each new adjoining spec must have a YAML schema defined in the `schemas
<https://github.com/riscv/riscv-config/tree/master/riscv_config/schemas>` director.


Adding checks through checker.py and SchemaValidator.py
-------------------------------------------------------

The user might want to add more custom checks in checker.py and SchemaValidator.py for the adjoining
spec.

For example the check_debug_specs() is a function that ensures the isa and debug specifications 
conform to their schemas. For details on check_debug_specs() check here : :ref:`checker`.

Details on the checks like s_debug_check() and u_debug_check, that can also be added to 
SchemaValidator.py are here: :ref:`schemaValidator`.

Modifications in Constants.py
-----------------------------

The new schema must be added in the constants.py to detect its path globally across other files.

.. code-block:: python

     debug_schema = os.path.join(root, 'schemas/schema_debug.yaml')
     
Performing new spec checks
--------------------------

Finally, in the main.py file the user must call the relevant functions from checker.py for
validating the inputs against the schema.


.. code-block:: python

        if args.debug_spec is not None:
            if args.isa_spec is None:
             logger.error(' Isa spec missing, Compulsory for debug')
            checker.check_debug_specs(os.path.abspath(args.debug_spec), isa_file, work_dir, True, args.no_anchors)
           


