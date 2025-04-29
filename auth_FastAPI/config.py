from authx import AuthX, AuthXConfig



config = AuthXConfig()
config.JWT_SECRET_KEY = 'secret_key'
config.JWT_ACCESS_COOKIE_NAME = 'token'
config.JWT_TOKEN_LOCATION = ['cookies']

