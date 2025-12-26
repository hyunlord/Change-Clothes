from abc import ABC, abstractmethod
import numpy as np
from PIL import Image

class SegmentationModel(ABC):
    @abstractmethod
    def load_model(self):
        """Load the model weights."""
        pass

    @abstractmethod
    def segment(self, image: Image.Image, category: str) -> Image.Image:
        """
        Segment the image and return the mask for the specific category.
        Returns a PIL Image (L mode) where 255 is the mask.
        """
        pass
