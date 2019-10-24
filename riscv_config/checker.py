import os
import logging

from cerberus import Validator

import riscv_config.utils as utils
from riscv_config.errors import ValidationError
from riscv_config.schemaValidator import schemaValidator
import riscv_config.constants as constants
from riscv_config.utils import yaml

logger = logging.getLogger(__name__)


def nosset():
    '''Function to check and set defaults for all fields which are dependent on 
        the presence of 'S' extension.'''
    global inp_yaml
    if 'S' in inp_yaml['ISA']:
        return {'implemented': True}
    else:
        return {'implemented': False}


def nouset():
    '''Function to check and set defaults for all fields which are dependent on 
        the presence of 'U' extension.'''
    global inp_yaml
    if 'U' in inp_yaml['ISA']:
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

    temp = {'rv32': {'implemented': False}, 'rv64': {'implemented': False}}
    if 32 in inp_yaml['supported_xlen']:
        temp['rv32']['implemented'] = True and var
    if 64 in inp_yaml['supported_xlen']:
        temp['rv64']['implemented'] = True and var
    return temp


def mepcset():
    return {
        'range': {
            'rangelist': [[0, int("FFFFFFFF", 16)]],
            'mode': "Unchanged"
        }
    }


def xtvecset():
    return {
        'BASE': {
            'range': {
                'rangelist': [[0, int("3FFFFFFF", 16)]],
                'mode': "Unchanged"
            }
        },
        'MODE': {
            'range': {
                'rangelist': [[0]],
                'mode': "Unchanged"
            }
        }
    }


def simpset():
    global inp_yaml
    if 'S' in inp_yaml['ISA']:
        return True
    else:
        return False


def satpset():
    return {'MODE': {'range': {'rangelist': [[0]]}}}


def xlenset():
    return findxlen()


def regset():
    global inp_yaml
    temp = {'rv32': {'implemented': False}, 'rv64': {'implemented': False}}
    if 32 in inp_yaml['supported_xlen']:
        temp['rv32']['implemented'] = True
    if 64 in inp_yaml['supported_xlen']:
        temp['rv64']['implemented'] = True
    return temp


