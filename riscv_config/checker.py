import os
import logging

from cerberus import Validator

import itertools
import riscv_config.utils as utils
from riscv_config.errors import ValidationError
from riscv_config.schemaValidator import schemaValidator
import riscv_config.constants as constants
from riscv_config.utils import yaml
from riscv_config.warl import warl_interpreter

logger = logging.getLogger(__name__)


def nosset():
    '''Function to check and set defaults for all fields which are dependent on
        the presence of 'S' extension.'''
    global inp_yaml
    if 'S' in inp_yaml['ISA']:
        return {'implemented': True}
    else:
        return {'implemented': False}


def uset():
    '''Function to set defaults based on presence of 'U' extension.'''
    global inp_yaml
    if 'U' in inp_yaml['ISA']:
        return {'implemented': True}
    else:
        return {'implemented': False}


def nuset():
    '''Function to check and set defaults for all fields which are dependent on
        the presence of 'U' extension and 'N' extension.'''
    global inp_yaml
    if 'U' in inp_yaml['ISA'] and 'N' in inp_yaml['ISA']:
        return {'implemented': True}
    else:
        return {'implemented': False}


def twset():
    '''Function to check and set value for tw field in misa.'''
    global inp_yaml
    if 'S' not in inp_yaml['ISA'] and 'U' not in inp_yaml['ISA']:
        return {'implemented': False}
    else:
        return {'implemented': False}


def delegset():
    '''Function to set "implemented" value for mideleg regisrer.'''
    # return True
    global inp_yaml
    var = True
    if 'U' not in inp_yaml['ISA']:
        var = False
    elif (('U' in inp_yaml['ISA']) and
          not ('N' in inp_yaml['ISA'] or 'S' in inp_yaml['ISA'])):
        var = False

    temp = {'rv32': {'accessible': False}, 'rv64': {'accessible': False}}
    if 32 in inp_yaml['supported_xlen']:
        temp['rv32']['accessible'] = True and var
    if 64 in inp_yaml['supported_xlen']:
        temp['rv64']['accessible'] = True and var
    return temp


def countset():
    global inp_yaml
    temp = {'rv32': {'accessible': False}, 'rv64': {'accessible': False}}
    if 'S' in inp_yaml['ISA'] or 'U' in inp_yaml["ISA"]:
        if 32 in inp_yaml['supported_xlen']:
            temp['rv32']['accessible'] = True
        if 64 in inp_yaml['supported_xlen']:
            temp['rv64']['accessible'] = True
    return temp


def regset():
    global inp_yaml
    temp = {'rv32': {'accessible': False}, 'rv64': {'accessible': False}}
    if 32 in inp_yaml['supported_xlen']:
        temp['rv32']['accessible'] = True
    if 64 in inp_yaml['supported_xlen']:
        temp['rv64']['accessible'] = True
    return temp


def counterhset():
    global inp_yaml
    temp = {'rv32': {'accessible': False}, 'rv64': {'accessible': False}}
    if 32 in inp_yaml['supported_xlen']:
        temp['rv32']['accessible'] = True
    return temp


