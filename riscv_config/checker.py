import os
import logging
import copy
import re

from cerberus import Validator

import itertools
import riscv_config.utils as utils
from riscv_config.errors import ValidationError
from riscv_config.schemaValidator import schemaValidator
import riscv_config.constants as constants
from riscv_config.warl import warl_interpreter

logger = logging.getLogger(__name__)


def reset():
    '''Function to set defaults to reset val of misa  based on presence of ISA extensions.'''
    global inp_yaml
    global extensions
    extension_enc = list("00000000000000000000000000")
    value=inp_yaml['ISA']
    if "32" in value:
       xlen = 32
       ext = value[4:]
    elif "64" in value:
       xlen = 64
       ext = value[4:]
    elif "128" in value:
       xlen = 128
       ext = value[5:]
    for x in "ABCDEFHIJKLMNPQSTUVX":
            if (x in ext):
                extension_enc[25 - int(ord(x) - ord('A'))] = "1"
    extensions = int("".join(extension_enc), 2)
    ext_b=format(extensions, '#0{}b'.format(xlen+2))
    mxl='10'if xlen==64 else '01'
    ext_b = ext_b[:2] + str(mxl) + ext_b[4:]
    return int(ext_b, 2)
    
def resetsu():
    '''Function to set defaults to reset val of mstatus based on the xlen and S, U extensions'''
    global inp_yaml
    if 64 in inp_yaml['supported_xlen'] and 'S' not in inp_yaml['ISA'] and 'U' in inp_yaml['ISA']:
      return 8589934592
    elif 64 in inp_yaml['supported_xlen'] and 'U' in inp_yaml['ISA'] and 'S' in inp_yaml['ISA']:
      return 42949672960
    else:	
      return 0

def uset():
    '''Function to set defaults based on presence of 'U' extension.'''
    global inp_yaml
    if 'U' in inp_yaml['ISA']:
        return {'implemented': True}
    else:
        return {'implemented': False}

def sset():
    '''Function to set defaults based on presence of 'S' extension.'''
    global inp_yaml
    if 'S' in inp_yaml['ISA']:
        return {'implemented': True}
    else:
        return {'implemented': False}
        
def fsset():
    '''Function to set defaults based on presence of 'F' extension.'''
    global inp_yaml
    if 'F' in inp_yaml['ISA'] or 'S' in inp_yaml['ISA']:
        return {'implemented': True}
    else:
        return {'implemented': False}
        

def uregset():
    '''Function to set defaults based on presence of 'U' extension.'''
    global inp_yaml
    temp = {'rv32': {'accessible': False}, 'rv64': {'accessible': False}}
    if 'U' in inp_yaml['ISA']:
      if 32 in inp_yaml['supported_xlen']:
        temp['rv32']['accessible'] = True
      if 64 in inp_yaml['supported_xlen']:
        temp['rv64']['accessible'] = True
    return temp

def uregseth():
    '''Function to set defaults based on presence of 'U' extension.'''
    global inp_yaml
    temp = {'rv32': {'accessible': False}, 'rv64': {'accessible': False}}
    if 'U' in inp_yaml['ISA']:
      if 32 in inp_yaml['supported_xlen']:
        temp['rv32']['accessible'] = True
    return temp
        
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

def nregset():
    '''Function to set defaults based on presence of 'N' extension.'''
    global inp_yaml
    temp = {'rv32': {'accessible': False}, 'rv64': {'accessible': False}}
    if 'N' in inp_yaml['ISA']:
      if 32 in inp_yaml['supported_xlen']:
        temp['rv32']['accessible'] = True
      if 64 in inp_yaml['supported_xlen']:
        temp['rv64']['accessible'] = True
    return temp
    
def sregseth():
    '''Function to set defaults based on presence of 'S' extension.'''
    global inp_yaml
    temp = {'rv32': {'accessible': False}, 'rv64': {'accessible': False}}
    if 'S' in inp_yaml['ISA']:
      if 32 in inp_yaml['supported_xlen']:
        temp['rv32']['accessible'] = True
    return temp


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
        return {'implemented': True}


def delegset():
    '''Function to set "implemented" value for mideleg regisrer.'''
    # return True
    global inp_yaml
    var = True
    if 'S' not in inp_yaml['ISA'] and 'N' not in inp_yaml['ISA']:
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
    
def pmpregset():
    global inp_yaml
    temp = {'rv32': {'accessible': False}, 'rv64': {'accessible': False}} 
    try:   
     if 32 in inp_yaml['supported_xlen'] and inp_yaml[temp]['rv32']['accessible'] :
        temp['rv32']['accessible'] = True
    except:
        temp['rv32']['accessible'] = False
    try: 
     if 64 in inp_yaml['supported_xlen'] and inp_yaml[temp]['rv64']['accessible']:
        temp['rv64']['accessible'] = True
    except:
        temp['rv64']['accessible'] = False
    return temp    

def pmpcounterhset():
    global inp_yaml
    temp = {'rv32': {'accessible': False}, 'rv64': {'accessible': False}}
    try: 
     if 32 in inp_yaml['supported_xlen'] and inp_yaml[temp]['rv32']['accessible'] :
        temp['rv32']['accessible'] = True
    except:
        temp['rv32']['accessible'] = False
    return temp
    
def counterhset():
    global inp_yaml
    temp = {'rv32': {'accessible': False}, 'rv64': {'accessible': False}}
    if 32 in inp_yaml['supported_xlen']:
        temp['rv32']['accessible'] = True
    return temp

def add_debug_setters(schema_yaml):
    '''Function to set the default setters for various fields in the debug schema'''
    regsetter = lambda doc: regset()
    
    schema_yaml['dcsr']['default_setter'] = regsetter
    return schema_yaml
    
def add_reset_setters(schema_yaml):
    '''Function to set the default setters for extension  subfields in the misa'''
    global inp_yaml
    global extensions
    xlen=inp_yaml['supported_xlen'][0]
    rvxlen='rv'+str(xlen)
    extensions=hex(int(format(reset(), '#0{}b'.format(xlen+2))[(xlen-24):(xlen+2)], 2))
    schema_yaml['misa']['schema'][rvxlen]['schema']['extensions']['schema']['type']['default']['warl']['legal'][0]=schema_yaml['misa']['schema'][rvxlen]['schema']['extensions']['schema']['type']['default']['warl']['legal'][0].replace('0x3FFFFFFF', extensions)
    return schema_yaml
    
def add_fflags_type_setters(schema_yaml):
    global inp_yaml
    xlen=inp_yaml['supported_xlen'][0]
    rvxlen='rv'+str(xlen)
    if 'F' not in inp_yaml['ISA']:
        schema_yaml['fflags']['schema'][rvxlen]['schema']['type']['default']={'ro_constant': 0}
        schema_yaml['frm']['schema'][rvxlen]['schema']['type']['default']={'ro_constant': 0}
        schema_yaml['fcsr']['schema'][rvxlen]['schema']['type']['default']={'ro_constant': 0}
    return schema_yaml
    
