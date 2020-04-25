import jwt
import os

def decode_authorization_jwt(authorization_header):

    if authorization_header is None:

        return None

    token = authorization_header.split(' ')[1]

    decoded = jwt.decode(token, os.environ.get('JWT_KEY'), options={ 'verify_aud': False }, algorithms=[ 'HS256' ] )
    
    return decoded
