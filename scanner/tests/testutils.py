import base64

# I have encoded them since I don't want to associate with them!
# Please be aware that I do not moderate these sites nor do I have control of what content is on them.
VALID_BOORUS = [
    'aHR0cHM6Ly9zYWZlYm9vcnUub3JnLw==',
    'aHR0cHM6Ly9nZWxib29ydS5jb20v'
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