def add_def_setters(schema_yaml):
    '''Function to set the default setters for various fields in the schema'''
    regsetter = lambda doc: regset()
    resetsetter=lambda doc: reset()
    reset_susetter=lambda doc: resetsu()
    pmpregsetter = lambda doc: pmpregset()
    counthsetter = lambda doc: counterhset()
    pmpcounthsetter = lambda doc: pmpcounterhset()
    uregsetter = lambda doc: uregset()
    ureghsetter = lambda doc: uregseth()
    ssetter = lambda doc: sset()
    fssetter = lambda doc: fsset()
    sregsetter = lambda doc: sregset()
    nregsetter = lambda doc: nregset()
    sregsetterh = lambda doc: sregseth()
    nusetter = lambda doc: nuset()
    usetter = lambda doc: uset()
    twsetter = lambda doc: twset()
    delegsetter = lambda doc: delegset()

    schema_yaml['sstatus']['default_setter'] = sregsetter
    schema_yaml['sstatus']['schema']['rv32']['schema']['uie'][
        'default_setter'] = nusetter
    schema_yaml['sstatus']['schema']['rv64']['schema']['uie'][
        'default_setter'] = nusetter
    schema_yaml['sstatus']['schema']['rv32']['schema']['upie'][
        'default_setter'] = nusetter
    schema_yaml['sstatus']['schema']['rv64']['schema']['upie'][
        'default_setter'] = nusetter

    schema_yaml['sstatus']['schema']['rv64']['schema']['uxl'][
        'default_setter'] = usetter
    schema_yaml['sstatus']['schema']['rv32']['schema']['sie'][
        'default_setter'] = ssetter
    schema_yaml['sstatus']['schema']['rv64']['schema']['sie'][
        'default_setter'] = ssetter
    schema_yaml['sstatus']['schema']['rv32']['schema']['spie'][
        'default_setter'] = ssetter
    schema_yaml['sstatus']['schema']['rv64']['schema']['spie'][
        'default_setter'] = ssetter
    schema_yaml['sstatus']['schema']['rv32']['schema']['spp'][
        'default_setter'] = ssetter
    schema_yaml['sstatus']['schema']['rv64']['schema']['spp'][
        'default_setter'] = ssetter
    schema_yaml['sstatus']['schema']['rv32']['schema']['mxr'][
        'default_setter'] = ssetter
    schema_yaml['sstatus']['schema']['rv64']['schema']['mxr'][
        'default_setter'] = ssetter
    schema_yaml['sstatus']['schema']['rv32']['schema']['sum'][
        'default_setter'] = ssetter
    schema_yaml['sstatus']['schema']['rv64']['schema']['sum'][
        'default_setter'] = ssetter
    schema_yaml['sstatus']['schema']['rv32']['schema']['fs'][
        'default_setter'] = fssetter
    schema_yaml['sstatus']['schema']['rv64']['schema']['fs'][
        'default_setter'] = fssetter
    schema_yaml['sstatus']['schema']['rv32']['schema']['sd'][
        'default_setter'] = fssetter
    schema_yaml['sstatus']['schema']['rv64']['schema']['sd'][
        'default_setter'] = fssetter
    schema_yaml['sie']['default_setter'] = sregsetter
    schema_yaml['sie']['schema']['rv32']['schema']['ueie'][
        'default_setter'] = nusetter
    schema_yaml['sie']['schema']['rv64']['schema']['ueie'][
        'default_setter'] = nusetter
    schema_yaml['sie']['schema']['rv32']['schema']['utie'][
        'default_setter'] = nusetter
    schema_yaml['sie']['schema']['rv64']['schema']['utie'][
        'default_setter'] = nusetter
    schema_yaml['sie']['schema']['rv32']['schema']['usie'][
        'default_setter'] = nusetter
    schema_yaml['sie']['schema']['rv64']['schema']['usie'][
        'default_setter'] = nusetter
    schema_yaml['sie']['schema']['rv32']['schema']['seie'][
        'default_setter'] = ssetter
    schema_yaml['sie']['schema']['rv64']['schema']['seie'][
        'default_setter'] = ssetter
    schema_yaml['sie']['schema']['rv32']['schema']['stie'][
        'default_setter'] = ssetter
    schema_yaml['sie']['schema']['rv64']['schema']['stie'][
        'default_setter'] = ssetter
    schema_yaml['sie']['schema']['rv32']['schema']['ssie'][
        'default_setter'] = ssetter
    schema_yaml['sie']['schema']['rv64']['schema']['ssie'][
        'default_setter'] = ssetter
    schema_yaml['sip']['default_setter'] = sregsetter
    schema_yaml['sip']['schema']['rv32']['schema']['ueip'][
        'default_setter'] = nusetter
    schema_yaml['sip']['schema']['rv64']['schema']['ueip'][
        'default_setter'] = nusetter
    schema_yaml['sip']['schema']['rv32']['schema']['utip'][
        'default_setter'] = nusetter
    schema_yaml['sip']['schema']['rv64']['schema']['utip'][
        'default_setter'] = nusetter
    schema_yaml['sip']['schema']['rv32']['schema']['usip'][
        'default_setter'] = nusetter
    schema_yaml['sip']['schema']['rv64']['schema']['usip'][
        'default_setter'] = nusetter
    schema_yaml['sip']['schema']['rv32']['schema']['seip'][
        'default_setter'] = ssetter
    schema_yaml['sip']['schema']['rv64']['schema']['seip'][
        'default_setter'] = ssetter
    schema_yaml['sip']['schema']['rv32']['schema']['stip'][
        'default_setter'] = ssetter
    schema_yaml['sip']['schema']['rv64']['schema']['stip'][
        'default_setter'] = ssetter
    schema_yaml['sip']['schema']['rv32']['schema']['ssip'][
        'default_setter'] = ssetter
    schema_yaml['sip']['schema']['rv64']['schema']['ssip'][
        'default_setter'] = ssetter
    schema_yaml['stvec']['default_setter'] = sregsetter
    schema_yaml['stvec']['schema']['rv32']['schema']['base'][
        'default_setter'] = ssetter
    schema_yaml['stvec']['schema']['rv64']['schema']['base'][
        'default_setter'] = ssetter
    schema_yaml['stvec']['schema']['rv32']['schema']['mode'][
        'default_setter'] = ssetter
    schema_yaml['stvec']['schema']['rv64']['schema']['mode'][
        'default_setter'] = ssetter
        
    schema_yaml['sepc']['default_setter'] = sregsetter
    schema_yaml['stval']['default_setter'] = sregsetter
    schema_yaml['scause']['default_setter'] = sregsetter
    schema_yaml['scause']['schema']['rv32']['schema']['interrupt'][
        'default_setter'] = ssetter
    schema_yaml['scause']['schema']['rv64']['schema']['interrupt'][
        'default_setter'] = ssetter
    schema_yaml['scause']['schema']['rv32']['schema']['exception_code'][
        'default_setter'] = ssetter
    schema_yaml['scause']['schema']['rv64']['schema']['exception_code'][
        'default_setter'] = ssetter
    schema_yaml['satp']['default_setter'] = sregsetter
    schema_yaml['satp']['schema']['rv32']['schema']['ppn'][
        'default_setter'] = ssetter
    schema_yaml['satp']['schema']['rv64']['schema']['ppn'][
        'default_setter'] = ssetter
    schema_yaml['satp']['schema']['rv32']['schema']['asid'][
        'default_setter'] = ssetter
    schema_yaml['satp']['schema']['rv64']['schema']['asid'][
        'default_setter'] = ssetter
    schema_yaml['satp']['schema']['rv32']['schema']['mode'][
        'default_setter'] = ssetter
    schema_yaml['satp']['schema']['rv64']['schema']['mode'][
        'default_setter'] = ssetter
    schema_yaml['sscratch']['default_setter'] = sregsetter
    
    schema_yaml['ustatus']['default_setter'] = nregsetter
    schema_yaml['ustatus']['schema']['rv32']['schema']['uie'][
        'default_setter'] = nusetter
    schema_yaml['ustatus']['schema']['rv64']['schema']['uie'][
        'default_setter'] = nusetter
    schema_yaml['ustatus']['schema']['rv32']['schema']['upie'][
        'default_setter'] = nusetter
    schema_yaml['ustatus']['schema']['rv64']['schema']['upie'][
        'default_setter'] = nusetter

    schema_yaml['uie']['default_setter'] = nregsetter
    schema_yaml['uie']['schema']['rv32']['schema']['ueie'][
        'default_setter'] = nusetter
    schema_yaml['uie']['schema']['rv64']['schema']['ueie'][
        'default_setter'] = nusetter
    schema_yaml['uie']['schema']['rv32']['schema']['utie'][
        'default_setter'] = nusetter
    schema_yaml['uie']['schema']['rv64']['schema']['utie'][
        'default_setter'] = nusetter
    schema_yaml['uie']['schema']['rv32']['schema']['usie'][
        'default_setter'] = nusetter
    schema_yaml['uie']['schema']['rv64']['schema']['usie'][
        'default_setter'] = nusetter
    schema_yaml['uip']['default_setter'] = nregsetter
    schema_yaml['uip']['schema']['rv32']['schema']['ueip'][
        'default_setter'] = nusetter
    schema_yaml['uip']['schema']['rv64']['schema']['ueip'][
        'default_setter'] = nusetter
    schema_yaml['uip']['schema']['rv32']['schema']['utip'][
        'default_setter'] = nusetter
    schema_yaml['uip']['schema']['rv64']['schema']['utip'][
        'default_setter'] = nusetter
    schema_yaml['uip']['schema']['rv32']['schema']['usip'][
        'default_setter'] = nusetter
    schema_yaml['uip']['schema']['rv64']['schema']['usip'][
        'default_setter'] = nusetter
    schema_yaml['utvec']['default_setter'] = nregsetter
    schema_yaml['utvec']['schema']['rv32']['schema']['base'][
        'default_setter'] = nusetter
    schema_yaml['utvec']['schema']['rv64']['schema']['base'][
        'default_setter'] = nusetter
    schema_yaml['utvec']['schema']['rv32']['schema']['mode'][
        'default_setter'] = nusetter
    schema_yaml['utvec']['schema']['rv64']['schema']['mode'][
        'default_setter'] = nusetter
    schema_yaml['uepc']['default_setter'] = nregsetter
    schema_yaml['utval']['default_setter'] = nregsetter
    schema_yaml['ucause']['default_setter'] = nregsetter
    schema_yaml['ucause']['schema']['rv32']['schema']['interrupt'][
        'default_setter'] = nusetter
    schema_yaml['ucause']['schema']['rv64']['schema']['interrupt'][
        'default_setter'] = nusetter
    schema_yaml['ucause']['schema']['rv32']['schema']['exception_code'][
        'default_setter'] = nusetter
    schema_yaml['ucause']['schema']['rv64']['schema']['exception_code'][
        'default_setter'] = nusetter
    schema_yaml['uscratch']['default_setter'] = nregsetter

    schema_yaml['misa']['default_setter'] = regsetter
    schema_yaml['misa']['schema']['reset-val']['default_setter'] = resetsetter
    schema_yaml['mstatus']['default_setter'] = regsetter
    schema_yaml['mstatus']['schema']['reset-val']['default_setter']=reset_susetter
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
    schema_yaml['mcycle']['default_setter'] = regsetter
    schema_yaml['minstret']['default_setter'] = regsetter
    schema_yaml['mcycleh']['default_setter'] = counthsetter
    schema_yaml['minstreth']['default_setter'] = counthsetter
    schema_yaml['pmpcfg0']['default_setter'] = pmpregsetter
    schema_yaml['pmpcfg1']['default_setter'] = pmpcounthsetter
    schema_yaml['pmpcfg2']['default_setter'] = pmpregsetter
    schema_yaml['pmpcfg3']['default_setter'] = pmpcounthsetter
    schema_yaml['pmpcfg4']['default_setter'] = pmpregsetter
    schema_yaml['pmpcfg5']['default_setter'] = pmpcounthsetter
    schema_yaml['pmpcfg6']['default_setter'] = pmpregsetter
    schema_yaml['pmpcfg7']['default_setter'] = pmpcounthsetter
    schema_yaml['pmpcfg8']['default_setter'] = pmpregsetter
    schema_yaml['pmpcfg9']['default_setter'] = pmpcounthsetter
    schema_yaml['pmpcfg10']['default_setter'] = pmpregsetter
    schema_yaml['pmpcfg11']['default_setter'] = pmpcounthsetter
    schema_yaml['pmpcfg12']['default_setter'] = pmpregsetter
    schema_yaml['pmpcfg13']['default_setter'] = pmpcounthsetter
    schema_yaml['pmpcfg14']['default_setter'] = pmpregsetter
    schema_yaml['pmpcfg15']['default_setter'] = pmpcounthsetter
    schema_yaml['pmpaddr0']['default_setter'] = pmpregsetter
    schema_yaml['pmpaddr1']['default_setter'] = pmpregsetter
    schema_yaml['pmpaddr2']['default_setter'] = pmpregsetter
    schema_yaml['pmpaddr3']['default_setter'] = pmpregsetter
    schema_yaml['pmpaddr4']['default_setter'] = pmpregsetter
    schema_yaml['pmpaddr5']['default_setter'] = pmpregsetter
    schema_yaml['pmpaddr6']['default_setter'] = pmpregsetter
    schema_yaml['pmpaddr7']['default_setter'] = pmpregsetter
    schema_yaml['pmpaddr8']['default_setter'] = pmpregsetter
    schema_yaml['pmpaddr9']['default_setter'] = pmpregsetter
    schema_yaml['pmpaddr10']['default_setter'] = pmpregsetter
    schema_yaml['pmpaddr11']['default_setter'] = pmpregsetter
    schema_yaml['pmpaddr12']['default_setter'] = pmpregsetter
    schema_yaml['pmpaddr13']['default_setter'] = pmpregsetter
    schema_yaml['pmpaddr14']['default_setter'] = pmpregsetter
    schema_yaml['pmpaddr15']['default_setter'] = pmpregsetter
    schema_yaml['pmpaddr16']['default_setter'] = pmpregsetter
    schema_yaml['pmpaddr17']['default_setter'] = pmpregsetter
    schema_yaml['pmpaddr18']['default_setter'] = pmpregsetter
    schema_yaml['pmpaddr19']['default_setter'] = pmpregsetter
    schema_yaml['pmpaddr20']['default_setter'] = pmpregsetter
    schema_yaml['pmpaddr21']['default_setter'] = pmpregsetter
    schema_yaml['pmpaddr22']['default_setter'] = pmpregsetter
    schema_yaml['pmpaddr23']['default_setter'] = pmpregsetter
    schema_yaml['pmpaddr24']['default_setter'] = pmpregsetter
    schema_yaml['pmpaddr25']['default_setter'] = pmpregsetter
    schema_yaml['pmpaddr26']['default_setter'] = pmpregsetter
    schema_yaml['pmpaddr27']['default_setter'] = pmpregsetter
    schema_yaml['pmpaddr28']['default_setter'] = pmpregsetter
    schema_yaml['pmpaddr29']['default_setter'] = pmpregsetter
    schema_yaml['pmpaddr30']['default_setter'] = pmpregsetter
    schema_yaml['pmpaddr31']['default_setter'] = pmpregsetter
    schema_yaml['pmpaddr32']['default_setter'] = pmpregsetter
    schema_yaml['pmpaddr33']['default_setter'] = pmpregsetter
    schema_yaml['pmpaddr34']['default_setter'] = pmpregsetter
    schema_yaml['pmpaddr35']['default_setter'] = pmpregsetter
    schema_yaml['pmpaddr36']['default_setter'] = pmpregsetter
    schema_yaml['pmpaddr37']['default_setter'] = pmpregsetter
    schema_yaml['pmpaddr38']['default_setter'] = pmpregsetter
    schema_yaml['pmpaddr39']['default_setter'] = pmpregsetter
    schema_yaml['pmpaddr40']['default_setter'] = pmpregsetter
    schema_yaml['pmpaddr41']['default_setter'] = pmpregsetter
    schema_yaml['pmpaddr42']['default_setter'] = pmpregsetter
    schema_yaml['pmpaddr43']['default_setter'] = pmpregsetter
    schema_yaml['pmpaddr44']['default_setter'] = pmpregsetter
    schema_yaml['pmpaddr45']['default_setter'] = pmpregsetter
    schema_yaml['pmpaddr46']['default_setter'] = pmpregsetter
    schema_yaml['pmpaddr47']['default_setter'] = pmpregsetter
    schema_yaml['pmpaddr48']['default_setter'] = pmpregsetter
    schema_yaml['pmpaddr49']['default_setter'] = pmpregsetter
    schema_yaml['pmpaddr50']['default_setter'] = pmpregsetter
    schema_yaml['pmpaddr51']['default_setter'] = pmpregsetter
    schema_yaml['pmpaddr52']['default_setter'] = pmpregsetter
    schema_yaml['pmpaddr53']['default_setter'] = pmpregsetter
    schema_yaml['pmpaddr54']['default_setter'] = pmpregsetter
    schema_yaml['pmpaddr55']['default_setter'] = pmpregsetter
    schema_yaml['pmpaddr56']['default_setter'] = pmpregsetter
    schema_yaml['pmpaddr57']['default_setter'] = pmpregsetter
    schema_yaml['pmpaddr58']['default_setter'] = pmpregsetter
    schema_yaml['pmpaddr59']['default_setter'] = pmpregsetter
    schema_yaml['pmpaddr60']['default_setter'] = pmpregsetter
    schema_yaml['pmpaddr61']['default_setter'] = pmpregsetter
    schema_yaml['pmpaddr62']['default_setter'] = pmpregsetter
    schema_yaml['pmpaddr63']['default_setter'] = pmpregsetter

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
    schema_yaml['hpmcounter3']['default_setter'] = uregsetter
    schema_yaml['hpmcounter3h']['default_setter'] = ureghsetter
    schema_yaml['hpmcounter4']['default_setter'] = uregsetter
    schema_yaml['hpmcounter4h']['default_setter'] = ureghsetter
    schema_yaml['hpmcounter5']['default_setter'] = uregsetter
    schema_yaml['hpmcounter5h']['default_setter'] = ureghsetter
    schema_yaml['hpmcounter6']['default_setter'] = uregsetter
    schema_yaml['hpmcounter6h']['default_setter'] = ureghsetter
    schema_yaml['hpmcounter7']['default_setter'] = uregsetter
    schema_yaml['hpmcounter7h']['default_setter'] = ureghsetter
    schema_yaml['hpmcounter8']['default_setter'] = uregsetter
    schema_yaml['hpmcounter8h']['default_setter'] = ureghsetter
    schema_yaml['hpmcounter9']['default_setter'] = uregsetter
    schema_yaml['hpmcounter9h']['default_setter'] = ureghsetter
    schema_yaml['hpmcounter10']['default_setter'] = uregsetter
    schema_yaml['hpmcounter10h']['default_setter'] = ureghsetter
    schema_yaml['hpmcounter11']['default_setter'] = uregsetter
    schema_yaml['hpmcounter11h']['default_setter'] = ureghsetter
    schema_yaml['hpmcounter12']['default_setter'] = uregsetter
    schema_yaml['hpmcounter12h']['default_setter'] = ureghsetter
    schema_yaml['hpmcounter13']['default_setter'] = uregsetter
    schema_yaml['hpmcounter13h']['default_setter'] = ureghsetter
    schema_yaml['hpmcounter14']['default_setter'] = uregsetter
    schema_yaml['hpmcounter14h']['default_setter'] = ureghsetter
    schema_yaml['hpmcounter15']['default_setter'] = uregsetter
    schema_yaml['hpmcounter15h']['default_setter'] = ureghsetter
    schema_yaml['hpmcounter16']['default_setter'] = uregsetter
    schema_yaml['hpmcounter16h']['default_setter'] = ureghsetter
    schema_yaml['hpmcounter17']['default_setter'] = uregsetter
    schema_yaml['hpmcounter17h']['default_setter'] = ureghsetter
    schema_yaml['hpmcounter18']['default_setter'] = uregsetter
    schema_yaml['hpmcounter18h']['default_setter'] = ureghsetter
    schema_yaml['hpmcounter19']['default_setter'] = uregsetter
    schema_yaml['hpmcounter19h']['default_setter'] = ureghsetter
    schema_yaml['hpmcounter20']['default_setter'] = uregsetter
    schema_yaml['hpmcounter20h']['default_setter'] = ureghsetter
    schema_yaml['hpmcounter21']['default_setter'] = uregsetter
    schema_yaml['hpmcounter21h']['default_setter'] = ureghsetter
    schema_yaml['hpmcounter22']['default_setter'] = uregsetter
    schema_yaml['hpmcounter22h']['default_setter'] = ureghsetter
    schema_yaml['hpmcounter23']['default_setter'] = uregsetter
    schema_yaml['hpmcounter23h']['default_setter'] = ureghsetter
    schema_yaml['hpmcounter24']['default_setter'] = uregsetter
    schema_yaml['hpmcounter24h']['default_setter'] = ureghsetter
    schema_yaml['hpmcounter25']['default_setter'] = uregsetter
    schema_yaml['hpmcounter25h']['default_setter'] = ureghsetter
    schema_yaml['hpmcounter26']['default_setter'] = uregsetter
    schema_yaml['hpmcounter26h']['default_setter'] = ureghsetter
    schema_yaml['hpmcounter27']['default_setter'] = uregsetter
    schema_yaml['hpmcounter27h']['default_setter'] = ureghsetter
    schema_yaml['hpmcounter28']['default_setter'] = uregsetter
    schema_yaml['hpmcounter28h']['default_setter'] = ureghsetter
    schema_yaml['hpmcounter29']['default_setter'] = uregsetter
    schema_yaml['hpmcounter29h']['default_setter'] = ureghsetter
    schema_yaml['hpmcounter30']['default_setter'] = uregsetter
    schema_yaml['hpmcounter30h']['default_setter'] = ureghsetter
    schema_yaml['hpmcounter31']['default_setter'] = uregsetter
    schema_yaml['hpmcounter31h']['default_setter'] = ureghsetter

    schema_yaml['mcounteren']['default_setter'] = uregsetter
    schema_yaml['scounteren']['default_setter'] = uregsetter

    schema_yaml['mcause']['default_setter'] = regsetter
    schema_yaml['mstatus']['schema']['rv32']['schema']['uie'][
        'default_setter'] = nusetter
    schema_yaml['mstatus']['schema']['rv64']['schema']['uie'][
        'default_setter'] = nusetter
    schema_yaml['mstatus']['schema']['rv32']['schema']['upie'][
        'default_setter'] = nusetter
    schema_yaml['mstatus']['schema']['rv64']['schema']['upie'][
        'default_setter'] = nusetter

    schema_yaml['mstatus']['schema']['rv32']['schema']['mprv'][
        'default_setter'] = ssetter
    schema_yaml['mstatus']['schema']['rv64']['schema']['mprv'][
        'default_setter'] = ssetter
    schema_yaml['mstatus']['schema']['rv64']['schema']['uxl'][
        'default_setter'] = usetter
    schema_yaml['fflags']['default_setter'] = uregsetter
    schema_yaml['frm']['default_setter'] = uregsetter
    schema_yaml['fcsr']['default_setter'] = uregsetter
    schema_yaml['time']['default_setter'] = uregsetter
    schema_yaml['timeh']['default_setter'] = ureghsetter
    schema_yaml['cycle']['default_setter'] = uregsetter
    schema_yaml['cycleh']['default_setter'] = ureghsetter
    schema_yaml['instret']['default_setter'] = uregsetter
    schema_yaml['instreth']['default_setter'] = ureghsetter

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

    schema_yaml['mstatus']['schema']['rv32']['schema']['sie'][
        'default_setter'] = ssetter
    schema_yaml['mstatus']['schema']['rv64']['schema']['sie'][
        'default_setter'] = ssetter
    schema_yaml['mstatus']['schema']['rv32']['schema']['fs'][
        'default_setter'] = fssetter
    schema_yaml['mstatus']['schema']['rv64']['schema']['fs'][
        'default_setter'] = fssetter
    schema_yaml['mstatus']['schema']['rv32']['schema']['sd'][
        'default_setter'] = fssetter
    schema_yaml['mstatus']['schema']['rv64']['schema']['sd'][
        'default_setter'] = fssetter
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
    schema_yaml['mstatus']['schema']['rv32']['schema']['tw'][
        'default_setter'] = twsetter
    schema_yaml['mstatus']['schema']['rv64']['schema']['tw'][
        'default_setter'] = twsetter
    schema_yaml['medeleg']['default_setter'] = delegsetter
    schema_yaml['mideleg']['default_setter'] = delegsetter
    schema_yaml['sedeleg']['default_setter'] = nregsetter
    schema_yaml['sideleg']['default_setter'] = nregsetter
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
                    set(['description', 'msb', 'lsb', 'implemented', 'shadow', 'shadow_type'])
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
        set(['fields', 'msb', 'lsb', 'accessible', 'shadow', 'shadow_type','type']))

    if not fields:
        return fields
    nf = {}
    for x in fields:
        nf[x] = node[x]['lsb']
    nf = sorted(nf.items(), key=lambda x: x[1], reverse=False)
    nfields=[]
    for k, v in nf:
        nfields.append(k)

    fields = nfields
    bits = set(range(bitwidth))
    for entry in fields:
        bits -= set(range(node[entry]['lsb'], node[entry]['msb'] + 1))
    bits = list(groupc(sorted(list(bits))))
    if not bits:
        return fields
    else:
        fields.append(bits)
        return fields
        
