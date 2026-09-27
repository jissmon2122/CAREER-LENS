import re

EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$')

def validate_registration_data(data):
    """
    Validates user registration payload.
    Returns (is_valid: bool, error_message: str)
    """
    if not isinstance(data, dict):
        return False, "Invalid payload data"

    required_fields = ['name', 'email', 'password', 'confirm_password']
    for field in required_fields:
        if not data.get(field) or str(data.get(field)).strip() == '':
            return False, f"Field '{field.replace('_', ' ').title()}' is required"

    email = str(data.get('email')).strip()
    if not EMAIL_REGEX.match(email):
        return False, "Please enter a valid email address format"

    password = str(data.get('password'))
    confirm_password = str(data.get('confirm_password'))

    if len(password) < 6:
        return False, "Password must be at least 6 characters in length"

    if password != confirm_password:
        return False, "Password and Confirm Password do not match"

    return True, ""

def validate_login_data(data):
    """
    Validates user login payload.
    Returns (is_valid: bool, error_message: str)
    """
    if not isinstance(data, dict):
        return False, "Invalid payload data"

    email = data.get('email')
    password = data.get('password')

    if not email or not str(email).strip():
        return False, "Email address is required"

    if not password:
        return False, "Password is required"

    return True, ""
