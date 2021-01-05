import re
import os
import logging
import riscv_config.utils as utils

logger = logging.getLogger(__name__)

class warl_interpreter():
    global val
    global bitsum
    global dep_val

    def __init__(self, warl):
        ''' the warl_description in the yaml is given as input to the constructor '''
        self.warl = warl
        self.dependencies = warl['dependency_fields']
        self.exp  = re.compile('(?P<csr>.*?)\[(?P<csr_ind>.*?)\]\s*(?P<csr_op>.*?)\s*\[(?P<csr_vals>.*?)\]')
        self.rexp = re.compile('(?P<csr>.*?)\[(?P<csr_ind>.*?)\]\s*(in|bitmask)\s*\s*\[(?P<csr_vals>.*?)\]')
        self.rexp_dependencies = re.compile('(?P<dep_csr>.*?)\[(?P<dep_ind>.*?)\]\s*(in|bitmask)\s*\[(?P<dep_vals>.*?)\]\s*->\s*(?P<csr>.*?)\[(?P<csr_ind>.*?)\]\s*(in|bitmask)\s*\s*\[(?P<csr_vals>.*?)\]')

    def prevsum(self, i, k):
        sump = 0
        for j in range(i + 1):
            sump = sump + k[j]
        return sump

    def islegal(self, value, dependency_vals=[]):
        is_legal = False
        logger.debug('Checking for isLegal for WARL: \n\t' +
                utils.pretty_print_yaml(self.warl) + '\n With following args:'\
                        + 'val : ' + str(value) + ' dep_vals :'+
                        str(dependency_vals))
        if not self.dependencies: # no dependencies in the warl
            for legal_str in self.warl['legal']: # iterate over every legal str
                search = self.exp.findall(legal_str)
                if search is None:
                    logger.error('Warl legal string is wrong:' + legal_str)
                    raise SystemExit
                part_legal = False
                for part in search:
                    (csr, csr_ind, csr_op, csr_vals) = part
                    msb = int(csr_ind.split(':')[0])
                    lsb = int(csr_ind.split(':')[-1])
                    bitmask = True if 'bitmask' in csr_op else False
                    trunc_val = int(bin(value)[2:].zfill(64)[::-1][lsb:msb+1][::-1],base=2)

                    if not bitmask: # if its not a bitmask
                        if ":" in csr_vals: # range is specified
                            [base, bound] = csr_vals.split(':')
                            if 'x' in base:
                                base = int(base,16)
                            if 'x' in bound:
                                bound = int(bound,16)
                            if trunc_val >= base and trunc_val <= bound: # check legal range
                                part_legal = True
                        else:
                            l_vals = csr_vals.split(',')
                            legal_vals = []
                            for i in l_vals : 
                                legal_vals.append(int(i,16))
                            if trunc_val in legal_vals:
                                part_legal = True
                    else: # in case of bitmask there are no illegal values
                        part_legal = True
                    if not part_legal:
                        break
                if part_legal:
                    is_legal = True
        else: # there are dependencies
            if len(self.dependencies) != len(dependency_vals):
                logger.error('length of dependency_vals not the same as dependencies')
                raise SystemExit
            leaf_dependencies = []
            for d in self.dependencies:
                leaf_dependencies.append(d.split('::')[-1])
            for legal_str in self.warl['legal']: # iterate over legal str
                dep_str = legal_str.split('->')[0]
                csr_str = legal_str.split('->')[1]
                csr_search = self.exp.findall(csr_str)
                dep_search = self.exp.search(dep_str)
                if csr_search is None or dep_search  is None:
                    logger.error('Warl legal string is wrong :\n\t' + legal_str)
                    raise SystemExit
                dep_csr = dep_search.group('csr')
                dep_ind = dep_search.group('csr_ind')
                dep_vals = dep_search.group('csr_vals')
                dep_bitmask = True if 'bitmask' in legal_str.split('->')[0] else False

                if dep_csr not in leaf_dependencies:
                    logger.error(\
            'Found a dependency in the legal_str which is not present in the dependency_fields of the warl:\n\n' + \
                    utils.pretty_print_yaml(self.warl))
                    raise SystemExit
                dep_satified = False
                recvd_val = dependency_vals[leaf_dependencies.index(dep_csr)]

                # check if the dependency value is satisfied.
                if ":" in dep_vals: # range is specified
                    [base, bound] = dep_vals.split(':')
                    if 'x' in base:
                        base = int(base,16)
                    if 'x' in bound:
                        bound = int(bound,16)
                    if recvd_val >= base and recvd_val <= bound: # check legal range
                        dep_satified = True
                else:
                    l_vals = dep_vals.split(',')
                    legal_vals = []
                    for i in l_vals : 
                        legal_vals.append(int(i,16))
                    if recvd_val in legal_vals:
                        dep_satified = True
                
                part_legal = False
                for part in csr_search:
                    (csr, csr_ind, csr_op, csr_vals) = part
                    msb = int(csr_ind.split(':')[0])
                    lsb = int(csr_ind.split(':')[-1])
                    bitmask = True if 'bitmask' in csr_op else False
                    trunc_val = int(bin(value)[2:].zfill(64)[::-1][lsb:msb+1][::-1],base=2)

                    if not bitmask: # if its not a bitmask
                        if ":" in csr_vals: # range is specified
                            [base, bound] = csr_vals.split(':')
                            if 'x' in base:
                                base = int(base,16)
                            if 'x' in bound:
                                bound = int(bound,16)
                            if trunc_val >= base and trunc_val <= bound: # check legal range
                                part_legal = True
                        else:
                            l_vals = csr_vals.split(',')
                            legal_vals = []
                            for i in l_vals : 
                                legal_vals.append(int(i,16))
                            if trunc_val in legal_vals:
                                part_legal = True
                    else: # in case of bitmask there are no illegal values
                        part_legal = True
                    if not part_legal:
                        break
                if part_legal and dep_satified:
                    is_legal = True
                
        return is_legal

    def update(self, curr_val, wr_val, dependency_vals=[]):
        ''' The function takes the current value, write value and an optional list(optional incase there are no dependencies) containing the
        values of the corresponding dependency fields and models the updation of
        the register i.e if the supplied value is legal then the value is returned, else the new value of
        the register is calculated and returned.
        '''
        flag1 = 0
        flag2 = 0
        flag3 = 0
        flag4 = 0
        j = 0
        if self.dependencies != [] and dependency_vals != []:
            for i in range(len(self.warl['legal'])):
                mode1 = re.findall('\[(\d)\]\s*->\s*', self.warl['legal'][i])
                for i1 in range(len(dependency_vals)):
                    if dependency_vals[i1] == int(mode1[i1]):
                        j = i
                        flag1 = 1
                        break
            if flag1 == 0:
                print("Dependency vals do not match")
                exit()
        else:
            if len(self.warl['legal']) != 1:
                print("There cannot be more than one legal value")
                exit()
            else:
                j = 0
        inp1 = self.warl['legal'][j]
        flag1 = 0
        if self.dependencies != [] and dependency_vals != []:
            for i in range(len(self.warl['legal'])):
                if "bitmask" in self.warl['legal'][i]:
                    flag4 = 1
                else:
                    flag4 = 0
                    break

            if flag4 == 0 and not "bitmask" in inp1:
                for i in range(len(self.warl['wr_illegal'])):
                    mode = re.findall('\[(\d)\]\s*.*->\s*',
                                      self.warl['wr_illegal'][i])
                    op = re.findall(r'in\s*\[(.*?)\]',
                                    self.warl['wr_illegal'][i])
                    if op != []:
                        z = re.split("\:", op[0])
                    for i1 in range(len(dependency_vals)):
                        if dependency_vals[i1] == int(mode[i1]):
                            if op != []:
                                if int(wr_val,
                                       16) in range(int(z[0], 16),
                                                    int(z[1], 16)):
                                    j = i
                                    flag1 = 1
                                    break
                            else:
                                j = i
                                flag1 = 1
                                break
                    if flag1 == 1:
                        break
                inp = self.warl['wr_illegal'][j]
            else:
                inp = "no value"
                flag1 = 1

        elif self.dependencies == [] and dependency_vals == [] and not "bitmask" in self.warl[
                'legal'][0]:
            for i in range(len(self.warl['wr_illegal'])):
                op = re.findall(r'\s*wr_val\s*in\s*\[(.*?)\]',
                                self.warl['wr_illegal'][i])
                if op != []:
                    z = re.split("\:", op[0])
                    if int(wr_val, 16) in range(int(z[0], 16), int(z[1], 16)):
                        j = i
                        flag1 = 1
                        break

                else:
                    j = i
                    flag1 = 1
                    break

            inp = self.warl['wr_illegal'][j]

        elif self.dependencies != [] and dependency_vals != [] and len(
                self.warl['legal']) == 1 and "bitmask" in self.warl['legal'][0]:
            flag1 = 1

        if flag1 == 0 and dependency_vals != []:
            print("Dependency vals do not match")
            exit()
        if (self.islegal(curr_val, dependency_vals) == False):
            return "Current value must be legal"
        if (self.islegal(wr_val, dependency_vals)):
            return wr_val
        elif not "bitmask" in inp1:
            if "->" in inp:
                op2 = re.split(r'\->', inp)
                wr = op2[1]
            else:
                wr = inp.strip()
            if "0x" in wr:
                return wr.strip()
            elif wr.lower().strip() == "unchanged":
                return ("0x" + curr_val)

            elif wr.lower().strip() == "nearup":
                a = []
                flag2 = 0
                l = self.legal(dependency_vals)
                for i in range(len(l)):
                    if len(l[i]) == 1:
                        a.append(abs(int(wr_val, 16) - int(l[i][0], 16)))
                for i in range(len(a) - 1, -1, -1):
                    if a[i] == min(a):
                        j = i
                        flag2 = 1
                        break
                if flag2 == 1:
                    return l[j][0]

            elif wr.lower().strip() == "neardown":
                a = []
                l = self.legal(dependency_vals)
                for i in range(len(l)):
                    if len(l[i]) == 1:
                        a.append(abs(int(wr_val, 16) - int(l[i][0], 16)))
                for i in range(len(a)):
                    if a[i] == min(a):
                        j = i
                        flag2 = 1
                        break
                if flag2 == 1:
                    return l[j][0]

            elif wr.lower().strip() == "nextup":
                l = self.legal(dependency_vals)
                for i in range(len(l)):
                    if int(l[i][0], 16) > int(wr_val, 16) and len(l[i]) == 1:
                        j = i
                        flag2 = 1
                        break
                if flag2 == 1:
                    return l[j][0]
                else:
                    return max(l)

            elif wr.lower().strip() == "nextdown":
                l = self.legal(dependency_vals)
                for i in range(len(l)):
                    if int(l[i][0], 16) > int(wr_val, 16) and len(l[i]) == 1:
                        j = i
                        flag2 = 1
                        break
                if flag2 == 1 and j != 0:
                    return l[j - 1][0]
                else:
                    return min(l)

            elif wr.lower().strip() == "max":
                flag3 = 0
                l = self.legal(dependency_vals)
                for i in range(len(l)):
                    if "," in l[i][0]:
                        flag3 = 1
                        j = i
                    else:
                        flag3 = 0
                if flag3 == 0:
                    return max(l)
                else:
                    y = re.split(",", l[j][0])
                    return y[1]

            elif wr.lower().strip() == "min":
                flag3 = 0
                l = self.legal(dependency_vals)
                for i in range(len(l)):
                    if "," in l[i][0]:
                        flag3 = 1
                        j = i
                    else:
                        flag3 = 0
                if flag3 == 0:
                    return min(l)
                else:
                    y = re.split(",", l[j][0])
                    return y[0]

            elif wr.lower().strip() == "addr":
                wr = format(int(wr_val, 16),
                            '#0{}b'.format(4 * self.bitsum + 2))
                wr = wr[2:]
                if wr[0:1] == '0':
                    wr_final = '1' + wr[1:]
                elif wr[0:1] == '1':
                    wr_final = '0' + wr[1:]
                else:
                    print("Invalid binary bit")
                return hex(int(wr_final, 2))

            else:
                return "Invalid update mode"

        else:
            x = re.findall(
                r'\s*.*\s*\[.*\]\s*{}\s*\[(.*?,.*?)\]'.format("bitmask"), inp1)
            z = re.findall(
                r'\s*.*\s*\[(.*)\]\s*{}\s*\[.*?,.*?\]'.format("bitmask"), inp1)
            y = re.split("\,", x[0])
            bitmask = int(y[0], 16)
            fixedval = int(y[1], 16)
            currval = int(wr_val, 16)
            legal = ((currval & bitmask) | fixedval)
            return hex(legal)

    def legal(self, dependency_vals=[]):
        '''The function takes a range(defined as a 2 tuple list) and an optional(optional incase there are no dependencies) list containing the
        values of the corresponding dependency fields and returns the set of legal values as a list of two tuple lists.
        '''
        flag1 = 0
        j = 0
        if self.dependencies != [] and dependency_vals != []:
            for i in range(len(self.warl['legal'])):
                mode = re.findall('\[(\d)\]\s*->\s*', self.warl['legal'][i])
                for i1 in range(len(dependency_vals)):
                    if dependency_vals[i1] == int(mode[i1]):
                        j = i
                        flag1 = 1
                        break
                if flag1 == 1:
                    break
            if flag1 == 0 and dependency_vals != []:
                print("Dependency vals do not match")
                exit()
        else:
            if len(self.warl['legal']) != 1:
                print("There cannot be more than one legal value")
                exit()
            else:
                j = 0
        inp = self.warl['legal'][j]
        s = re.findall(r'in\s*\[(.*?)\]', inp)
        a = []
        b = []
        tup = []
        for i in range(len(s)):
            tup = []
            if ":" in s[i]:
                tup.append(s[i].replace(":", ","))
                a.append(tup)

            else:
                tup = []
                tup.append(s[i])
                a.append(tup)
        if not "bitmask" in inp:
            w = re.split(",", a[0][0])
            o = []
            for i in range(len(w)):
                e = w[i].strip().split()
                o.append(e)
            o.sort()
            return o
        else:
            return a
#str1=\
#'''
#dependency_fields: []
#legal:
#  - "extensions[7:4] in [1,3,5] extensions[3:0] in [0x0:0xF]"
#wr_illegal:
#  - "Unchanged"
#'''
#
#str2=\
#'''
#dependency_fields: [pmpcfg0]
#legal:
#  - "pmpcfg0[0] in [0] -> pmp3cfg[7:4] in [1,3,5] pmp3cfg[3:0] [0x00:0xF]"
#wr_illegal:
#  - "Unchanged"
#'''
#
#node = yaml.load(str2)
#warl = warl_interpreter(node)
#print(str(warl.islegal(0x302, [0])))
#
