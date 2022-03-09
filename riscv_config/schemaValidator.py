from cerberus import Validator
from riscv_config.warl import warl_interpreter
import riscv_config.constants as constants
import re
import os


class schemaValidator(Validator):
    ''' Custom validator for schema having the custom rules necessary for implementation and checks.'''

    def __init__(self, *args, **kwargs):
        global rv32
        global rv64
        global extensions
        global xlen
        global supported_xlen
        supported_xlen = kwargs.get('xlen')
        xlen = 0 if len(supported_xlen)==0 else max(supported_xlen)
        global isa_string
        isa_string = kwargs.get('isa_string')
        if 32 in supported_xlen:
            rv32 = True
        else:
            rv32 = False
        if 64 in supported_xlen:
            rv64 = True
        else:
            rv64 = False
        super(schemaValidator, self).__init__(*args, **kwargs)

    def _check_with_isa_xlen(self, field, value):
        global supported_xlen
        global isa_string
        if str(max(supported_xlen)) not in isa_string:
            self._error(field, 'XLEN in ISA and supported_xlen fields do not match')

    def _check_with_phy_addr(self, field, value):
        if rv32 and value > 34:
            self._error(field, "Physical address size should not exceed 34 for RV32")
        if rv64 and value > 56:
            self._error(field, "Physical address size should not exceed 56 for RV64")


    def _check_with_cannot_be_false_rv64(self, field, value):
        ''' Functions ensures that the field cannot be False in rv64 mode'''
        if rv64 and not value:
            self._error(field, "This field cannot be False")

    def _check_with_cannot_be_false_rv32(self, field, value):
        ''' Functions ensures that the field cannot be False in rv32 mode'''
        if rv32 and not value:
            self._error(field, "This field cannot be False")

    def _check_with_capture_isa_specifics(self, field, value):
        '''
        Function to extract and store ISA specific information(such as xlen,user
        spec version and extensions present)
        and check whether the dependencies in ISA extensions are satisfied.
        '''
        global xlen
        global extensions
        extension_enc = list("00000000000000000000000000")
        if "32" in value:
            xlen = 32
            ext = value[4:]
        elif "64" in value:
            xlen = 64
            ext = value[4:]
        elif "128" in value:
            xlen = 128
            ext = value[5:]
        else:
            self._error(field, "Invalid width in ISA.")
        #ISA checks
        str_match = re.findall('(?P<stdisa>[^\d]*?)(?!_)*(?P<zext>Z.*?)*(?P<sext>S[a-z]*)*(_|$)',value)
        extension_list= []
        standard_isa = ''
        for match in str_match:
            stdisa, zext, sext, ignore = match
            if stdisa != '':
                for e in stdisa:
                    extension_list.append(e)
                standard_isa = stdisa
            if zext != '':
                extension_list.append(zext)
            if sext != '':
                extension_list.append(sext)
        # check ordering of ISA
        canonical_ordering = 'IEMAFDQLCBJKTPVNSHU'
        order_index = {c: i for i, c in enumerate(canonical_ordering)}
        for i in range(len(standard_isa)-1):
            a1 = standard_isa[i]
            a2 = standard_isa[i+1]
        
            if order_index[a1] > order_index[a2]:
                self._error(field, "Alphabet '" + a1 + "' should occur after '" + a2)

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

