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
        xlen = kwargs.get('xlen')
        if 32 in xlen:
            rv32 = True
        else:
            rv32 = False
        if 64 in xlen:
            rv64 = True
        else:
            rv64 = False
        super(schemaValidator, self).__init__(*args, **kwargs)

    def _check_with_cannot_be_false_rv64(self, field, value):
        ''' Functions ensures that the field cannot be False in rv64 mode'''
        if rv64 and not value:
            self._error(field, "This field cannot be False")

    def _check_with_cannot_be_false_rv32(self, field, value):
        ''' Functions ensures that the field cannot be False in rv32 mode'''
        if rv32 and not value:
            self._error(field, "This field cannot be False")

    def _check_with_priv_version_check(self, field, value):
        '''Function to check whether the Privileged spec version specified is valid or not.'''
        if value not in constants.priv_versions:
            self._error(
                field,
                "Invalid privilege spec version. Please select one of the following- "
                + ", ".join(constants.priv_versions))

    def _check_with_user_version_check(self, field, value):
        '''Function to check whether the User spec version specified is valid or not.'''
        if value not in constants.user_versions:
            self._error(
                field,
                "Invalid User spec version. Please select one of the following- "
                + ", ".join(constants.user_versions))

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
        if any(x in value for x in "EI"):
            if 'D' in value and not 'F' in value:
                self._error(field, "D cannot exist without F.")
            if 'Q' in value and not all(x in value for x in "FD"):
                self._error(field, "Q cannot exist without F and D.")
            if 'F' in value and not "Zicsr" in value:
                self._error(field, "F cannot exist without Zicsr.")
            if 'Zam' in value and not 'A' in value:
                self._error(field, "Zam cannot exist without A.")
            if 'N' in value and not 'U' in value:
                self._error(field, "N cannot exist without U.")
            if 'S' in value and not 'U' in value:
                self._error(field, "S cannot exist without U.")
            if 'Z' in value and not self.document['User_Spec_Version'] == "2.3":
                self._error(
                    field, "Z is not supported in the User Spec given version.")
        else:
            self._error(field, "Neither of E or I extensions are present")
        #ISA encoding for future use.
        for x in "ABCDEFHIJLMNPQSTUVX":
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
        global xlen
        global extensions
        maxv = max(xlen)
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
        if rv64 and value == True:
            mxl = format(extensions, '#066b')
            if (mxl[65 - s:66 - s] != '1'):
                self._error(field, "S is not present(64)")

        elif rv32 and value == True:
            mxl = format(extensions, '#034b')
            if (mxl[33 - s:34 - s] != '1'):
                self._error(field, "S is not present(32)")

    def _check_with_n_check(self, field, value):
        n = 13
        if rv64:
            mxl = format(extensions, '#066b')
            if (mxl[65 - n:66 - n] != '1'):
                self._error(field, "N is not present")

        elif rv32:
            mxl = format(extensions, '#034b')
            if (mxl[33 - n:34 - n] != '1'):
                self._error(field, "N is not present")

    def _check_with_mdeleg_checks(self, field, value):
        if rv32:
            if (value['rv32']['accessible'] == True and
                (not 'S' in self.document['ISA'] and
                 not 'N' in self.document['ISA'])):
                value['rv32']['accessible'] = False
                self._error(field, "S and N are not present(32)")

        if rv64:
            if (value['rv64']['accessible'] == True and
                (not 'S' in self.document['ISA'] and
                 not 'N' in self.document['ISA'])):
                value['rv64']['accessible'] = False
                self._error(field, "S and N are not present(64)")

    def _check_with_ndeleg_checks(self, field, value):
        if rv32:
            if (value['rv32']['accessible'] == True and
                    not 'N' in self.document['ISA']):
                value['rv32']['accessible'] = False
                self._error(field, "N is not present(32)")

        if rv64:
            if (value['rv64']['accessible'] == True and
                    not 'N' in self.document['ISA']):
                value['rv64']['accessible'] = False
                self._error(field, "N is not present(64)")

    def _check_with_xcause_check(self, field, value):
        '''Function to verify the inputs for mcause.'''
        if (min(value) < 16):
            self._error(
                field, "Invalid platform specific values for exception cause.")

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
            self._error(field, "no mode must exist(legal)")
        elif value['warl']['dependency_fields'] == [] and len(
                value['warl']['legal']) != 1:
            self._error(field, "There should be only one legal value")
        elif value['warl']['dependency_fields'] == [] and pri == 1:
            self._error(field, "no mode must exist(illlegal)")
        elif value['warl']['dependency_fields'] == [] and len(
                value['warl']['legal']
        ) == 1 and value['warl']['wr_illegal'] != None and "bitmask" in value[
                'warl']['legal'][0]:
            self._error(field, "illegal value cannot exist")

    def _check_with_key_check(self, field, value):
        if value['base']['type']['warl']['dependency_fields'] != []:
            par = re.split(
                "::", value['base']['type']['warl']['dependency_fields'][0])
            if not par[1] in value:
                self._error(field, " {} not present".format(par[1]))

    def _check_with_medeleg_reset(self, field, value):
        global xlen
        s = format(value, '#{}b'.format(xlen[0] + 2))
        if (s[-11:-10]) != '0' and value >= int("0x400", 16):
            self._error(field, " 11th bit must be hardwired to 0")

    def _check_with_sedeleg_reset(self, field, value):
        global xlen
        s = format(value, '#{}b'.format(xlen[0] + 2))
        if (s[-11:-8]) != '000' and value >= int("400", 16):
            self._error(field, " 11,10,9 bits should be hardwired to 0")
