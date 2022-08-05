import base64
import pathlib
import datetime
import os
import shutil

import booru.boorutils as boorutils
import booru.tests.testutils as booru_testutils


# Booru image
BOORU_MD5 = boorutils.get_file_checksum(booru_testutils.BOORU_IMAGE)

# Expected booru tags for that image
BOORU_TAGS = [
    'astolfo_(fate)',
    '1boy',
    'pink_hair'
]

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

class TempScanFolder:
    def __init__(self, files : list = []):
        self.__files = files

    def setUp(self):
        # Get a folder name
        timestamp = str(datetime.datetime.now().timestamp())
        md5 = boorutils.hash_str(timestamp)

        # Create a temporary folder
        self.folder = pathlib.Path('/tmp/' + md5)

        # Create the folder
        self.folder.mkdir(parents=True, exist_ok=True)

        # Copy the files
        for file in self.__files:
            # Original path
            original_path = pathlib.Path(file)

            # New path
            result_path = self.folder / (boorutils.get_file_checksum(original_path) + original_path.suffix)

            # Copy the file
            shutil.copy(original_path, result_path)

    def tearDown(self):
        # Remove the folder and all of its contents
        shutil.rmtree(self.folder)
    
    def add_file(self, file : str):
        self.__files.append(file)
    
    def remove_file(self, file : str):
        self.__files.remove(file)
    
    def remove_all_files(self):
        self.__files.clear()