def check_fields(spec):
    errors = {} 
    for csr, node, in spec.items() :
         fault_node = node
         error=[]
         if node['rv32']['accessible']:
                node['rv32']['fields'] = get_fields(node['rv32'], 32)
         if node['rv64']['accessible']:
                node['rv64']['fields'] = get_fields(node['rv64'], 64)
         fields = list(set(['rv32', 'rv64', 'description', 'address', 'priv_mode', 'reset-val']) - set(node.keys()) )
         if fields:
            error.append("The fields " + "".join(fields) + " are missing")
         if node['rv32']['accessible']:
            if any(type(e)==list for e in node['rv32']['fields']): 
             sub_fields = node['rv32']['fields'][:-1]
            else:
             sub_fields = node['rv32']['fields']
            if not sub_fields :
             subfields = list(set(['msb', 'lsb', 'accessible', 'shadow', 'shadow_type', 'fields', 'type']) - set(node['rv32'].keys()) )    
             if subfields:
                error.append("The subfield " + "".join(subfields) + " are not present")         
            else:
              for x in sub_fields :
                subfields = list(set(['msb', 'lsb', 'implemented', 'description', 'shadow', 'shadow_type', 'type']) - set(node['rv32'][x].keys()) )
                if subfields :                   
                   error.append("The subfields " + "".join(subfields) + " are not present in " + str(x))
         if node['rv64']['accessible']:            
            if any(type(e)==list for e in node['rv64']['fields']): 
             sub_fields = node['rv64']['fields'][:-1]
            else:
             sub_fields = node['rv64']['fields']
            if not sub_fields :
             subfields = list(set(['msb', 'lsb', 'accessible', 'fields', 'shadow', 'shadow_type', 'type']) - set(node['rv64'].keys()))
             if subfields:
                error.append("The subfield " + "".join(subfields) + " are not present")
            else:
              for x in sub_fields :
                subfields = list(set(['msb', 'lsb', 'implemented', 'description', 'shadow', 'shadow_type', 'type']) - set(node['rv64'][x].keys()) )
                if subfields :                   
                   error.append("The subfields " + "".join(subfields) + " are not present in " + str(x))
         if bin(node['address'])[2:][::-1][6:8] != '11' and bin(node['address'])[2:][::-1][8:12] != '0001':
             error.append('Address is not in custom csr ranges')
         if (bin(node['address'])[2:][::-1][8:10] == '00' and node['priv_mode'] != 'U' ) or (bin(node['address'])[2:][::-1][8:10] == '01' and node['priv_mode'] != 'S' ) or (bin(node['address'])[2:][::-1][8:10] == '11' and node['priv_mode'] != 'M') :
            error.append('Privilege does not match with the address')
         if error:
            errors[csr] = error
    return errors 