def add_def_setters(schema_yaml):
    '''Function to set the default setters for various fields in the schema'''
    regsetter = lambda doc: regset()
    schema_yaml['misa']['default_setter'] = regsetter
    schema_yaml['mstatus']['default_setter'] = regsetter
    schema_yaml['mvendorid']['default_setter'] = regsetter
    schema_yaml['mimpid']['default_setter'] = regsetter
    schema_yaml['marchid']['default_setter'] = regsetter
    schema_yaml['mhartid']['default_setter'] = regsetter
    schema_yaml['mtvec']['default_setter'] = regsetter
    schema_yaml['mip']['default_setter'] = regsetter
    schema_yaml['mie']['default_setter'] = regsetter
    schema_yaml['mscratch']['default_setter'] = regsetter
    schema_yaml['mepc']['default_setter'] = regsetter
    schema_yaml['mtval']['default_setter'] = regsetter
    schema_yaml['mcountinhibit']['default_setter'] = regsetter

    # event counters
    schema_yaml['mhpmevent3']['default_setter'] = regsetter
    schema_yaml['mhpmevent4']['default_setter'] = regsetter
    schema_yaml['mhpmevent5']['default_setter'] = regsetter
    schema_yaml['mhpmevent6']['default_setter'] = regsetter
    schema_yaml['mhpmevent7']['default_setter'] = regsetter
    schema_yaml['mhpmevent8']['default_setter'] = regsetter
    schema_yaml['mhpmevent9']['default_setter'] = regsetter
    schema_yaml['mhpmevent10']['default_setter'] = regsetter
    schema_yaml['mhpmevent11']['default_setter'] = regsetter
    schema_yaml['mhpmevent12']['default_setter'] = regsetter
    schema_yaml['mhpmevent13']['default_setter'] = regsetter
    schema_yaml['mhpmevent14']['default_setter'] = regsetter
    schema_yaml['mhpmevent15']['default_setter'] = regsetter
    schema_yaml['mhpmevent16']['default_setter'] = regsetter
    schema_yaml['mhpmevent17']['default_setter'] = regsetter
    schema_yaml['mhpmevent18']['default_setter'] = regsetter
    schema_yaml['mhpmevent19']['default_setter'] = regsetter
    schema_yaml['mhpmevent20']['default_setter'] = regsetter
    schema_yaml['mhpmevent21']['default_setter'] = regsetter
    schema_yaml['mhpmevent22']['default_setter'] = regsetter
    schema_yaml['mhpmevent23']['default_setter'] = regsetter
    schema_yaml['mhpmevent24']['default_setter'] = regsetter
    schema_yaml['mhpmevent25']['default_setter'] = regsetter
    schema_yaml['mhpmevent26']['default_setter'] = regsetter
    schema_yaml['mhpmevent27']['default_setter'] = regsetter
    schema_yaml['mhpmevent28']['default_setter'] = regsetter
    schema_yaml['mhpmevent29']['default_setter'] = regsetter
    schema_yaml['mhpmevent30']['default_setter'] = regsetter
    schema_yaml['mhpmevent31']['default_setter'] = regsetter

    schema_yaml['mhpmcounter3']['default_setter'] = regsetter
    schema_yaml['mhpmcounter4']['default_setter'] = regsetter
    schema_yaml['mhpmcounter5']['default_setter'] = regsetter
    schema_yaml['mhpmcounter6']['default_setter'] = regsetter
    schema_yaml['mhpmcounter7']['default_setter'] = regsetter
    schema_yaml['mhpmcounter8']['default_setter'] = regsetter
    schema_yaml['mhpmcounter9']['default_setter'] = regsetter
    schema_yaml['mhpmcounter10']['default_setter'] = regsetter
    schema_yaml['mhpmcounter11']['default_setter'] = regsetter
    schema_yaml['mhpmcounter12']['default_setter'] = regsetter
    schema_yaml['mhpmcounter13']['default_setter'] = regsetter
    schema_yaml['mhpmcounter14']['default_setter'] = regsetter
    schema_yaml['mhpmcounter15']['default_setter'] = regsetter
    schema_yaml['mhpmcounter16']['default_setter'] = regsetter
    schema_yaml['mhpmcounter17']['default_setter'] = regsetter
    schema_yaml['mhpmcounter18']['default_setter'] = regsetter
    schema_yaml['mhpmcounter19']['default_setter'] = regsetter
    schema_yaml['mhpmcounter20']['default_setter'] = regsetter
    schema_yaml['mhpmcounter21']['default_setter'] = regsetter
    schema_yaml['mhpmcounter22']['default_setter'] = regsetter
    schema_yaml['mhpmcounter23']['default_setter'] = regsetter
    schema_yaml['mhpmcounter24']['default_setter'] = regsetter
    schema_yaml['mhpmcounter25']['default_setter'] = regsetter
    schema_yaml['mhpmcounter26']['default_setter'] = regsetter
    schema_yaml['mhpmcounter27']['default_setter'] = regsetter
    schema_yaml['mhpmcounter28']['default_setter'] = regsetter
    schema_yaml['mhpmcounter29']['default_setter'] = regsetter
    schema_yaml['mhpmcounter30']['default_setter'] = regsetter
    schema_yaml['mhpmcounter31']['default_setter'] = regsetter

    counthsetter = lambda doc: counterhset()

    schema_yaml['mhpmcounter3h']['default_setter'] = counthsetter
    schema_yaml['mhpmcounter4h']['default_setter'] = counthsetter
    schema_yaml['mhpmcounter5h']['default_setter'] = counthsetter
    schema_yaml['mhpmcounter6h']['default_setter'] = counthsetter
    schema_yaml['mhpmcounter7h']['default_setter'] = counthsetter
    schema_yaml['mhpmcounter8h']['default_setter'] = counthsetter
    schema_yaml['mhpmcounter9h']['default_setter'] = counthsetter
    schema_yaml['mhpmcounter10h']['default_setter'] = counthsetter
    schema_yaml['mhpmcounter11h']['default_setter'] = counthsetter
    schema_yaml['mhpmcounter12h']['default_setter'] = counthsetter
    schema_yaml['mhpmcounter13h']['default_setter'] = counthsetter
    schema_yaml['mhpmcounter14h']['default_setter'] = counthsetter
    schema_yaml['mhpmcounter15h']['default_setter'] = counthsetter
    schema_yaml['mhpmcounter16h']['default_setter'] = counthsetter
    schema_yaml['mhpmcounter17h']['default_setter'] = counthsetter
    schema_yaml['mhpmcounter18h']['default_setter'] = counthsetter
    schema_yaml['mhpmcounter19h']['default_setter'] = counthsetter
    schema_yaml['mhpmcounter20h']['default_setter'] = counthsetter
    schema_yaml['mhpmcounter21h']['default_setter'] = counthsetter
    schema_yaml['mhpmcounter22h']['default_setter'] = counthsetter
    schema_yaml['mhpmcounter23h']['default_setter'] = counthsetter
    schema_yaml['mhpmcounter24h']['default_setter'] = counthsetter
    schema_yaml['mhpmcounter25h']['default_setter'] = counthsetter
    schema_yaml['mhpmcounter26h']['default_setter'] = counthsetter
    schema_yaml['mhpmcounter27h']['default_setter'] = counthsetter
    schema_yaml['mhpmcounter28h']['default_setter'] = counthsetter
    schema_yaml['mhpmcounter29h']['default_setter'] = counthsetter
    schema_yaml['mhpmcounter30h']['default_setter'] = counthsetter
    schema_yaml['mhpmcounter31h']['default_setter'] = counthsetter

    schema_yaml['mcounteren']['default_setter'] = lambda doc: countset()

    schema_yaml['mcause']['default_setter'] = regsetter
    nusetter = lambda doc: nuset()
    schema_yaml['mstatus']['schema']['rv32']['schema']['uie'][
        'default_setter'] = nusetter
    schema_yaml['mstatus']['schema']['rv64']['schema']['uie'][
        'default_setter'] = nusetter
    schema_yaml['mstatus']['schema']['rv32']['schema']['upie'][
        'default_setter'] = nusetter
    schema_yaml['mstatus']['schema']['rv64']['schema']['upie'][
        'default_setter'] = nusetter

    usetter = lambda doc: uset()
    schema_yaml['mstatus']['schema']['rv32']['schema']['mprv'][
        'default_setter'] = usetter
    schema_yaml['mstatus']['schema']['rv64']['schema']['mprv'][
        'default_setter'] = usetter
    schema_yaml['mstatus']['schema']['rv64']['schema']['uxl'][
        'default_setter'] = usetter

    schema_yaml['mip']['schema']['rv32']['schema']['ueip'][
        'default_setter'] = nusetter
    schema_yaml['mip']['schema']['rv64']['schema']['ueip'][
        'default_setter'] = nusetter
    schema_yaml['mip']['schema']['rv32']['schema']['utip'][
        'default_setter'] = nusetter
    schema_yaml['mip']['schema']['rv64']['schema']['utip'][
        'default_setter'] = nusetter
    schema_yaml['mip']['schema']['rv32']['schema']['usip'][
        'default_setter'] = nusetter
    schema_yaml['mip']['schema']['rv64']['schema']['usip'][
        'default_setter'] = nusetter
    schema_yaml['mie']['schema']['rv32']['schema']['ueie'][
        'default_setter'] = nusetter
    schema_yaml['mie']['schema']['rv64']['schema']['ueie'][
        'default_setter'] = nusetter
    schema_yaml['mie']['schema']['rv32']['schema']['utie'][
        'default_setter'] = nusetter
    schema_yaml['mie']['schema']['rv64']['schema']['utie'][
        'default_setter'] = nusetter
    schema_yaml['mie']['schema']['rv32']['schema']['usie'][
        'default_setter'] = nusetter
    schema_yaml['mie']['schema']['rv64']['schema']['usie'][
        'default_setter'] = nusetter

    ssetter = lambda doc: nosset()
    schema_yaml['mstatus']['schema']['rv32']['schema']['sie'][
        'default_setter'] = ssetter
    schema_yaml['mstatus']['schema']['rv64']['schema']['sie'][
        'default_setter'] = ssetter
    schema_yaml['mstatus']['schema']['rv32']['schema']['spie'][
        'default_setter'] = ssetter
    schema_yaml['mstatus']['schema']['rv64']['schema']['spie'][
        'default_setter'] = ssetter
    schema_yaml['mstatus']['schema']['rv32']['schema']['spp'][
        'default_setter'] = ssetter
    schema_yaml['mstatus']['schema']['rv64']['schema']['spp'][
        'default_setter'] = ssetter
    schema_yaml['mstatus']['schema']['rv32']['schema']['tvm'][
        'default_setter'] = ssetter
    schema_yaml['mstatus']['schema']['rv64']['schema']['tvm'][
        'default_setter'] = ssetter
    schema_yaml['mstatus']['schema']['rv64']['schema']['sxl'][
        'default_setter'] = ssetter
    schema_yaml['mstatus']['schema']['rv32']['schema']['tsr'][
        'default_setter'] = ssetter
    schema_yaml['mstatus']['schema']['rv64']['schema']['tsr'][
        'default_setter'] = ssetter
    schema_yaml['mstatus']['schema']['rv32']['schema']['mxr'][
        'default_setter'] = ssetter
    schema_yaml['mstatus']['schema']['rv64']['schema']['mxr'][
        'default_setter'] = ssetter
    schema_yaml['mstatus']['schema']['rv32']['schema']['sum'][
        'default_setter'] = ssetter
    schema_yaml['mstatus']['schema']['rv64']['schema']['sum'][
        'default_setter'] = ssetter
    schema_yaml['mip']['schema']['rv32']['schema']['seip'][
        'default_setter'] = ssetter
    schema_yaml['mip']['schema']['rv64']['schema']['seip'][
        'default_setter'] = ssetter
    schema_yaml['mip']['schema']['rv32']['schema']['stip'][
        'default_setter'] = ssetter
    schema_yaml['mip']['schema']['rv64']['schema']['stip'][
        'default_setter'] = ssetter
    schema_yaml['mip']['schema']['rv32']['schema']['ssip'][
        'default_setter'] = ssetter
    schema_yaml['mip']['schema']['rv64']['schema']['ssip'][
        'default_setter'] = ssetter
    schema_yaml['mie']['schema']['rv32']['schema']['seie'][
        'default_setter'] = ssetter
    schema_yaml['mie']['schema']['rv64']['schema']['seie'][
        'default_setter'] = ssetter
    schema_yaml['mie']['schema']['rv32']['schema']['stie'][
        'default_setter'] = ssetter
    schema_yaml['mie']['schema']['rv64']['schema']['stie'][
        'default_setter'] = ssetter
    schema_yaml['mie']['schema']['rv32']['schema']['ssie'][
        'default_setter'] = ssetter
    schema_yaml['mie']['schema']['rv64']['schema']['ssie'][
        'default_setter'] = ssetter
    twsetter = lambda doc: twset()
    schema_yaml['mstatus']['schema']['rv32']['schema']['tw'][
        'default_setter'] = twsetter
    schema_yaml['mstatus']['schema']['rv64']['schema']['tw'][
        'default_setter'] = twsetter
    delegsetter = lambda doc: delegset()
    schema_yaml['medeleg']['default_setter'] = delegsetter
    schema_yaml['mideleg']['default_setter'] = delegsetter
    return schema_yaml


