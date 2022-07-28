import base64

# I have encoded them since I don't want to associate with them!
VALID_BOORUS = [
    'aHR0cHM6Ly9zYWZlYm9vcnUub3JnLw=='
]

# Decode them
for i in range(len(VALID_BOORUS)):
    VALID_BOORUS[i] = base64.b64decode(VALID_BOORUS[i]).decode('utf-8')

INVALID_BOORUS = [
    'https://whoasked.gov.uk',
    'https://example.com',
    'https://google.com/',
    VALID_BOORUS[0] + '/cement', # for non-200 case
]