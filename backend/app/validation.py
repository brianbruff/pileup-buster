"""
Callsign validation module for ITU amateur radio standards.
"""
import re


# ITU callsign pattern supporting multiple valid formats:
# 1. Traditional ITU with extended suffix: 1-2 letters + 1-2 numbers + 1-4 letters
# 2. UK numeric prefix format: 1 number + 1 letter + 1 number + 1-3 letters (e.g., 2E0JFS)
ITU_CALLSIGN_PATTERN = re.compile(r'^([A-Z]{1,2}[0-9]{1,2}[A-Z]{1,4}|[0-9][A-Z][0-9][A-Z]{1,3})$')


def validate_callsign(callsign: str) -> bool:
    """
    Validate a callsign against ITU amateur radio standards.
    
    Args:
        callsign: The callsign to validate (should be uppercase and stripped)
        
    Returns:
        bool: True if the callsign is valid according to ITU standards, False otherwise
        
    Supported callsign formats:
    1. Traditional ITU (with extended suffix for special events):
       - 1-2 letters (prefix indicating country/region)
       - 1-2 numbers (indicating region within country) 
       - 1-4 letters (suffix identifying the specific station)
    2. UK numeric prefix format:
       - 1 number + 1 letter + 1 number + 1-3 letters (e.g., 2E0JFS)
    
    Examples of valid callsigns:
    - KC1ABC (2 letters + 1 number + 3 letters) - Traditional ITU
    - W1AW (1 letter + 1 number + 2 letters) - Traditional ITU
    - EI0IRTS (2 letters + 1 number + 4 letters) - Special event
    - 2E0JFS (1 number + 1 letter + 1 number + 3 letters) - UK Foundation
    """
    if not callsign:
        return False
        
    return bool(ITU_CALLSIGN_PATTERN.match(callsign))