def trim(foo):
    '''
        Function to trim the dictionary. Any node with implemented field set to false is trimmed of all the other nodes.

        :param foo: The dictionary to be trimmed.

        :type foo: dict

        :return: The trimmed dictionary.
    '''
    keys = foo.keys()
    if 'rv32' in keys:
        if not foo['rv32']['accessible']:
            foo['rv32'] = {'accessible': False}
    if 'rv64' in keys:
        if not foo['rv64']['accessible']:
            foo['rv64'] = {'accessible': False}
    if 'implemented' in keys:
        if not foo['implemented']:
            temp = foo
            for k in list(
                    set(foo.keys()) -
                    set(['description', 'msb', 'lsb', 'implemented', 'shadow'])
            ):
                try:
                    temp.pop(k)
                except KeyError:
                    continue
            return temp
    for key in keys:
        if isinstance(foo[key], dict):
            t = trim(foo[key])
            foo[key] = t
    return foo


def groupc(test_list):
    ''' Generator function to squash consecutive numbers for wpri bits.'''
    for x, y in itertools.groupby(enumerate(test_list), lambda a: a[1] - a[0]):
        y = list(y)
        a = y[0][1]
        b = y[-1][1]
        if a == b:
            yield [a]
        else:
            yield [a, b]


def get_fields(node, bitwidth):
    fields = list(
        set(node.keys()) -
        set(['fields', 'msb', 'lsb', 'accessible', 'shadow', 'type']))
    if not fields:
        return fields
    bits = set(range(bitwidth))
    for entry in fields:
        bits -= set(range(node[entry]['lsb'], node[entry]['msb'] + 1))
    bits = list(groupc(sorted(list(bits))))
    if not bits:
        return fields
    else:
        fields.append(bits)
        return fields


