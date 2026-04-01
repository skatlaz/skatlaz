import random

codes = {}

def send_email_code(email):
    code = str(random.randint(100000, 999999))
    codes[email] = code
    print("CODE:", code)
    return code

def verify_code(email, code):
    return codes.get(email) == code
