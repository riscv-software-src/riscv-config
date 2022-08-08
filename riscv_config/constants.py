import os
import re

root = os.path.abspath(os.path.dirname(__file__))

isa_schema = os.path.join(root, 'schemas/schema_isa.yaml')
debug_schema = os.path.join(root, 'schemas/schema_debug.yaml')
platform_schema = os.path.join(root, 'schemas/schema_platform.yaml')
isa_regex = \
        re.compile("^RV(32|64|128)[IE]+[ACDEFGHJLMNPQSTUVX]*(Zicbom|Zicbop|Zicboz|Zicsr|Zifencei|Zihintpause|Zam|Zfinx|Zfh|Zdinx|Zhinx|Zhinxmin|Ztso|Zba|Zbb|Zbc|Zbe|Zbf|Zbkb|Zbkc|Zbkx|Zbm|Zbp|Zbr|Zbs|Zbt|Zk|Zkn|Zknd|Zkne|Zknh|Zkr|Zks|Zksed|Zksh|Zkt|Zmmul|Svnapot){,1}(_Zicbom){,1}(_Zicbop){,1}(_Zicboz){,1}(_Zicsr){,1}(_Zifencei){,1}(_Zihintpause){,1}(_Zmmul){,1}(_Zam){,1}(_Zfinx){,1}(Zfh){,1}(_Zdinx){,1}(_Zhinx){,1}(_Zhinxmin){,1}(_Zba){,1}(_Zbb){,1}(_Zbc){,1}(_Zbe){,1}(_Zbf){,1}(_Zbkb){,1}(_Zbkc){,1}(_Zbkx){,1}(_Zbm){,1}(_Zbp){,1}(_Zbr){,1}(_Zbs){,1}(_Zbt){,1}(_Zk){,1}(_Zkn){,1}(_Zknd){,1}(_Zkne){,1}(_Zknh){,1}(_Zkr){,1}(_Zks){,1}(_Zksed){,1}(_Zksh){,1}(_Zkt){,1}(_Ztso){,1}(_Svnapot){,1}$")
