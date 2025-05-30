# backend/app/services/exceptions.py
class UserAlreadyExistsError(Exception):
    pass

class InvalidCredentialsError(Exception):
    pass