#        if 'Z' in value and not self.document['User_Spec_Version'] == "2.3":
#            self._error(
#                field, "Z is not supported in the User Spec given version.")
        #ISA encoding for future use.
        for x in "ABCDEFHIJKLMNPQSTUVX":
            if (x in ext):
                extension_enc[25 - int(ord(x) - ord('A'))] = "1"
        extensions = int("".join(extension_enc), 2)
        extensions = int("".join(extension_enc), 2)

    def _check_with_rv32_check(self, field, value):
        global xlen
        if value:
            if not rv32:
                self._error(
                    field,
                    "Register cannot be implemented in rv32 mode due to unsupported xlen."
                )

    def _check_with_rv64_check(self, field, value):
        global xlen
        if value:
            if not rv64:
                self._error(
                    field,
                    "Register cannot be implemented in rv64 mode due to unsupported xlen."
                )

    def _check_with_max_length(self, field, value):
        '''Function to check whether the given value is less than the maximum value that can be stored(2^xlen-1).'''
        global supported_xlen
        global extensions
        maxv = max(supported_xlen)
        if value > (2**maxv) - 1:
            self._error(field, "Value exceeds max supported length")
    
    def _check_with_max_length32(self, field, value):
        '''Function to check whether the given value is less than the maximum value that can be stored(2^xlen-1).'''
        maxv = 32
        if value > (2**maxv) - 1:
            self._error(field, "Value exceeds max supported length")

    def _check_with_xtveccheck(self, field, value):
        '''Function to check whether the inputs in range type in mtvec are valid.'''
        global xlen
        maxv = 2**(xlen - 2)
        for list in value:
            if (len(list) > 2):
                self._error(field,
                            "Only two values are allowed in each sub list.")
            for val in list:
                if not (val < maxv):
                    self._error(field, "Invalid values.")

    def _check_with_s_check(self, field, value):
        s = 18
        check = False
        if 'implemented' in value:
            if value['implemented']:
                check = True
        if 'accessible' in value:
            if value['accessible']:
                check = True

        if rv64 and check:
            mxl = format(extensions, '#066b')
            if (mxl[65 - s:66 - s] != '1'):
                self._error(field, "should not be implemented since S is not present")

        elif rv32 and check:
            mxl = format(extensions, '#034b')
            if (mxl[33 - s:34 - s] != '1'):
                self._error(field, "should not be implemented S is not present")
    
    def _check_with_fs_check(self, field, value):
        f = 5
        s = 18
        check = False
        if 'implemented' in value:
            if value['implemented']:
                check = True
        if 'accessible' in value:
            if value['accessible']:
                check = True

        if rv64 and check:
            mxl = format(extensions, '#066b')
            if (mxl[65 - s:66 - s] != '1') and (mxl[65 - f:66 - f] != '1'):
                self._error(field, "neither S nor F is present")

        elif rv32 and check:
            mxl = format(extensions, '#034b')
            if (mxl[33 - s:34 - s] != '1') and (mxl[33 - f:34 - f] != '1'):
                self._error(field, "neither S nor F is present")
                

    def _check_with_u_check(self, field, value):
        u = 20
        check = False
        if 'implemented' in value:
            if value['implemented']:
                check = True
        if 'accessible' in value:
            if value['accessible']:
                check = True
        if rv64 and check:
            mxl = format(extensions, '#066b')
            if (mxl[65 - u:66 - u] != '1'):
                self._error(field, "should not be implemented since U is not present")

        elif rv32 and check:
            mxl = format(extensions, '#034b')
            if (mxl[33 - u:34 - u] != '1'):
                self._error(field, "should not be implemented since U is not present")
              
    def _check_with_s_debug_check(self, field, value):
        ''' Function ensures that the ro_constant is hardwired to zero when S is present in the ISA string
            Used mainly for debug schema'''
        global isa_string

        if 'S' not in isa_string :
          if 'ro_constant' not in value:
              self._error(field, "S is not present to dcsr.v should be ro_constant = 0")
          elif value['ro_constant'] != 0:
                self._error(field, "S is not present but ro constant is not hardwired to zero")
                
    def _check_with_u_debug_check(self, field, value):
        ''' Function ensures that the ro_constant is hardwired to zero when U is present in the ISA string
            Used mainly for debug schema'''
        global isa_string

        if 'U' not in isa_string :
          if value['ro_constant'] != 0:
                self._error(field, "U is not present but ro constant is not hardwired to zero")

    def _check_with_su_check(self, field, value):
        s = 18
        u = 20
        check = False
        if 'implemented' in value:
            if value['implemented']:
                check = True
        if 'accessible' in value:
            if value['accessible']:
                check = True

        if rv64 and check:
            mxl = format(extensions, '#066b')
            if (mxl[65 - s:66 - s] != '1') and (mxl[65 - u:66 - u] != '1'):
                self._error(field, "neither S nor U is present")

        elif rv32 and check:
            mxl = format(extensions, '#034b')
            if (mxl[33 - s:34 - s] != '1') and (mxl[33 - u:34 - u] != '1'):
                self._error(field, "neither S nor U is present")
                
    def _check_with_reset_ext(self, field, value):
        
        if rv64:
            mxl = format(extensions, '#066b')
            reset = format(value, '#066b')
            if (mxl[40:66] != reset[40:66] ):
                self._error(field, "reset value does not match with extensions enabled")

        elif rv32 :
            mxl = format(extensions, '#034b')
            reset = format(value, '#034b')
            if (mxl[8:34] != reset[8:34] ):
                self._error(field, "reset value does not match with extensions enabled")
                
    def _check_with_sn_check(self, field, value):
        s = 18
        n = 13
        check = False
        if 'implemented' in value:
            if value['implemented']:
                check = True
        if 'accessible' in value:
            if value['accessible']:
                check = True

        if rv64 and check:
            mxl = format(extensions, '#066b')
            if (mxl[65 - s:66 - s] != '1') and (mxl[65 - n:66 - n] != '1'):
                self._error(field, "neither S nor N is present")

        elif rv32 and check:
            mxl = format(extensions, '#034b')
            if (mxl[33 - s:34 - s] != '1') and (mxl[33 - n:34 - n] != '1'):
                self._error(field, "neither S nor N is present")

    def _check_with_n_check(self, field, value):
        n = 13
        check = False
        if 'implemented' in value:
            if value['implemented']:
                check = True
        if 'accessible' in value:
            if value['accessible']:
                check = True
        if rv64 and check:
            mxl = format(extensions, '#066b')
            if (mxl[65 - n:66 - n] != '1'):
                self._error(field, "should not be implemented since N is not present")

        elif rv32 and check:
            mxl = format(extensions, '#034b')
            if (mxl[33 - n:34 - n] != '1'):
                self._error(field, "should not be implemented since N is not present")

    def _check_with_h_check(self, field, value):
        h = 7
        check = False
        if 'implemented' in value:
            if value['implemented']:
                check = True
        if 'accessible' in value:
            if value['accessible']:
                check = True
        if rv64 and check:
            mxl = format(extensions, '#066b')
            if (mxl[65 - h:66 - h] != '1'):
                self._error(field, "h is not present")

        elif rv32 and check:
            mxl = format(extensions, '#034b')
            if (mxl[33 - h:34 - h] != '1'):
                self._error(field, "h is not present")

    def _check_with_mdeleg_checks(self, field, value):
        if rv32:
            if (value['rv32']['accessible'] == True and
                (not 'S' in self.document['ISA'] and
                 not 'N' in self.document['ISA'])):
                value['rv32']['accessible'] = False
                self._error(field, "S and N are not present")

        if rv64:
            if (value['rv64']['accessible'] == True and
                (not 'S' in self.document['ISA'] and
                 not 'N' in self.document['ISA'])):
                value['rv64']['accessible'] = False
                self._error(field, "S and N are not present")

    def _check_with_ndeleg_checks(self, field, value):
        if rv32:
            if (value['rv32']['accessible'] == True and
                    not 'N' in self.document['ISA']):
                value['rv32']['accessible'] = False
                self._error(field, "should not be implemented since N is not present")

        if rv64:
            if (value['rv64']['accessible'] == True and
                    not 'N' in self.document['ISA']):
                value['rv64']['accessible'] = False
                self._error(field, "should not be implemented since N is not present")

    def _check_with_xcause_check(self, field, value):
        '''Function to verify the inputs for mcause.'''
        if (min(value) < 16):
            self._error(
                field, "Invalid platform specific values for exception cause.")

    def _check_with_wr_illegal32(self, field, value):
        '''Function to ensure the warl does not cross 2^32
        '''
        if 'warl' in value:
            warlnode = warl_interpreter(value['warl'])
            x = 0x8000000000000000
            if (len(value['warl']['legal']) > 1):
                while (x > 0x10000000):
                    if warlnode.islegal(x):
                        self._error(
                            field, "Must have a warl which is only 32-bits. Value"  + \
                                        str(hex(x)) + " was considered legal")
                        break
                    x = x>> 1
            else:
                for l in value['warl']['legal']:
                    if 'bitmask' in l:
                        bmask = re.findall(r'\s*\[.*\]\s*bitmask\s*\[(.*?)\]',l)[0]
                        maxval_str = bmask.split(',')[0]
                        if '0x' in maxval_str:
                            maxval = int(maxval_str,16)
                        else:
                            maxval = int(maxval_str,10)
                        if maxval > 0xFFFFFFFF:
                            self._error(
                                field, "Must have a warl which is only 32-bits. Value"  + \
                                        str(hex(maxval)) + " was considered legal")
                    else:
                        while (x > 0x10000000):
                            if warlnode.islegal(x):
                                self._error(
                                    field, "Must have a warl which is only 32-bits. Value"  + \
                                                str(hex(x)) + " was considered legal")
                                break
                            x = x>> 1

    def _check_with_wr_illegal(self, field, value):
        pr = 0
        pri = 0
        if 'warl' not in value.keys():
            return
        for i in range(len(value['warl']['legal'])):
            if ' -> ' in value['warl']['legal'][i]:
                pr = 1
                break
        if value['warl']['wr_illegal'] != None:
            for i in range(len(value['warl']['wr_illegal'])):
                split = re.findall(r'^\s*\[(\d)]\s*',
                                   value['warl']['wr_illegal'][i])
                if split != []:
                    pri = 1
                    break
        if value['warl']['dependency_fields'] != []:
            l = (len(value['warl']['legal']))
            f = 0
            for i in range(l):
                if "bitmask" in value['warl']['legal'][i]:
                    f = 1
                    splits = re.findall(
                        r'(\[\d\])\s*->\s*.*\s*\[.*\]\s*{}\s*\[.*?[,|:].*?]'.
                        format("bitmask"), value['warl']['legal'][i])
                    if value['warl']['wr_illegal'] != None:
                        for j in range(len(value['warl']['wr_illegal'])):
                            if splits[0] in value['warl']['wr_illegal'][j]:
                                self._error(
                                    field,
                                    "illegal value does not exist for the given mode{}(bitmask)"
                                    .format(splits[0]))
            if f == 0:
                pass

        elif value['warl']['dependency_fields'] == [] and pr == 1:
            self._error(field, "since dependency_fields is empty no '->' in legal fields")
        elif value['warl']['dependency_fields'] == [] and len(value['warl']['legal']) != 1:
            self._error(field, "There should be only one legal string")
        elif value['warl']['dependency_fields'] == [] and pri == 1:
            self._error(field, "since dependency_fields is empty illegal fields must be defined for each")
        else:
            for l in value['warl']['legal']:
                if 'bitmask' in l:
                    bmask = re.findall(r'\s*\[.*\]\s*bitmask\s*\[(.*?)\]',l)[0]
                    if ',' not in bmask:
                        self._error(field, 'Legal string "'+l+'" has wrong bitmask syntax')
                    if len(bmask.split(','))!=2:
                        self._error(field, 'Legal string "'+l+'" has wrong bitmkask syntax')
                    for v in bmask.split(','):
                        if '0x' not in v:
                            try:
                                isinstance(int(v,10),int)
                            except:
                                self._error(field, 'Value ' +str(v) + ' in Legal string "'+l+'" is not a valid number')


#        elif value['warl']['dependency_fields'] == [] and len(
#                value['warl']['legal']
#        ) == 1 and value['warl']['wr_illegal'] != None and "bitmask" in value[
#                'warl']['legal'][0]:
#            self._error(field, "illegal value cannot exist for bitmask type")

    def _check_with_key_check(self, field, value):
        if value['base']['type']['warl']['dependency_fields'] != []:
            par = re.split(
                "::", value['base']['type']['warl']['dependency_fields'][0])
            if not par[1] in value:
                self._error(field, " {} not present".format(par[1]))

    def _check_with_medeleg_reset(self, field, value):
        global supported_xlen
        s = format(value, '#{}b'.format(supported_xlen[0] + 2))
        if (s[-11:-10]) != '0' and value >= int("0x400", 16):
            self._error(field, " 11th bit must be hardwired to 0")

    def _check_with_sedeleg_reset(self, field, value):
        global supported_xlen
        s = format(value, '#{}b'.format(supported_xlen[0] + 2))
        if (s[-11:-8]) != '000' and value >= int("400", 16):
            self._error(field, " 11,10,9 bits should be hardwired to 0")
