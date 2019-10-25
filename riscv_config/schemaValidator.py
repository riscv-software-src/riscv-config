from cerberus import Validator
import riscv_config.constants as constants


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

    def _check_with_misa_reset_values(self, field, value):
        ''' Functions checks if the reset value of the misa register is in
        correlation with the ISA field'''

        global extensions
        if rv64:
            mxl = format(value, '#066b')[:4]
            if mxl != format(2, '#04b')[:4]:
                self._error(field, 'MXL in reset-val is wrong. Expected: 2')
        elif rv32:
            mxl = format(value, '#034b')[:4]
            if mxl != format(1, '#04b')[:4]:
                self._error(field, 'MXL in reset-val is wrong. Expected: 1')

        if (value & 0x3FFFFFF) != extensions:
            self._error(
                field, "Reset value of MISA is not compliant with the \
ISA provided. Expeected reset-val: " + str(extensions))

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
                self._error(field, "Z is not supported in the given version.")
        else:
            self._error(field, "Neither of E or I extensions are present.")
        #ISA encoding for future use.
        for x in "ACDEFGIJLMNPQSTUVXZ":
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

    def _check_with_ro_reset_check(self, field, value):
        '''Function to check whether the reset value of the register is equal to the max supported ro value.'''
        if rv64:
            if not value['reset-val'] in value['rv64']['type']['ro']:
                self._error(field, "Reset value not equal to readonly value.")
        elif rv32:
            if not value['reset-val'] in value['rv32']['type']['ro']:
                self._error(field, "Reset value not equal to readonly value.")

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

    def _check_with_len_check(self, field, value):
        '''Function to check whether the given value is less than XLEN/32(For check).'''
        global xlen
        global extensions
        maxv = xlen / 32 + 1
        for list in value:
            if (len(list) > 2):
                self._error(field,
                            "Only two values are allowed in each sub list.")
            for val in list:
                if not (val < maxv):
                    self._error(field, "Invalid values.")

    def _check_with_sxl_check(self, field, value):
        '''Function to check whether the input list for SXL field is valid.'''
        global extensions
        global xlen
        global sxlen
        maxv = xlen / 32
        allowed = []
        for list in value:
            if (len(list) > 2):
                self._error(field,
                            "Only two values are allowed in each sub list.")
            if (len(list) == 2):
                for x in range(list[0], list[1] + 1):
                    allowed.append(x)
            else:
                allowed.append(list[0])
        sxlen = max(allowed)
        if any(x > maxv for x in allowed):
            self._error(field, "Max allowed value is " + str(maxv))
        if 0 in allowed:
            if len(allowed) > 1:
                self._error(
                    field,
                    "0 is not allowed as a legal value with other values")
            elif extensions & int("0040000", 16) == 0:
                self._error(
                    field,
                    "SXL cannot be hardwired to 0 when S mode is supported")

    def _check_with_uxl_check(self, field, value):
        '''Function to check whether the input list for UXL field is valid.'''
        global extensions
        global xlen
        maxv = xlen / 32
        allowed = []
        for list in value:
            if (len(list) > 2):
                self._error(field,
                            "Only two values are allowed in each sub list.")
            if (len(list) == 2):
                for x in range(list[0], list[1] + 1):
                    allowed.append(x)
            else:
                allowed.append(list[0])
        if any(x > maxv for x in allowed):
            self._error(field, "Max allowed value is " + str(maxv))
        if 0 in allowed:
            if len(allowed) > 1:
                self._error(
                    field,
                    "0 is not allowed as a legal value with other values")
            elif extensions & int("0100000", 16) == 0:
                self._error(
                    field,
                    "UXL cannot be hardwired to 0 when S mode is supported")

    def _check_with_ext_check(self, field, value):
        '''Function to check whether the bitmask given for the Extensions field in misa is valid.'''
        global xlen
        global extensions
        val = value['mask'] ^ value['default'] ^ extensions
        if (val > 0):
            self._error(field, "Extension Bitmask error.")

    def _check_with_mpp_check(self, field, value):
        '''Function to check whether the modes specified in MPP field in mstatus is supported'''
        global extensions
        allowed = []
        for list in value:
            if (len(list) > 2):
                self._error(field,
                            "Only two values are allowed in each sub list.")
            if (len(list) == 2):
                for x in range(list[0], list[1] + 1):
                    allowed.append(x)
            else:
                allowed.append(list[0])
        if (0 in allowed) and extensions & int("0100000", 16) == 0:
            self._error(field,
                        "0 not a valid entry as U extension is not supported.")
        if (1 in allowed) and extensions & int("0040000", 16) == 0:
            self._error(field,
                        "1 not a valid entry as S extension is not supported.")

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

    def _check_with_hardwirecheck(self, field, value):
        '''Function to check that none of the bits in the field are hardwired to 1'''
        if (value['implemented']):
            if (value['bitmask']['default'] > 0):
                self._error(field, "No bit can be harwired to 1.")

    def _check_with_medelegcheck(self, field, value):
        '''Function to check that the input given for medeleg satisfies the constraints'''
        if (value['implemented']):
            if (value['bitmask']['mask'] & int("800", 16) > 0):
                self._error(field, "11th bit must be hardwired to 0.")
            if (value['bitmask']['default'] > 0):
                self._error(field, "No bit can be harwired to 1.")

    def _check_with_rangecheck(self, field, value):
        '''Function to check whether the inputs in range type in WARL fields are valid.'''
        global xlen
        maxv = 2**(xlen)
        for list in value:
            if (len(list) > 2):
                self._error(field,
                            "Only two values are allowed in each sub list.")
            for val in list:
                if not (val < maxv):
                    self._error(field, "Value greater than " + str(maxv))

    def _check_with_xcause_check(self, field, value):
        '''Function to verify the inputs for mcause.'''
        if (min(value) < 16):
            self._error(
                field, "Invalid platform specific values for exception cause.")

    def _check_with_satp_check(self, field, value):
        global sxlen
        if value['implemented']:
            try:
                if sxlen == 1:
                    for list in value['MODE']['range']['rangelist']:
                        if (len(list) > 2):
                            self._error(
                                field,
                                "Only two values are allowed in each sub list.")
                        for val in list:
                            if not val in [0, 1]:
                                self._error(field, "Invalid value " + str(val))
                    asidlen = 9
                    ppnlen = 22
                elif sxlen == 2:
                    allowed = []
                    for list in value['MODE']['range']['rangelist']:
                        if (len(list) > 2):
                            self._error(
                                field,
                                "Only two values are allowed in each sub list.")
                        for val in list:
                            if not val in [0, 8, 9]:
                                self._error(field, "Invalid value " + str(val))
                            allowed.append(val)
                    if 9 in allowed and 8 not in allowed:
                        self._error(field, "9 cannot be present without 8.")
                    asidlen = 16
                    ppnlen = 44
                maxv = (2**asidlen) - 1
                if 'bitmask' in value['ASID']:
                    if value['ASID']['bitmask']['mask'] > maxv:
                        self._error(
                            field, "ASID-Bitmask-mask value is greater than " +
                            str(maxv))
                    if value['ASID']['bitmask']['mask'] > maxv:
                        self._error(
                            field,
                            "ASID-Bitmask-default value is greater than " +
                            str(maxv))
                if 'range' in value['ASID']:
                    for list in value['ASID']['range']['rangelist']:
                        if (len(list) > 2):
                            self._error(
                                field,
                                "Only two values are allowed in each sub list.")
                        for val in list:
                            if val > maxv:
                                self._error(
                                    field,
                                    "ASID-range-rangelist Value greater than " +
                                    str(maxv))
                maxv = (2**ppnlen) - 1
                if 'bitmask' in value['PPN']:
                    if value['PPN']['bitmask']['mask'] > maxv:
                        self._error(
                            field, "PPN-Bitmask-mask value is greater than " +
                            str(maxv))
                    if value['PPN']['bitmask']['mask'] > maxv:
                        self._error(
                            field,
                            "PPN-Bitmask-default value is greater than " +
                            str(maxv))
                if 'range' in value['PPN']:
                    for list in value['PPN']['range']['rangelist']:
                        if (len(list) > 2):
                            self._error(
                                field,
                                "Only two values are allowed in each sub list.")
                        for val in list:
                            if val > maxv:
                                self._error(
                                    field,
                                    "PPN-range-rangelist Value greater than " +
                                    str(maxv))
            except KeyError:
                self._error(
                    field,
                    "Please refer to the schema and enter the node values correctly."
                )