def check_shadows(spec, logging = False):
    ''' Check if the shadowed fields are implemented and of the same size as the
    source'''
    errors = {}
    _rvxlen = ['rv32', 'rv64']
    for csr, content in spec.items():
        if logging:
            logger.debug('Checking Shadows for ' + csr)
        error = []
        if isinstance(content, dict) and 'description' in content:
            for rvxlen in _rvxlen:
                if content[rvxlen]['accessible'] and not content[rvxlen]['fields']:
                    if content[rvxlen]['shadow'] is None: 
                        continue
                    else:
                        shadow = content[rvxlen]['shadow'].split('.')
                        if len(shadow) != 1:
                            error.append('Shadow field of should not have dot')
                            continue
                        else:
                            scsr = shadow[0]
                            if not spec[scsr][rvxlen]['accessible']:
                                error.append('Shadow field ' + scsr + ' not implemented')
                                continue
                            scsr_size = spec[scsr][rvxlen]['msb'] - spec[scsr][rvxlen]['lsb']
                            csr_size = spec[csr][rvxlen]['msb'] - spec[csr][rvxlen]['lsb']
                            if scsr_size != csr_size :
                                error.append('Shadow field '+ scsr +\
                                        'does not match in size') 
                elif content[rvxlen]['accessible']:
                    for subfield in content[rvxlen]['fields']:
                        if isinstance(subfield ,list):
                            continue
                        if content[rvxlen][subfield]['shadow'] is None:
                           continue
                        elif content[rvxlen][subfield]['implemented']:
                            shadow = content[rvxlen][subfield]['shadow'].split('.')
                            if len(shadow) != 2:
                                error.append('Shadow field of should only 1 dot')
                                continue
                            else:
                                scsr = shadow[0]
                                subscsr = shadow[1]
                                if not spec[scsr][rvxlen][subscsr]['implemented']:
                                    error.append('Subfield ' + subfield + \
                                            ' shadowing ' + scsr + '.' +\
                                            subscsr + ' not implemented')
                                    continue
                                scsr_size = spec[scsr][rvxlen][subscsr]['msb'] -\
                                        spec[scsr][rvxlen][subfield]['lsb']
                                csr_size = spec[csr][rvxlen][subfield]['msb'] -\
                                        spec[csr][rvxlen][subfield]['lsb']
                                if scsr_size != csr_size :
                                    error.append('Subfield ' + subfield +'shadowing'+ \
                                            scsr + '.' + subscsr + \
                                            ' does not match in size') 

        if error:
            errors[csr] = error
    return errors