def add_def_setters(schema_yaml):
    '''Function to set the default setters for various fields in the schema'''
    # schema_yaml['mstatus']['schema']['SXL']['schema']['implemented'][
    #     'default_setter'] = lambda doc: iset()
    # schema_yaml['mstatus']['schema']['UXL']['schema']['implemented'][
    #     'default_setter'] = lambda doc: iset()
    # schema_yaml['mstatus']['schema']['TVM'][
    #     'default_setter'] = lambda doc: nosset()
    # schema_yaml['mstatus']['schema']['TSR'][
    #     'default_setter'] = lambda doc: nosset()
    # schema_yaml['mstatus']['schema']['MXR'][
    #     'default_setter'] = lambda doc: nosset()
    # schema_yaml['mstatus']['schema']['SUM'][
    #     'default_setter'] = lambda doc: nosset()
    # schema_yaml['mstatus']['schema']['SPP'][
    #     'default_setter'] = lambda doc: nosset()
    # schema_yaml['mstatus']['schema']['SPIE'][
    #     'default_setter'] = lambda doc: nosset()
    # schema_yaml['mstatus']['schema']['SIE'][
    #     'default_setter'] = lambda doc: nosset()
    # schema_yaml['mstatus']['schema']['UPIE'][
    #     'default_setter'] = lambda doc: upieset(doc)
    # schema_yaml['mstatus']['schema']['UIE'][
    #     'default_setter'] = lambda doc: uieset(doc)
    # schema_yaml['mstatus']['schema']['MPRV'][
    #     'default_setter'] = lambda doc: nouset()
    # schema_yaml['mstatus']['schema']['TW'][
    #     'default_setter'] = lambda doc: twset()
    # schema_yaml['mideleg']['schema']['implemented'][
    #     'default_setter'] = lambda doc: miedelegset()
    # schema_yaml['medeleg']['schema']['implemented'][
    #     'default_setter'] = lambda doc: miedelegset()
    # schema_yaml['mepc']['default_setter'] = lambda doc: mepcset()
    # schema_yaml['mtvec']['default_setter'] = lambda doc: xtvecset()
    # schema_yaml['stvec']['default_setter'] = lambda doc: xtvecset()
    # schema_yaml['satp']['default_setter'] = lambda doc: satpset()
    # schema_yaml['stvec']['schema']['implemented'][
    #     'default_setter'] = lambda doc: simpset()
    # schema_yaml['sie']['schema']['implemented'][
    #     'default_setter'] = lambda doc: simpset()
    # schema_yaml['sip']['schema']['implemented'][
    #     'default_setter'] = lambda doc: simpset()
    # schema_yaml['scounteren']['schema']['implemented'][
    #     'default_setter'] = lambda doc: simpset()
    # schema_yaml['sepc']['schema']['implemented'][
    #     'default_setter'] = lambda doc: simpset()
    # schema_yaml['satp']['schema']['implemented'][
    #     'default_setter'] = lambda doc: simpset()
    # schema_yaml['xlen']['default_setter'] = lambda doc: xlenset()
    regsetter = lambda doc: regset()
    schema_yaml['misa']['default_setter'] = regsetter
    schema_yaml['mstatus']['default_setter'] = regsetter
    schema_yaml['mvendorid']['default_setter'] = regsetter
    schema_yaml['marchid']['default_setter'] = regsetter
    schema_yaml['mhartid']['default_setter'] = regsetter
    schema_yaml['mtvec']['default_setter'] = regsetter
    schema_yaml['mip']['default_setter'] = regsetter
    schema_yaml['mie']['default_setter'] = regsetter
    schema_yaml['mscratch']['default_setter'] = regsetter
    schema_yaml['mepc']['default_setter'] = regsetter
    schema_yaml['mtval']['default_setter'] = regsetter
    schema_yaml['mcause']['default_setter'] = regsetter
    usetter = lambda doc: nouset()
    schema_yaml['mstatus']['schema']['rv32']['schema']['uie'][
        'default_setter'] = usetter
    schema_yaml['mstatus']['schema']['rv64']['schema']['uie'][
        'default_setter'] = usetter
    schema_yaml['mstatus']['schema']['rv32']['schema']['upie'][
        'default_setter'] = usetter
    schema_yaml['mstatus']['schema']['rv64']['schema']['upie'][
        'default_setter'] = usetter
    schema_yaml['mstatus']['schema']['rv32']['schema']['mprv'][
        'default_setter'] = usetter
    schema_yaml['mstatus']['schema']['rv64']['schema']['mprv'][
        'default_setter'] = usetter
    schema_yaml['mstatus']['schema']['rv64']['schema']['uxl'][
        'default_setter'] = usetter
    schema_yaml['mip']['schema']['rv32']['schema']['ueip'][
        'default_setter'] = usetter
    schema_yaml['mip']['schema']['rv64']['schema']['ueip'][
        'default_setter'] = usetter
    schema_yaml['mip']['schema']['rv32']['schema']['utip'][
        'default_setter'] = usetter
    schema_yaml['mip']['schema']['rv64']['schema']['utip'][
        'default_setter'] = usetter
    schema_yaml['mip']['schema']['rv32']['schema']['usip'][
        'default_setter'] = usetter
    schema_yaml['mip']['schema']['rv64']['schema']['usip'][
        'default_setter'] = usetter
    schema_yaml['mie']['schema']['rv32']['schema']['ueie'][
        'default_setter'] = usetter
    schema_yaml['mie']['schema']['rv64']['schema']['ueie'][
        'default_setter'] = usetter
    schema_yaml['mie']['schema']['rv32']['schema']['utie'][
        'default_setter'] = usetter
    schema_yaml['mie']['schema']['rv64']['schema']['utie'][
        'default_setter'] = usetter
    schema_yaml['mie']['schema']['rv32']['schema']['usie'][
        'default_setter'] = usetter
    schema_yaml['mie']['schema']['rv64']['schema']['usie'][
        'default_setter'] = usetter

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


def imp_normalise(foo):
    '''
        Function to trim the dictionary. Any node with implemented field set to false is trimmed of all the other nodes.
        
        :param foo: The dictionary to be trimmed.
        
        :type foo: dict

        :return: The trimmed dictionary.
    '''
    imp = False
    for key in foo.keys():
        if key == 'implemented':
            if not foo[key]:
                imp = True
                break    
        elif isinstance(foo[key], dict):
            foo[key] = imp_normalise(foo[key])
        
        if imp:
            temp = foo
            for k in ['reset-val','type']:
                try:
                    temp = temp.pop(k)
                except KeyError:
                    continue
            return temp
        else:
            return foo


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
    valid = validator.validate(inp_yaml)

    # Print out errors
    if valid:
        if logging:
            logger.info('No Syntax errors in Input ISA Yaml. :)')
    else:
        error_list = validator.errors
        raise ValidationError("Error in " + foo + ".", error_list)

    file_name = os.path.split(foo)
    file_name_split = file_name[1].split('.')
    output_filename = os.path.join(
        work_dir, file_name_split[0] + '_checked.' + file_name_split[1])
    ifile = output_filename
    outfile = open(output_filename, 'w')
    if logging:
        logger.info('Dumping out Normalized Checked YAML: ' + output_filename)
    yaml.dump(imp_normalise(normalized), outfile)

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
    valid = validator.validate(inp_yaml)

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
    yaml.dump(imp_normalise(normalized), outfile)
    return (ifile, pfile)
