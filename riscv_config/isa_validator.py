import riscv_config.constants as constants
import re

def get_extension_list(isa):
    extension_list = []
    err = False
    err_list = []
    if not constants.isa_regex.match(isa):
        err = True
        err_list.append('Input ISA string does not match accepted canonical ordering')
        return (extension_list, err, err_list)

    
    str_match = re.findall('(?P<stdisa>[^\d]*?)(?!_)*(?P<zext>Z.*?)*(?P<sext>S[a-z]*)*(_|$)',isa)
    extension_list= []
    standard_isa = ''
    zext_list = []
    for match in str_match:
        stdisa, zext, sext, ignore = match
        if stdisa != '':
            for e in stdisa:
                extension_list.append(e)
            standard_isa = stdisa
        if zext != '':
            extension_list.append(zext)
            zext_list.append(zext)
        if sext != '':
            extension_list.append(sext)
    # check ordering of ISA
    canonical_ordering = 'IEMAFDQLCBJKTPVNSHU'
    order_index = {c: i for i, c in enumerate(canonical_ordering)}
    for i in range(len(standard_isa)-1):
        a1 = standard_isa[i]
        a2 = standard_isa[i+1]
    
        if order_index[a1] > order_index[a2]:
            err = True
            err_list.append( "Alphabet '" + a1 + "' should occur after '" + a2)

    # check canonical ordering within Zextensions
    for i in range(len(zext_list)-1):
        a1 = zext_list[i][1].upper()
        a2 = zext_list[i+1][1].upper()
        a3 = zext_list[i][2]
        a4 = zext_list[i+1][2]
        if order_index[a1] > order_index[a2]:
            err = True
            err_list.append( f"Z extension {zext_list[i]} must occur after {zext_list[i+1]}")
        elif a1 == a2 and a3 > a4:
            err = True
            err_list.append( f"Within the Z{a1.lower()} category extension {zext_list[i]} must occur after {zext_list[i+1]}")
        
    if 'I' not in extension_list and 'E' not in extension_list:
        err_list.append( 'Either of I or E base extensions need to be present in the ISA string')
        err = True
    if 'F' in extension_list and not "Zicsr" in extension_list:
        err_list.append( "F cannot exist without Zicsr.")
        err = True
    if 'D' in extension_list and not 'F' in extension_list:
        err_list.append( "D cannot exist without F.")
        err = True
    if 'Q' in extension_list and not 'D' in extension_list:
        err_list.append( "Q cannot exist without D and F.")
        err = True
    if 'Zam' in extension_list and not 'A' in extension_list:
        err_list.append( "Zam cannot exist without A.")
        err = True
    if 'N' in extension_list and not 'U' in extension_list:
        err_list.append( "N cannot exist without U.")
        err = True
    if 'S' in extension_list and not 'U' in extension_list:
        err_list.append( "S cannot exist without U.")
        err = True
    if 'Zkg' in extension_list and 'Zbc' in extension_list:
        err_list.append( "Zkg being a proper subset of Zbc (from B extension) should be ommitted from the ISA string")
        err = True
    if 'Zkb' in extension_list and 'Zbp' in extension_list :
        err_list.append( "Zkb being a proper subset of Zbp (from B extension) should be ommitted from the ISA string")
        err = True
    if 'Zks' in extension_list and ( set(['Zkse', 'Zksh','Zkg','Zkb']) & set(extension_list) ):
        err_list.append( "Zks is a superset of Zkse, Zksh, Zkg and Zkb. In presence of Zks the subsets must be ignored in the ISA string.")
        err = True
    if 'Zkn' in extension_list and ( set(['Zkne','Zknd','Zknh','Zkg','Zkb']) & set(extension_list) ):
        err_list.append( "Zkn is a superset of Zkne, Zknd, Zknh, Zkg and Zkb, In presence of Zkn the subsets must be ignored in the ISA string")
        err = True
    if 'K' in extension_list and ( set(['Zkn','Zkr','Zkne','Zknd','Zknh','Zkg','Zkb']) & set(extension_list) ) :
        err_list.append( "K is a superset of Zkn and Zkr , In presence of K the subsets must be ignored in the ISA string")
        err = True
    return (extension_list, err, err_list)


        
