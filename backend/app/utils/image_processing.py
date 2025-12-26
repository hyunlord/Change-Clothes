from PIL import Image
import cv2
import numpy as np

def resize_image(image_path: str, target_size: tuple = (768, 1024)) -> str:
    """
    Resize image to target size while maintaining aspect ratio or padding.
    For VTO, 768x1024 is a common resolution for IDM-VTON.
    """
    img = Image.open(image_path)
    img = img.resize(target_size, Image.Resampling.LANCZOS)
    img.save(image_path)
    return image_path

def remove_background(image_path: str) -> str:
    """
    Remove background from image using rembg (placeholder).
    """
    # from rembg import remove
    # input_image = Image.open(image_path)
    # output_image = remove(input_image)
    # output_image.save(image_path)
    return image_path
