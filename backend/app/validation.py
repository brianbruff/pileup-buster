"""
Callsign validation module for ITU amateur radio standards.
"""
import re


# ITU callsign pattern: 1-2 letters (prefix) + 1-2 numbers (region) + 1-3 letters (suffix)
ITU_CALLSIGN_PATTERN = re.compile(r'^[A-Z]{1,2}[0-9]{1,2}[A-Z]{1,3}$')


def validate_callsign(callsign: str) -> bool:
    """
    Validate a callsign against ITU amateur radio standards.
    
    Args:
        callsign: The callsign to validate (should be uppercase and stripped)
        
    Returns:
        bool: True if the callsign is valid according to ITU standards, False otherwise
        
    ITU callsign format:
    - 1-2 letters (prefix indicating country/region)
    - 1-2 numbers (indicating region within country) 
    - 1-3 letters (suffix identifying the specific station)
    
    Examples of valid callsigns:
    - KC1ABC (2 letters + 1 number + 3 letters)
    - W1AW (1 letter + 1 number + 2 letters)
    - VK2DEF (2 letters + 1 number + 3 letters)
    - N0AA (1 letter + 1 number + 2 letters)
    """
    if not callsign:
        return False
        
    return bool(ITU_CALLSIGN_PATTERN.match(callsign))