def check_mhpm(spec, logging = False):
    ''' Check if the mhpmcounters and corresponding mhpmevents are implemented and of the same size as the
    source'''
    errors = {}
    for csrname, content, in spec.items():
        error = []
        if 'mhpmcounter' in csrname:
            index = int(re.findall('\d+',csrname.lower())[0])
            if content['rv64']['accessible'] :
                if not spec['mhpmevent'+str(index)]['rv64']['accessible']:
                    error.append(csrname + " counter doesn't have the corresponding mhpmevent register accessible")
            if content['rv32']['accessible'] :
                if not spec['mhpmevent'+str(index)]['rv32']['accessible']:
                    error.append(csrname + " counter doesn't have the corresponding mhpmevent register accessible")
        if 'mhpmevent' in csrname:
            index = int(re.findall('\d+',csrname.lower())[0])
            if content['rv64']['accessible'] :
                if not spec['mhpmcounter'+str(index)]['rv64']['accessible']:
                    error.append(csrname + " event reg doesn't have the corresponding mhpmcounter register accessible")
            if content['rv32']['accessible'] :
                if not spec['mhpmcounter'+str(index)]['rv32']['accessible']:
                    error.append(csrname + " event reg doesn't have the corresponding mhpmcounter register accessible")
            if content['rv32']['accessible'] :
                if not spec['mhpmcounter'+str(index)+'h']['rv32']['accessible']:
                    error.append(csrname + " event reg doesn't have the corresponding mhpmcounter 'h' counterpart register accessible")
        if error:
            errors[csrname] = error
    return errors
    
     
