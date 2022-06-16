import homebooru.settings

from ..models.posts import Post
from ..models.tags import Tag

import pathlib
import shutil
import os


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