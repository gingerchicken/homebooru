import homebooru.settings

from ..models.posts import Post
from ..models.tags import Tag

import pathlib
import shutil
import os

# Paths
TEST_DATA_PATH = pathlib.Path('assets/TEST_DATA')
CONTENT_PATH = TEST_DATA_PATH / 'content'

# Expected
FELIX_PATH = pathlib.Path(CONTENT_PATH / 'felix.jpg')
GATO_PATH  = pathlib.Path(CONTENT_PATH / 'gato.png')
VIDEO_PATH = pathlib.Path(CONTENT_PATH / 'ana_cat.mp4')
SAMPLEABLE_PATH = pathlib.Path(CONTENT_PATH / 'sampleable_image.jpg')

# Erroneous
NON_IMAGE_PATH = pathlib.Path(CONTENT_PATH / 'test.txt')
CORRUPT_IMAGE_PATH = pathlib.Path(CONTENT_PATH / 'corrupt_image.jpg')

class TempStorage():
    og_path = None
    temp_storage_path = "/tmp/storage"

    def setUp(self):
        self.og_path = homebooru.settings.BOORU_STORAGE_PATH
        homebooru.settings.BOORU_STORAGE_PATH = pathlib.Path(self.temp_storage_path)

        Post.objects.all().delete()
        Tag.objects.all().delete()

        if os.path.exists(self.temp_storage_path):
            shutil.rmtree(self.temp_storage_path)

        # Create the temp storage path
        os.mkdir(self.temp_storage_path)
    
    def tearDown(self):
        homebooru.settings.BOORU_STORAGE_PATH = self.og_path

        if os.path.exists(self.temp_storage_path):
            shutil.rmtree(self.temp_storage_path)