def check_pmp(spec, logging = False):
    ''' Check if the mhpmcounters and corresponding mhpmevents are implemented and of the same size as the
    source'''
    errors = {}
    for csrname, content, in spec.items():
        error = []
        Grain=int(spec['pmp_granularity'])
        if 'pmpaddr' in csrname:
            index = int(re.findall('\d+',csrname.lower())[0])
            if content['rv64']['accessible'] :                
                reset_val_addr = (bin(content['reset-val'])[2:].zfill(64))[::-1] 
                reset_val_cfg  = (bin(spec['pmpcfg'+str(int(int(index/8)*2))]['reset-val'])[2:].zfill(64))[::-1]
                if not spec['pmpcfg'+str(int(int(index/8)*2))]['rv64']['accessible']:
                    error.append(csrname + " addr doesn't have the corresponding pmp config register accessible")
                if not spec['pmpcfg'+str(int(int(index/8)*2))]['rv64']['pmp'+str(index)+'cfg']['implemented'] :
                    error.append(csrname + " addr doesn't have the corresponding pmpcfg" +str(int(index/4)) + "_pmp" + str(index) +"cfg register implemented")
                if reset_val_cfg[8*(index-(int(index/8)*8)) + 4] == '1' and Grain >=2 :     #NAPOT, Bit A of pmpXcfg is set
                  if '0' in reset_val_addr[0:(Grain-1)] or (reset_val_addr[Grain-1] != '0') :
                    error.append(csrname + 'reset value does not adhere with the pmp granularity')
                elif Grain >= 1: #TOR
                  if int(content['reset-val']) % (2**Grain) != 0 :
                    error.append(csrname + 'reset value does not adhere with the pmp granularity')
            if content['rv32']['accessible'] :
                reset_val_addr = (bin(content['reset-val'])[2:].zfill(32))[::-1] 
                reset_val_cfg  = (bin(spec['pmpcfg'+str(int(index/4))]['reset-val'])[2:].zfill(32))[::-1]
                if not spec['pmpcfg'+str(int(index/4))]['rv32']['accessible']:
                    error.append(csrname + " addr doesn't have the corresponding pmp config register accessible")
                if not spec['pmpcfg'+str(int(index/4))]['rv32']['pmp'+str(index)+'cfg']['implemented'] :
                    error.append(csrname + " addr doesn't have the corresponding pmpcfg" +str(int(index/4)) + "_pmp" + str(index) +"cfg register implemented")
                if reset_val_cfg[8*(index-(int(index/4)*4)) + 4] == '1' and Grain >=2 :     #NAPOT, Bit A of pmpXcfg is set
                 if '0' in reset_val_addr[0:(Grain-1)] or (reset_val_addr[Grain-1] != '0') :
                    error.append(csrname + 'reset value does not adhere with the pmp granularity')
                elif Grain >= 1: #TOR
                  if int(content['reset-val']) % (2**Grain) != 0 :
                    error.append(csrname + 'reset value does not adhere with the pmp granularity')
        if 'pmpcfg' in csrname:
            if content['rv64']['accessible'] :
                for subfield in content['rv64']['fields']:
                 index = int(re.findall('\d+',subfield)[0])
                 if content['rv64'][subfield]['implemented'] and not spec['pmpaddr'+str(index)]['rv64']['accessible']:
                    error.append(csrname + "_" + subfield + " doesn't have the corresponding pmpaddr accessible")
            if content['rv32']['accessible'] :
                for subfield in content['rv32']['fields']:
                 index = int(re.findall('\d+',subfield)[0])
                 if content['rv32'][subfield]['implemented'] and not spec['pmpaddr'+str(index)]['rv32']['accessible']:
                    error.append(csrname + "_" + subfield + " doesn't have the corresponding pmpaddr accessible")
        if error:
            errors[csrname] = error
    return errors
   





