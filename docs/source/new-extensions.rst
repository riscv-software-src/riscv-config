##############################
Flow to add new ISA extensions
##############################

This section describe the steps to be followed while adding new extension and the corresponding constraints attached to it.

Step 1: Modifications in Schema_isa.yaml
========================================

As shown in the example below, any new extensions and sub extensions have to be enabled by adding them in the regex expression given below. This will give the user the option to configure with the extensions in the input isa yamls. :ref:`isa_yaml_spec`. 

.. code-block:: yaml
   
   
   
   SA: { type: string, required: true, check_with: capture_isa_specifics, 
           regex: "^RV(32|64|128)[IE]+[ABCDEFGIJKLMNPQSTUVX]*(Zicsr|Zifencei|Zihintpause|Zam|Ztso|Zkne|Zknd|Zknh|Zkse|Zksh|Zkg|Zkb|Zkr|Zks|Zkn|Zbc|Zbb|Zbp|Zbm|Zbe|Zbf){,1}(_Zicsr){,1}(_Zifencei){,1}(_Zihintpause){,1}(_Zam){,1}(_Ztso){,1}(_Zkne){,1}(_Zknd){,1}(_Zknh){,1}(_Zkse){,1}(_Zksh){,1}(_Zkg){,1}(_Zkb){,1}(_Zkr){,1}(_Zks){,1}(_Zkn){,1}(_Zbc){,1}(_Zbb){,1}(_Zbp){,1}(_Zbm){,1}(_Zbe){,1}(_Zbf){,1}$" }

    


Step 2: Adding constraints in the SchemaValidator.py file
=========================================================

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
