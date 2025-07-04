"""Tests for ISA regex pattern validation."""

import pytest
import re
from riscv_config.constants import isa_regex


class TestISARegex:

    @pytest.mark.parametrize("isa_string,expected", [
        # Basic ISA strings
        ("RV32I", True),
        ("RV64I", True),
        ("RV128I", True),
        ("RV32E", True),
        
        # Standard extensions
        ("RV32IMAFD", True),
        ("RV64IG", True),
        ("RV32IMC", True),
        ("RV64IMAFDC", True),
        
        # Sub-extensions
        ("RV32I_Zicsr", True),
        ("RV64I_Zifencei", True),
        ("RV32I_Zicsr_Zifencei", True),
        ("RV32I_Svnapot", True),
        ("RV64I_Smrnmi", True),
        
        # Custom extensions
        ("RV32I_Xvendor", True),
        ("RV64I_Xvendor1_Xvendor2", True),
        ("RV64I_XcustomExt123", True),
        
        # Complex combinations
        ("RV64IMAFD_Zicsr_Zifencei_Xvendor", True),
        ("RV32I_Zve32x", True),
        ("RV64I_Zve64f", True),
        ("RV32I_Zvl32b", True),
    ])
    def test_valid_isa_strings(self, isa_string, expected):
        """Valid ISA strings should match the regex."""
        assert bool(isa_regex.match(isa_string)) == expected

    @pytest.mark.parametrize("isa_string,expected", [
        # Missing base ISA
        ("RV64G", False),
        ("RV32", False),
        ("RV64", False),
        
        # Invalid widths
        ("RV16I", False),
        ("RV256I", False),
        
        # Invalid base ISA
        ("RV32X", False),
        ("RV32II", False),
        ("RV64EI", False),
        
        # Format errors
        ("RV32IZicsr", False),
        ("RV32I_", False),
        ("RV32I__Zicsr", False),
        ("RV32I_Zicsr_", False),
        
        # Case sensitivity
        ("rv32i", False),
        ("RV32i", False),
        ("RV32I_zicsr", False),
        ("RV32I_ZICSR", False),
        
        # Unknown extensions
        ("RV32I_Zunknown", False),
        ("RV32I_Sunknown", False),
        ("RV32I_X", False),
        ("RV32I_Xinvalid-name", False),
        
        # Whitespace and special chars
        ("", False),
        ("RV32I ", False),
        (" RV32I", False),
        ("RV32I@", False),
        ("RV32I_Zicsr!", False),
    ])
    def test_invalid_isa_strings(self, isa_string, expected):
        """Invalid ISA strings should be rejected."""
        assert bool(isa_regex.match(isa_string)) == expected

    def test_regex_structure(self):
        """Basic regex structure tests."""
        assert isinstance(isa_regex, re.Pattern)
        assert isa_regex.pattern.startswith("^")
        assert isa_regex.pattern.endswith("$")

    def test_all_standard_extensions(self):
        """Test all standard extensions work."""
        for ext in "ACDFGHJLMNPQSTUV":
            isa = f"RV32I{ext}"
            assert isa_regex.match(isa), f"Extension {ext} should work"

    def test_all_architectures(self):
        """Test all supported architectures."""
        for width in ["32", "64", "128"]:
            for base in ["I", "E"]:
                isa = f"RV{width}{base}"
                assert isa_regex.match(isa), f"{isa} should match"

    def test_extension_categories(self):
        """Test different extension categories."""
        # Z extensions
        z_tests = ["RV32I_Zicsr", "RV32I_Zba", "RV32I_Zfh"]
        for test in z_tests:
            assert isa_regex.match(test), f"{test} should match"
        
        # S extensions  
        s_tests = ["RV32I_Smrnmi", "RV32I_Svnapot"]
        for test in s_tests:
            assert isa_regex.match(test), f"{test} should match"
        
        # Vector extensions
        v_tests = ["RV32I_Zve32x", "RV32I_Zvl32b"]
        for test in v_tests:
            assert isa_regex.match(test), f"{test} should match"


class TestRealWorldScenarios:
    """Test realistic ISA configurations."""

    def test_common_configurations(self):
        """Test ISA strings from real projects."""
        configs = [
            "RV32I",
            "RV32IMC", 
            "RV32IMAFD",
            "RV64IMAFD",
            "RV32I_Zicsr_Zifencei",
            "RV64IG_Zicsr_Zifencei",
            "RV32I_Zba_Zbb_Zbc_Zbs",
            "RV64I_Zfh_Zfa",
            "RV32I_Zve32x_Zvl32b",
        ]
        
        for config in configs:
            assert isa_regex.match(config), f"Config {config} should work"

    def test_user_mistakes(self):
        """Test common user errors."""
        mistakes = [
            ("RV32G", "G needs I or E"),
            ("RV32i", "Wrong case"),
            ("RV32I_zicsr", "Extension case"),
            ("RV32IZicsr", "Missing underscore"),
            ("RV32I_Zicsr_", "Trailing underscore"),
            ("rv32i", "All lowercase"),
        ]
        
        for mistake, _ in mistakes:
            assert not isa_regex.match(mistake), f"{mistake} should fail"


def test_can_import_regex():
    """Test regex imports correctly."""
    from riscv_config.constants import isa_regex
    assert isa_regex is not None
    assert callable(isa_regex.match)