def check_reset_fill_fields(spec, logging= False):
    '''The check_reset_fill_fields function fills the field node with the names of the sub-fields of the register and then checks whether the reset-value of the register is a legal value. To do so, it iterates over all the subfields and extracts the corresponding field value from the reset-value. Then it checks the legality of the value according to the given field description. If the fields is implemented i.e accessible in both 64 bit and 32 bit modes, the 64 bit mode is given preference. '''
    errors = {}
    for node in spec:

        if isinstance(spec[node], dict):
            if logging:
                logger.debug('Checking Reset fields for: ' +  node)
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
                    if field_desc['shadow'] is None:
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
                            if reset_val != desc['ro_constant']:
                                error.append(
                                    "Reset value doesnt match the 'ro_constant' description for the register."
                                )
                        elif 'ro_variable' in keys:
                            pass
                        elif "warl" in keys:
                            warl = (warl_interpreter(desc['warl']))
                            deps = warl.dependencies
                            dep_vals = []
                            for dep in deps:
                                reg = dep.split("::")
                                if len(reg) == 1:
                                    dep_vals.append(spec[reg[0]]['reset-val'])
                                else:
                                    bin_str = bin(spec[reg[0]]
                                                  ['reset-val'])[2:].zfill(bit_len)
                                    msb = spec[reg[0]]['rv{}'.format(bit_len)][reg[1]]['msb']
                                    lsb = spec[reg[0]]['rv{}'.format(bit_len)][reg[1]]['lsb']
                                    dep_vals.append(
                                        int(bin_str[::-1][lsb:msb+1][::-1], base=2))
                            if (warl.islegal(int(reset_val), dep_vals) != True):
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
                                if field_desc[field]['shadow'] is None:
                                    logger.debug('--> Subfield: ' + field)
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
                                        if test_val != desc['ro_constant']:
                                            error.append(
                                                "Reset value for " + field +
                                                " doesnt match the 'ro_constant' description."
                                            )
                                    elif 'ro_variable' in keys:
                                        pass
                                    elif "warl" in keys:
                                        warl = (warl_interpreter(desc['warl']))
                                        deps = warl.dependencies
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
                                                int(test_val), dep_vals) !=
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

def check_debug_specs(debug_spec, isa_spec,
                work_dir,
                logging=False,
                no_anchors=False):
    '''
        Function to perform ensure that the isa and debug specifications confirm
        to their schemas. The :py:mod:`Cerberus` module is used to validate that the
        specifications confirm to their respective schemas.


        :param debug_spec: The path to the DUT debug specification yaml file.

        :param isa_spec: The path to the DUT isa specification yaml file.

        :param logging: A boolean to indicate whether log is to be printed.

        :type logging: bool

        :type isa_spec: str

        :raise ValidationError: It is raised when the specifications violate the
            schema rules. It also contains the specific errors in each of the fields.

        :return: A tuple with the first entry being the absolute path to normalized isa file
            and the second being the absolute path to the platform spec file.
    '''

    if logging:
        logger.info('Input-Debug file')
    
    foo1 = isa_spec
    foo = debug_spec
    schema = constants.debug_schema
    """
      Read the input-isa foo (yaml file) and validate with schema-isa for feature values
      and constraints
    """
    # Load input YAML file
    if logging:
        logger.info('Loading input file: ' + str(foo))
    master_inp_debug_yaml = utils.load_yaml(foo, no_anchors)

    # Load input YAML file
    if logging:
        logger.info('Loading input isa file: ' + str(foo1))
    master_inp_yaml = utils.load_yaml(foo1, no_anchors)
    isa_string = master_inp_yaml['hart0']['ISA']
    
    # instantiate validator
    if logging:
        logger.info('Load Schema ' + str(schema))
    master_schema_yaml = utils.load_yaml(schema, no_anchors)

    outyaml = copy.deepcopy(master_inp_debug_yaml)
    for x in master_inp_debug_yaml['hart_ids']:
        if logging:
            logger.info('Processing Hart: hart'+str(x))
        inp_debug_yaml = master_inp_debug_yaml['hart'+str(x)]
        schema_yaml = add_debug_setters(master_schema_yaml['hart_schema']['schema'])
        #Extract xlen
        xlen = inp_debug_yaml['supported_xlen']

        validator = schemaValidator(schema_yaml, xlen=xlen, isa_string=isa_string)
        validator.allow_unknown = False
        validator.purge_readonly = True
        normalized = validator.normalized(inp_debug_yaml, schema_yaml)

        # Perform Validation
        if logging:
            logger.info('Initiating Validation')
        valid = validator.validate(normalized)

        # Print out errors
        if valid:
            if logging:
                logger.info('No errors for Hart: '+str(x) + ' :)')
        else:
            error_list = validator.errors
            raise ValidationError("Error in " + foo + ".", error_list)
        if logging:
            logger.info("Initiating post processing and reset value checks.")
        normalized, errors = check_reset_fill_fields(normalized, logging)
        if errors:
            raise ValidationError("Error in " + foo + ".", errors)
        outyaml['hart'+str(x)] = trim(normalized)
    file_name = os.path.split(foo)
    file_name_split = file_name[1].split('.')
    output_filename = os.path.join(
        work_dir, file_name_split[0] + '_checked.' + file_name_split[1])
    ifile = output_filename
    outfile = open(output_filename, 'w')
    if logging:
        logger.info('Dumping out Normalized Checked YAML: ' + output_filename)
    utils.dump_yaml(outyaml, outfile, no_anchors )
    return ifile
    
