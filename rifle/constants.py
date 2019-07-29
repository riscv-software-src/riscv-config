import os

root = os.path.abspath(os.path.dirname(__file__))

isa_schema = os.path.join(root, 'schemas/schema_isa.yaml')
platform_schema = os.path.join(root, 'schemas/schema_platform.yaml')

priv_versions = ["1.10", "1.11"]
user_versions = ["2.2", "2.3"]
