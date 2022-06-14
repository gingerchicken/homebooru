import hashlib
import pathlib
import ffmpegio

def hash_str(s):
    """Hashes a string using the md5 algorithm"""
    return hashlib.md5(s.encode('utf-8')).hexdigest()

def get_content_dimensions(path : str) -> (int, int):
    """Gets the dimensions of an image or video"""

    # Make sure that the file exists
    file_path = pathlib.Path(path)

    if not file_path.exists():
        raise Exception("File does not exist")

    # Make the file path absolute
    file_path = file_path.resolve()

    # Use ffmpeg to get the dimensions
    pixels = ffmpegio.image.read(str(file_path))

    # get the dimensions
    (height, width) = pixels.shape[:2]

    # Make it the right way round!
    return (width, height)