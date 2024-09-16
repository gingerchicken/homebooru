import sys
import os

# Add the directory containing Models.py to the Python path
sys.path.append(os.path.expanduser('~/.joytag/joytag'))

from Models import VisionModel # ~/.joytag/joytag/Models.py
from PIL import Image
import torch.amp.autocast_mode
from pathlib import Path
import torch
import torchvision.transforms.functional as TVF

from .tag_automation import TagAutomation
from booru.models.tags import Tag
from booru.models.posts import Post

class JoytagAutomation(TagAutomation):
    """
    An automation for tagging images with Joytag.
    """

    model_path = Path(os.path.expanduser('~/.joytag/model'))
    threshold = 0.7

    def __init__(self):
        super().__init__()

    def __prepare_model(self):
        """
        Creates a VisionModel object from the model at the given path.
        """

        self.__model = None
        self.__top_tags = None

        if self.__model is not None and self.__top_tags is not None:
            return
        
        model = VisionModel.load_model(self.model_path, device='cpu')
        model.eval()
        model = model.to('cpu')

        # Get the top tags
        # Load the tags from the file
        with open(self.model_path / 'top_tags.txt', 'r') as f:
            top_tags = [line.strip() for line in f.readlines() if line.strip()]
            
        self.__model = model
        self.__top_tags = top_tags

    # Wrappers
    def __prepare_image(self, image: Image.Image, target_size: int) -> torch.Tensor:
        # Pad image to square
        image_shape = image.size
        max_dim = max(image_shape)
        pad_left = (max_dim - image_shape[0]) // 2
        pad_top = (max_dim - image_shape[1]) // 2

        padded_image = Image.new('RGB', (max_dim, max_dim), (255, 255, 255))
        padded_image.paste(image, (pad_left, pad_top))

        # Resize image
        if max_dim != target_size:
            padded_image = padded_image.resize((target_size, target_size), Image.BICUBIC)

        # Convert to tensor
        image_tensor = TVF.pil_to_tensor(padded_image) / 255.0

        # Normalize
        image_tensor = TVF.normalize(image_tensor, mean=[0.48145466, 0.4578275, 0.40821073], std=[0.26862954, 0.26130258, 0.27577711])

        return image_tensor

    @torch.no_grad()
    def __predict(self, image: Image.Image):
        self.__prepare_model() # Ensure the model is loaded

        image_tensor = self.__prepare_image(image, self.__model.image_size)
        batch = {
            'image': image_tensor.unsqueeze(0).to('cpu'),
        }

        with torch.amp.autocast_mode.autocast('cpu', enabled=True):
            preds = self.__model(batch)
            tag_preds = preds['tags'].sigmoid().cpu()

        scores = {self.__top_tags[i]: tag_preds[0][i] for i in range(len(self.__top_tags))}
        predicted_tags = [tag for tag, score in scores.items() if score > self.threshold]
        tag_string = ', '.join(predicted_tags)

        return tag_string, scores

    # Override
    def get_tags(self, post : Post) -> list[Tag]:
        # Check if the post is a video or gif
        if post.is_video:
            return []

        image = Image.open(post.get_media_path())

        tag_string, scores = self.__predict(image)

        # Select the tags over the threshold
        selected_tags = []
        predicted_tags = scores.items()
        for tag, score in predicted_tags:
            if score <= self.threshold:
                continue
        
            selected_tags.append(Tag.create_or_get(tag))
        
        return selected_tags