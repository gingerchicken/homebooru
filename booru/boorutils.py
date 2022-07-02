import hashlib
import pathlib
import ffmpegio

import homebooru.settings

# show log constant
__SHOW_LOG = True if homebooru.settings.BOORU_SHOW_FFMPEG_OUTPUT else None

def hash_str(s):
    """Hashes a string using the md5 algorithm"""
    return hashlib.md5(s.encode('utf-8')).hexdigest()

def get_file_checksum(path : str) -> str:
    """Gets the checksum of a file"""

    # Make sure that the file exists
    file_path = pathlib.Path(path)

    if not file_path.exists():
        raise Exception("File does not exist")

    # Make the file path absolute
    file_path = file_path.resolve()

    # Get the file md5 checksum
    md5 = hashlib.md5(file_path.read_bytes()).hexdigest()

    return md5

def get_content_dimensions(path : str) -> (int, int):
    """Gets the dimensions of an image or video"""

    # Make sure that the file exists
    file_path = pathlib.Path(path)

    if not file_path.exists():
        raise Exception("File does not exist")

    # Make the file path absolute
    file_path = file_path.resolve()

    # Use ffmpeg to get the dimensions
    pixels = ffmpegio.image.read(str(file_path), show_log=__SHOW_LOG)

    # get the dimensions
    (height, width) = pixels.shape[:2]

    # Make it the right way round!
    return (width, height)

def rescale_image(path : str, save_path : str, scale_arg : str) -> None:
    ffmpegio.transcode(path, save_path, overwrite=True, show_log=__SHOW_LOG, **{"vf": f"scale={scale_arg}", "vframes": "1"})

def generate_thumbnail(path : str, save_path : str) -> bool:
    """Generates a thumbnail for a post"""

    # Make sure that the file exists
    file_path = pathlib.Path(path)
    file_save_path = pathlib.Path(save_path)

    if not file_path.exists():
        raise Exception("File does not exist")
    
    # Make both paths absolute
    file_path = file_path.resolve()
    file_save_path = file_save_path.resolve()

    # Use ffmpeg to generate the thumbnail (i.e. create a new image with the resolution of ?x150)
    rescale_image(file_path, file_save_path, "-1:150")

    # Check that the file was created
    if not file_save_path.exists():
        raise Exception("File was not created")
    
    return True

def generate_sample(path : str, save_path : str) -> bool:
    """Generates a sample for a post - if over a certain size"""

    # Make sure that the file exists
    file_path = pathlib.Path(path)
    file_save_path = pathlib.Path(save_path)

    if not file_path.exists():
        raise Exception("File does not exist")
    
    # Make both paths absolute
    file_path = file_path.resolve()
    file_save_path = file_save_path.resolve()

    # Get the dimensions of the file
    (width, height) = get_content_dimensions(file_path)

    # If the width is over 850px, then generate a sample
    if width <= 850:
        return False

    # Rescale the image
    rescale_image(file_path, file_save_path, "850:-1")
    
    # Check that the file was created
    if not file_save_path.exists():
        raise Exception("File was not created")
    
    return True

def wildcard_to_regex(phrase : str, wildcard : str = '*') -> str:
    """Converts a wildcard to a regex"""
    r = phrase

    # Regex escape the all of the characters, unless it is a wild card
    escaped = ''
    for c in r:
        if c == wildcard:
            escaped += c
            continue
        
        # Escape the character but if it is a number don't make it the character code
        if c.isdigit() or c.isalpha():
            escaped += f"[{c}]"
            continue
            
        # Escape the character as a character code
        escaped += '\\' + c

    r = escaped.replace(wildcard, '.*')

    return r

def is_valid_username(username : str) -> bool:
    """Checks if a username is valid"""
    
    # Check if the username is empty
    if not username:
        return False

    # Make sure that the username is at least 3 characters long
    if len(username) < 3:
        return False

    # Check if the username is too long
    if len(username) > 20:
        return False

    # Check if the username contains invalid characters
    for c in username:
        if c.isalnum(): continue
        if c in '_.': continue
        
        # It must be invalid
        return False

    # It must be valid as all checks passed
    return True

def is_valid_password(password : str):
    """Checks if a password is valid"""

    # Check if the password is empty
    if not password:
        return False

    # Make sure that the password is at least 6 characters long
    if len(password) < 6:
        return False
    
    # It must contain at least one number
    if not any(c.isdigit() for c in password):
        return False
    
    # It must contain at least one special character (i.e. non-alphanumeric)
    if not any(not c.isalnum() for c in password):
        return False

    # It passes all checks
    return True