# Changelog

This project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.0] - 2019-07-29
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

## [1.0.3] - 2019-07-19
### Fixed
- doc update

## [1.0.2] - 2019-07-19
### Fixed
- pdf documentation
- ci-cd to host pdf as well

## [1.0.1] - 2019-07-18
### Added
- Documentation to install and use pyenv 

## [1.0.0] - 2019-07-18
### Added
- Initial schemas for M mode and S mode csrs with constraints as specified in the spec.