def check_reset_fill_fields(spec):
    errors = {}
    for node in spec:
        if isinstance(spec[node], dict):
            if spec[node]['rv32']['accessible']:
                spec[node]['rv32']['fields'] = get_fields(
                    spec[node]['rv32'], 32)
            if spec[node]['rv64']['accessible']:
                spec[node]['rv64']['fields'] = get_fields(
                    spec[node]['rv64'], 64)
            if 'reset-val' in spec[node].keys():
                reset_val = spec[node]['reset-val']
                if spec[node]['rv64']['accessible']:
                    field_desc = spec[node]['rv64']
                    bit_len = 64
                elif spec[node]['rv32']['accessible']:
                    field_desc = spec[node]['rv32']
                    bit_len = 32
                else:
                    continue
                error = []
                if not field_desc['fields']:
                    desc = field_desc['type']
                    keys = desc.keys()
                    if 'wlrl' in keys:
                        res = False
                        for entry in desc['wlrl']:
                            if ":" in entry:
                                low, high = entry.split(":")
                                if "x" in low:
                                    low = int(low, base=16)
                                    high = int(high, base=16)
                                else:
                                    low = int(low)
                                    high = int(high)
                                if reset_val >= low and reset_val <= high:
                                    res = True
                                    break
                            else:
                                if "x" in entry:
                                    val = int(entry, base=16)
                                else:
                                    val = int(entry)
                                if val == reset_val:
                                    res = True
                                    break
                        if not res:
                            error.append(
                                "Reset value doesnt match the 'wlrl' description for the register."
                            )
                    elif 'ro_constant' in keys:
                        if reset_val not in desc['ro_constant']:
                            error.append(
                                "Reset value doesnt match the 'ro_constant' description for the register."
                            )
                    elif 'ro_variable' in keys:
                        pass
                    elif "warl" in keys:
                        warl = (warl_interpreter(desc['warl']))
                        deps = warl.dependencies()
                        dep_vals = []
                        for dep in deps:
                            reg = dep.split("::")
                            if len(reg) == 1:
                                dep_vals.append(spec[reg[0]]['reset-val'])
                            else:
                                bin_str = bin(spec[reg[0]]
                                              ['reset-val'])[2:].zfill(bit_len)
                                dep_vals.append(
                                    int(bin_str[bit_len - 1 - spec[reg[0]][
                                        'rv{}'.format(bit_len
                                                     )][reg[1]]['msb']:bit_len -
                                                spec[reg[0]]['rv{}'.format(
                                                    bit_len)][reg[1]]['lsb']],
                                        base=2))
                        if (warl.islegal(hex(reset_val)[2:], dep_vals) != True):
                            error.append(
                                "Reset value doesnt match the 'warl' description for the register."
                            )
                else:
                    bin_str = bin(reset_val)[2:].zfill(bit_len)
                    for field in field_desc['fields']:
                        if isinstance(field, list):
                            for entry in field:
                                if len(entry) == 2:
                                    test_val = int(
                                        bin_str[bit_len - 1 - entry[1]:bit_len -
                                                entry[0]],
                                        base=2)
                                    if test_val != 0:
                                        error.append("WPRI bits " +
                                                     str(entry[0]) + " to " +
                                                     str(entry[1]) +
                                                     " should be zero.")
                                elif len(entry) == 1:
                                    test_val = int(bin_str[bit_len - 1 -
                                                           entry[0]],
                                                   base=2)
                                    if test_val != 0:
                                        error.append("WPRI bit " +
                                                     str(entry[0]) +
                                                     " should be zero.")
                        else:
                            test_val = int(
                                bin_str[bit_len - 1 -
                                        field_desc[field]['msb']:bit_len -
                                        field_desc[field]['lsb']],
                                base=2)
                            if field_desc[field]['implemented']:
                                desc = field_desc[field]['type']
                                keys = desc.keys()
                                if 'wlrl' in keys:
                                    res = False
                                    for entry in desc['wlrl']:
                                        if ":" in entry:
                                            low, high = entry.split(":")
                                            if "x" in low:
                                                low = int(low, base=16)
                                                high = int(high, base=16)
                                            else:
                                                low = int(low)
                                                high = int(high)
                                            if test_val >= low and test_val <= high:
                                                res = True
                                                break
                                        else:
                                            if "x" in entry:
                                                val = int(entry, base=16)
                                            else:
                                                val = int(entry)
                                            if val == test_val:
                                                res = True
                                                break
                                    if not res:
                                        error.append(
                                            "Reset value for " + field +
                                            " doesnt match the 'wlrl' description."
                                        )
                                elif 'ro_constant' in keys:
                                    if test_val not in desc['ro_constant']:
                                        error.append(
                                            "Reset value for " + field +
                                            " doesnt match the 'ro_constant' description."
                                        )
                                elif 'ro_variable' in keys:
                                    pass
                                elif "warl" in keys:
                                    warl = (warl_interpreter(desc['warl']))
                                    deps = warl.dependencies()
                                    dep_vals = []
                                    for dep in deps:
                                        reg = dep.split("::")
                                        if len(reg) == 1:
                                            dep_vals.append(
                                                spec[reg[0]]['reset-val'])
                                        else:
                                            bin_str = bin(
                                                spec[reg[0]]['reset-val']
                                            )[2:].zfill(bit_len)
                                            dep_vals.append(
                                                int(bin_str[
                                                    bit_len - 1 -
                                                    spec[reg[0]]['rv{}'.format(
                                                        bit_len
                                                    )][reg[1]]['msb']:bit_len -
                                                    spec[reg[0]]['rv{}'.format(
                                                        bit_len
                                                    )][reg[1]]['lsb']],
                                                    base=2))
                                    if (warl.islegal(
                                            hex(test_val)[2:], dep_vals) !=
                                            True):
                                        error.append(
                                            "Reset value for " + field +
                                            " doesnt match the 'warl' description."
                                        )
                            elif test_val != 0:
                                error.append("Reset value for unimplemented " +
                                             field + " cannot be non zero.")
                if error:
                    errors[node] = error
    return spec, errors


