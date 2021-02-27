#################################
Adding support for new Extensions
#################################

Adding support for a new ISA extension or an adjoining spec to RISCV-CONFIG could entail one or more of the following:

1. Updating the ISA string and its constraints to recognize valid configurations of the new
   extension
2. Updating the schema_isa.yaml with new CSRs defined by the new ISA extension
3. Adding new schemas and a new cli argument for supporting adjoining RISC-V specs like debug, trace, etc.

This chapter will descrive how one can go about RISC-V achieving the above tasks.

Updates to the ISA string
=========================

Modifications in Schema_isa.yaml
----------------------------------------

As shown in the example below, any new extensions and sub extensions have to be enabled by adding them in the regex expression given below. This will give the user the option to configure with the extensions in the input isa yamls. :ref:`isa_yaml_spec`. 

.. code-block:: yaml
   
   
   
   SA: { type: string, required: true, check_with: capture_isa_specifics, 
           regex: "^RV(32|64|128)[IE]+[ABCDEFGIJKLMNPQSTUVX]*(Zicsr|Zifencei|Zihintpause|Zam|Ztso|Zkne|Zknd|Zknh|Zkse|Zksh|Zkg|Zkb|Zkr|Zks|Zkn|Zbc|Zbb|Zbp|Zbm|Zbe|Zbf){,1}(_Zicsr){,1}(_Zifencei){,1}(_Zihintpause){,1}(_Zam){,1}(_Ztso){,1}(_Zkne){,1}(_Zknd){,1}(_Zknh){,1}(_Zkse){,1}(_Zksh){,1}(_Zkg){,1}(_Zkb){,1}(_Zkr){,1}(_Zks){,1}(_Zkn){,1}(_Zbc){,1}(_Zbb){,1}(_Zbp){,1}(_Zbm){,1}(_Zbe){,1}(_Zbf){,1}$" }

    


Adding constraints in the SchemaValidator.py file
---------------------------------------------------------

The conditions shown below are any constraints that will have to be written while adding a new extension.

For example, in the code below , the constraints for the K (Crypto-Scalar extension) have been added wherein the subextensions Zkn, Zks, K are supersets of other Zk* abbreviations. Thus, if the superset extension exists in the ISA, none of the corresponding subset ZK* should be present in the ISA at the same time.


**Constraints used here** : 

   1.If Zkn is present , its subset extensions Zkne, Zknh, Zknd, Zkg and Zkb cannot be present in the ISA string.  

   2.If Zks is present , its subset extensions Zkse, Zksh, Zkg and Zkb cannot be present in the ISA string.


   3.If K extension is present , its subset extensions Zkn, Zkr, Zkne, Zknh, Zknd, Zkg and Zkb cannot be present in the ISA string.
   
   4. If **B extension** Zbp is present , its subset extensions  Zkb cannot be present in the ISA string. Cross-checking across two different extensions can also be done. Zkb contains instructions from other subextensions in B extension like Zbm, Zbe, Zbf and Zbb , but unlike Zbp is not a proper superset.
   
   5. If **B extension** Zbc is present , its subset extensions Zkg cannot be present in the ISA string.


.. code-block:: python

        if 'I' not in extension_list and 'E' not in extension_list:
            self._error(field, 'Either of I or E base extensions need to be present in the ISA string')
        if 'F' in extension_list and not "Zicsr" in extension_list:
            self._error(field, "F cannot exist without Zicsr.")
        if 'D' in extension_list and not 'F' in extension_list:
            self._error(field, "D cannot exist without F.")
        if 'Q' in extension_list and not 'D' in extension_list:
            self._error(field, "Q cannot exist without D and F.")
        if 'Zam' in extension_list and not 'A' in extension_list:
            self._error(field, "Zam cannot exist without A.")
        if 'N' in extension_list and not 'U' in extension_list:
            self._error(field, "N cannot exist without U.")
        if 'S' in extension_list and not 'U' in extension_list:
            self._error(field, "S cannot exist without U.")
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


Updating the schema_isa.yaml with new CSRs defined by the new ISA extension
===========================================================================

Addition of new csrs to schema
------------------------------

Taking S extension as an example, the supervisor-specific csrs from the schema is shown below :

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

All new csrs added must have the corresponding default setter in the checker.py as shown below. 

This must make them accessible by default when the appropriate ISA extension is enabled.

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

          

Adding new schemas and a new cli argument for supporting adjoining RISC-V specs like debug, trace, etc.
=======================================================================================================

Modification to Main.py
-----------------------
The code below shows an example on how to add a new cli argument in main.py for adjoining RISC-V specs with their independent schemas.

The example taken here is the RISC-V Debug Specification . It depends on the input ISA string and hence the isa yaml is also given as input to the debug checker function.

.. code-block:: python

        if args.debug_spec is not None:
            if args.isa_spec is None:
             logger.error(' Isa spec missing, Compulsory for debug')
            checker.check_debug_specs(os.path.abspath(args.debug_spec), isa_file, work_dir, True, args.no_anchors)
           
Modifications in Utils.py
-------------------------

.. code-block:: python

   parser.add_argument('--debug_spec', '-dspec', type=str, metavar='YAML', default=None, help='The YAML which contains the debug csr specs.') 


Modifications in Constants.py
-----------------------------
.. code-block:: python

     debug_schema = os.path.join(root, 'schemas/schema_debug.yaml')
     
Adding checks through checker.py and SchemaValidator.py
-------------------------------------------------------
The check_debug_specs() is a function that ensures the isa and debug specifications confirm to their schemas.
For details on check_debug_specs() check here : :ref:`checker`.

Details on the checks like s_debug_check() and u_debug_check, that can also be added to SchemaValidator.py are here: :ref:`schemaValidator`.


Adding New Schema
----------------------
This schema shows the csrs added according to the `RISC-V Debug Specification <https://github.com/riscv/riscv-debug-spec/blob/master/riscv-debug-stable.pdf>`_ :

.. include:: schema_debug.rst

