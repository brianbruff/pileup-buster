"""
Tests for callsign validation following ITU standards.
"""
import pytest
from app.validation import validate_callsign


class TestCallsignValidation:
    """Test cases for ITU callsign validation"""
    
    def test_valid_callsigns(self):
        """Test various valid callsign formats"""
        valid_callsigns = [
            # Standard US callsigns
            'KC1ABC',  # 2 letters + 1 number + 3 letters
            'W1AW',    # 1 letter + 1 number + 2 letters
            'N0AA',    # 1 letter + 1 number + 2 letters
            'K5XYZ',   # 1 letter + 1 number + 3 letters
            
            # International callsigns
            'VK2DEF',  # Australia: 2 letters + 1 number + 3 letters
            'G0ABC',   # UK: 1 letter + 1 number + 3 letters
            'JA1XYZ',  # Japan: 2 letters + 1 number + 3 letters
            'DL9ABC',  # Germany: 2 letters + 1 number + 3 letters
            
            # Two-digit region numbers
            'W10ABC',  # 1 letter + 2 numbers + 3 letters
            'KC12XY',  # 2 letters + 2 numbers + 2 letters
            'VK21A',   # 2 letters + 2 numbers + 1 letter
            
            # UK Foundation/Intermediate callsigns (numeric prefix)
            '2E0JFS',  # Foundation license format
            '2M0ABC',  # Intermediate license format
            '2M1DEF',  # Intermediate license format
            
            # Special event callsigns (extended suffix)
            'EI0IRTS', # 2 letters + 1 number + 4 letters
            'G0ABCD',  # 1 letter + 1 number + 4 letters
            'W1ABCD',  # 1 letter + 1 number + 4 letters
            
            # Minimal valid formats
            'W1A',     # 1 letter + 1 number + 1 letter
            'KC1A',    # 2 letters + 1 number + 1 letter
            'W10A',    # 1 letter + 2 numbers + 1 letter
            'KC10A',   # 2 letters + 2 numbers + 1 letter
        ]
        
        for callsign in valid_callsigns:
            assert validate_callsign(callsign), f"'{callsign}' should be valid"
    
    def test_invalid_callsigns(self):
        """Test various invalid callsign formats"""
        invalid_callsigns = [
            # Empty/None
            '',
            None,
            
            # Too many letters in prefix
            'ABC1DEF',  # 3+ letters at start
            'ABCD1XYZ', # 4+ letters at start
            
            # No numbers
            'ABCDEF',   # All letters
            'KC',       # Only prefix
            'ABCD',     # Only letters
            
            # No prefix letters
            '123ABC',   # Starts with numbers
            '1ABC',     # Starts with number
            
            # No suffix letters
            'KC123',    # Ends with numbers
            'W1',       # Missing suffix
            
            # Too many suffix letters (more than 4)
            'KC1DEFGH', # 5+ letters at end
            
            # Too many numbers
            'W123ABC',  # 3+ numbers
            'KC1234XY', # 4+ numbers
            
            # Invalid characters
            'KC1AB-',   # Hyphen
            'W1A/B',    # Slash
            'KC1 ABC',  # Space
            'kc1abc',   # Lowercase (should be validated after uppercase conversion)
            'KC1@BC',   # Special character
            
            # Common amateur radio special formats that don't follow basic ITU pattern
            '/P',       # Portable indicator only
            'KC1ABC/P', # With portable indicator (not basic ITU format)
            'KC1ABC/M', # With mobile indicator
        ]
        
        for callsign in invalid_callsigns:
            assert not validate_callsign(callsign), f"'{callsign}' should be invalid"
    
    def test_edge_cases(self):
        """Test edge cases for callsign validation"""
        # Test boundary conditions
        assert validate_callsign('A1A')        # Minimum: 1+1+1
        assert validate_callsign('AB12ABCD')    # Maximum traditional: 2+2+4
        assert validate_callsign('9Z9ABC')      # Maximum UK format: 1+1+1+3
        
        # Test just over boundaries
        assert not validate_callsign('ABC1A')   # Too many prefix letters (3 for traditional)
        assert not validate_callsign('A123A')   # Too many numbers
        assert not validate_callsign('A1ABCDE') # Too many suffix letters (5+ for traditional)
        assert not validate_callsign('1ABC9ABC') # Invalid UK format (too many suffix letters)
        
    def test_case_sensitivity(self):
        """Test that validation expects uppercase input"""
        # The validation function expects uppercase input
        # (case conversion should happen before validation)
        assert validate_callsign('KC1ABC')  # Uppercase
        assert not validate_callsign('kc1abc')  # Lowercase should fail
        assert not validate_callsign('Kc1Abc')  # Mixed case should fail