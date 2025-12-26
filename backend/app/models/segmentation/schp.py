from .base import SegmentationModel
from PIL import Image
import numpy as np

class SCHPSegmentation(SegmentationModel):
    def __init__(self):
        self.model = None
        print("Initialized SCHP Segmentation Strategy")

    def load_model(self):
        print("Loading SCHP model... (Mock)")
        self.model = "SCHP_LOADED"

    def segment(self, image: Image.Image, category: str) -> Image.Image:
        print(f"Running SCHP segmentation for category: {category}")
        w, h = image.size
        mask = Image.new('L', (w, h), 0)
        # Draw a circle to distinguish from SAM3
        from PIL import ImageDraw
        draw = ImageDraw.Draw(mask)
        draw.ellipse([w//4, h//4, 3*w//4, 3*h//4], fill=255)
        return mask