def check_specs(isa_spec, platform_spec, work_dir, logging=False):
    '''
        Function to perform ensure that the isa and platform specifications confirm
        to their schemas. The :py:mod:`Cerberus` module is used to validate that the
        specifications confirm to their respective schemas.

        :param isa_spec: The path to the DUT isa specification yaml file.

        :param platform_spec: The path to the DUT platform specification yaml file.

        :param logging: A boolean to indicate whether log is to be printed.

        :type logging: bool

        :type isa_spec: str

        :type platform_spec: str

        :raise ValidationError: It is raised when the specifications violate the
            schema rules. It also contains the specific errors in each of the fields.

        :return: A tuple with the first entry being the absolute path to normalized isa file
            and the second being the absolute path to the platform spec file.
    '''
    global inp_yaml

    if logging:
        logger.info('Input-ISA file')

    foo = isa_spec
    schema = constants.isa_schema
    """
      Read the input-isa foo (yaml file) and validate with schema-isa for feature values
      and constraints
    """
    # Load input YAML file
    if logging:
        logger.info('Loading input file: ' + str(foo))
    inp_yaml = utils.load_yaml(foo)

    # instantiate validator
    if logging:
        logger.info('Load Schema ' + str(schema))
    schema_yaml = add_def_setters(utils.load_yaml(schema))

    #Extract xlen
    xlen = inp_yaml['supported_xlen']

    # schema_yaml = add_def_setters(schema_yaml)
    validator = schemaValidator(schema_yaml, xlen=xlen)
    validator.allow_unknown = False
    validator.purge_readonly = True
    normalized = validator.normalized(inp_yaml, schema_yaml)

    # Perform Validation
    if logging:
        logger.info('Initiating Validation')
    valid = validator.validate(normalized)

    # Print out errors
    if valid:
        if logging:
            logger.info('No Syntax errors in Input ISA Yaml. :)')
    else:
        error_list = validator.errors
        raise ValidationError("Error in " + foo + ".", error_list)
    logger.info("Initiating post processing and reset value checks.")
    normalized, errors = check_reset_fill_fields(normalized)
    if errors:
        raise ValidationError("Error in " + foo + ".", errors)
    file_name = os.path.split(foo)
    file_name_split = file_name[1].split('.')
    output_filename = os.path.join(
        work_dir, file_name_split[0] + '_checked.' + file_name_split[1])
    ifile = output_filename
    outfile = open(output_filename, 'w')
    if logging:
        logger.info('Dumping out Normalized Checked YAML: ' + output_filename)
    yaml.dump(trim(normalized), outfile)

    if logging:
        logger.info('Input-Platform file')

    foo = platform_spec
    schema = constants.platform_schema
    """
      Read the input-platform foo (yaml file) and validate with schema-platform for feature values
      and constraints
    """
    # Load input YAML file
    if logging:
        logger.info('Loading input file: ' + str(foo))
    inp_yaml = utils.load_yaml(foo)
    if inp_yaml is None:
        inp_yaml = {'mtime': {'implemented': False}}

    # instantiate validator
    if logging:
        logger.info('Load Schema ' + str(schema))
    schema_yaml = utils.load_yaml(schema)

    validator = schemaValidator(schema_yaml, xlen=xlen)
    validator.allow_unknown = False
    validator.purge_readonly = True
    normalized = validator.normalized(inp_yaml, schema_yaml)

    # Perform Validation
    if logging:
        logger.info('Initiating Validation')
    valid = validator.validate(normalized)

    # Print out errors
    if valid:
        if logging:
            logger.info('No Syntax errors in Input Platform Yaml. :)')
    else:
        error_list = validator.errors
        raise ValidationError("Error in " + foo + ".", error_list)

    file_name = os.path.split(foo)
    file_name_split = file_name[1].split('.')
    output_filename = os.path.join(
        work_dir, file_name_split[0] + '_checked.' + file_name_split[1])
    pfile = output_filename
    outfile = open(output_filename, 'w')
    if logging:
        logger.info('Dumping out Normalized Checked YAML: ' + output_filename)
    yaml.dump(trim(normalized), outfile)
    return (ifile, pfile)
