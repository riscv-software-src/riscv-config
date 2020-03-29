# Changelog

This project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## 2.1.1 - 2020-03-29
## Fixed
- doc issue for mtimecmp
- mimpid is now part of the default setters list

## 2.1.0 - 2020-03-29
## Fixed
- Moved machine timer nodes to platform yaml.
## Added
- `--version` option to arguments to print version and exit when specified.
- Print help and exit when no options/arguments are specified.

## 2.0.2 - 2020-03-28
### Fixed
- Redundant reset-val check for mtvec and misa registers.

## 2.0.1 - 2020-03-25
### Fixed
- typos in quickstart doc
- disabled deployment to repository until authentication issue is fixed.

## 2.0.0 - 2020-03-25
### Added
- adding support for warl fields and support
- documentation for the warl fields added
- reset-value checks added
### Changed
- using a new common template for defining all csrs
- updated docs with new template
- using special function within conf.py to extract comments from yaml file as docs.
### Fixed
- closed issues #10, #11, #12, #13

## 1.0.2 - 2019-08-09
### Changed
- Log is generated only if specified(for API calls to checker.check_specs).
### Fixed
- link in readme now points to github instead of gitlab.

## 1.0.0 - 2019-07-30
### Changed
- Work directory isnt deleted if the directory exists, although the files of the same name will be overwritten.
### Fixed
- Checked yaml passes validation too.

## 0.1.0 - 2019-07-29
### Added
- Added work_dir as arg and always outputs to that dir.
- Added reset vector and nmi vector to platform.yaml
- Vendor description fields in schema.
- An xlen field added for internal use.
### Fixed
- In ISA field in isa_specs subsequent 'Z' extensions should be prefixed by an underscore '_'
- Fixed `cerberus.validator.DocumentError: document is missing` error when platform specs is empty. 
- mtvec:mode max value is set to 1.
- privilege-spec and user-spec are taken as strings instead of float.
### Changed
- The representation of the int fields is preserved in the checked-yaml.
- mepc is a required field.
- check_specs function now returns the paths to the dumped normalized files.
- No other entries in node where implemented is False.
- Readonly fields are purged by default.
- Multiple values/entries for the same node is not allowed.
### Removed
- remove *_checked.yaml files from Examples.
- changed templates_platform.yaml to template_platform.yaml in docs.

## 0.0.3 - 2019-07-19
### Fixed
- doc update

## 0.0.2 - 2019-07-19
### Fixed
- pdf documentation
- ci-cd to host pdf as well

## 0.0.1 - 2019-07-18
### Added
- Documentation to install and use pyenv 

## 0.0.0 - 2019-07-18
### Added
- Initial schemas for M mode and S mode csrs with constraints as specified in the spec.
