"""
Credit to Sci Prog on stackoverflow for the code.
https://stackoverflow.com/questions/35857967/python-password-requirement-program
"""


def validate(password: str) -> bool:
    """
    Validates a password to make sure it follows the requirments

    Args:
        password (str): The password to validate

    Returns:
        bool
    """
    SPECIAL = "@$#!&*()[].,?+=-"

    Cap, Low, Num, Spec, Len = False, False, False, False, False
    for i in password:
        if i.isupper():
            Cap = True
        elif i.islower():
            Low = True
        elif i.isdigit():
            Num = True
        elif i in SPECIAL:
            Spec = True
    if len(password) >= 8:
        Len = True

    if Cap and Low and Num and Spec and Len:
        return True
    else:
        return False
