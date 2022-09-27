import os
import re

root = os.path.abspath(os.path.dirname(__file__))

isa_schema = os.path.join(root, 'schemas/schema_isa.yaml')
debug_schema = os.path.join(root, 'schemas/schema_debug.yaml')
platform_schema = os.path.join(root, 'schemas/schema_platform.yaml')
Z_extensions = [
        "Zicbom", "Zicbop", "Zicboz", "Zicsr", "Zifencei", "Zihintpause",
        "Zam",
        "Zfh",
        "Zfinx", "Zdinx", "Zhinx", "Zhinxmin",
        "Ztso",
        "Zba", "Zbb", "Zbc", "Zbe", "Zbf", "Zbkb", "Zbkc", "Zbkx", "Zbm", "Zbp", "Zbr", "Zbs", "Zbt",
        "Zk", "Zkn", "Zknd", "Zkne", "Zknh", "Zkr", "Zks", "Zksed", "Zksh", "Zkt",
        "Zmmul",
        "Svnapot"
]
isa_regex = \
        re.compile("^RV(32|64|128)[IE][ACDFGHJLMNPQSTUVX]*(("+'|'.join(Z_extensions)+")(_("+'|'.join(Z_extensions)+"))*){,1}$")