def check_isa_specs(isa_spec,
                work_dir,
                logging=False,
                no_anchors=False):
    '''
        Function to perform ensure that the isa and platform specifications confirm
        to their schemas. The :py:mod:`Cerberus` module is used to validate that the
        specifications confirm to their respective schemas.

        :param isa_spec: The path to the DUT isa specification yaml file.

        :param logging: A boolean to indicate whether log is to be printed.

        :type logging: bool

        :type isa_spec: str

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
    master_inp_yaml = utils.load_yaml(foo, no_anchors)

    # instantiate validator
    if logging:
        logger.info('Load Schema ' + str(schema))
    master_schema_yaml = utils.load_yaml(schema, no_anchors)

    outyaml = copy.deepcopy(master_inp_yaml)
    for x in master_inp_yaml['hart_ids']:
        if logging:
            logger.info('Processing Hart: hart'+str(x))
        inp_yaml = master_inp_yaml['hart'+str(x)]
        schema_yaml = add_def_setters(master_schema_yaml['hart_schema']['schema'])
        schema_yaml = add_reset_setters(master_schema_yaml['hart_schema']['schema']) 
        schema_yaml = add_fflags_type_setters(master_schema_yaml['hart_schema']['schema']) 
        #Extract xlen
        xlen = inp_yaml['supported_xlen']
        rvxlen='rv'+str(xlen[0])
        validator = schemaValidator(schema_yaml, xlen=xlen, isa_string=inp_yaml['ISA'])
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
                logger.info('No errors for Hart: '+str(x) + ' :)')
        else:
            error_list = validator.errors
            raise ValidationError("Error in " + foo + ".", error_list)
        if logging:
            logger.info("Initiating post processing and reset value checks.")
        normalized, errors = check_reset_fill_fields(normalized, logging)
        if errors:
            raise ValidationError("Error in " + foo + ".", errors)
        if normalized['mhartid']['reset-val'] != x:
            raise ValidationError('Error in ' + foo + ".", 
                    {'mhartid': ['wrong reset-val of for hart'+str(x)]})
        errors = check_shadows(normalized, logging)
        if errors:
            raise ValidationError("Error in " + foo + ".", errors)
        errors = check_mhpm(normalized, logging)
        if errors:
            raise ValidationError("Error in " + foo + ".", errors)
        errors = check_pmp(normalized, logging)
        if errors:
            raise ValidationError("Error in " + foo + ".", errors) 
              
        outyaml['hart'+str(x)] = trim(normalized)
    file_name = os.path.split(foo)
    file_name_split = file_name[1].split('.')
    output_filename = os.path.join(
        work_dir, file_name_split[0] + '_checked.' + file_name_split[1])
    ifile = output_filename
    outfile = open(output_filename, 'w')
    if logging:
        logger.info('Dumping out Normalized Checked YAML: ' + output_filename)
    utils.dump_yaml(outyaml, outfile, no_anchors )
    return ifile
    
def check_custom_specs(custom_spec,
                work_dir,
                logging=False,
                no_anchors=False):
    '''
        Function to perform ensure that the isa and platform specifications confirm
        to their schemas. The :py:mod:`Cerberus` module is used to validate that the
        specifications confirm to their respective schemas.

        :param isa_spec: The path to the DUT isa specification yaml file.

        :param logging: A boolean to indicate whether log is to be printed.

        :type logging: bool

        :type isa_spec: str

        :raise ValidationError: It is raised when the specifications violate the
            schema rules. It also contains the specific errors in each of the fields.

        :return: A tuple with the first entry being the absolute path to normalized isa file
            and the second being the absolute path to the platform spec file.
    '''
    if logging:
        logger.info('Custom CSR Spec')

    foo = custom_spec
    
    # Load input YAML file
    if logging:
        logger.info('Loading input file: ' + str(foo))
    master_custom_yaml = utils.load_yaml(foo, no_anchors)

    outyaml = copy.deepcopy(master_custom_yaml)
    for x in master_custom_yaml['hart_ids']:
        if logging:
            logger.info('Processing Hart: hart'+str(x))
        inp_yaml = master_custom_yaml['hart'+str(x)]
    errors = check_fields(inp_yaml)
    if errors:
            raise ValidationError("Error in " + foo + ".", errors)
    outyaml['hart'+str(x)] = trim(inp_yaml)
    file_name = os.path.split(foo)
    file_name_split = file_name[1].split('.')
    output_filename = os.path.join(
        work_dir, file_name_split[0] + '_checked.' + file_name_split[1])
    cfile = output_filename
    outfile = open(output_filename, 'w')
    if logging:
        logger.info('Dumping out Normalized Checked YAML: ' + output_filename)
    utils.dump_yaml(outyaml, outfile, no_anchors )
    return cfile
    
def check_platform_specs(platform_spec,
                work_dir,
                logging=False,
                no_anchors=False):
    foo = platform_spec
    schema = constants.platform_schema
    if logging:
        logger.info('Input-Platform file')
    """
      Read the input-platform foo (yaml file) and validate with schema-platform for feature values
      and constraints
    """
    # Load input YAML file
    if logging:
        logger.info('Loading input file: ' + str(foo))
    inp_yaml = utils.load_yaml(foo, no_anchors)
    if inp_yaml is None:
        inp_yaml = {'mtime': {'implemented': False}}

    # instantiate validator
    if logging:
        logger.info('Load Schema ' + str(schema))
    schema_yaml = utils.load_yaml(schema, no_anchors)
    validator = schemaValidator(schema_yaml, xlen=[])
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
    utils.dump_yaml(trim(normalized), outfile, no_anchors)

    return pfile
