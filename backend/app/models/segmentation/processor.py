from PIL import Image
import torch
from transformers import SegformerImageProcessor, SegformerForSemanticSegmentation
from rembg import remove
import numpy as np
import io

class SegmentationProcessor:
    def __init__(self):
        print(" [1/3] Initializing Segmentation Processor...")
        print(" [2/3] Downloading/Loading Segformer Model (mattmdjaga/segformer_b2_clothes)...")
        print("       (This may take a while on first run...)")
        self.processor = SegformerImageProcessor.from_pretrained("mattmdjaga/segformer_b2_clothes")
        self.model = SegformerForSemanticSegmentation.from_pretrained("mattmdjaga/segformer_b2_clothes")
        
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model.to(self.device)
        print(f" [3/3] Segmentation Model Successfully Loaded on: {self.device}")

    def segment_person(self, image: Image.Image):
        # Segformer Inference
        inputs = self.processor(images=image, return_tensors="pt").to(self.device)
        with torch.no_grad():
            outputs = self.model(**inputs)
            logits = outputs.logits.cpu()
        
        upsampled_logits = torch.nn.functional.interpolate(
            logits,
            size=image.size[::-1], # PIL size is (W, H), torch needs (H, W)
            mode="bilinear",
            align_corners=False,
        )
        pred_seg = upsampled_logits.argmax(dim=1)[0].numpy()
        
        # Label Map for mattmdjaga/segformer_b2_clothes
        label_map = {
            0: "Background", 1: "Hat", 2: "Hair", 3: "Sunglasses", 
            4: "Upper-clothes", 5: "Skirt", 6: "Pants", 7: "Dress", 
            8: "Belt", 9: "Left-shoe", 10: "Right-shoe", 11: "Face", 
            12: "Left-leg", 13: "Right-leg", 14: "Left-arm", 15: "Right-arm", 
            16: "Bag", 17: "Scarf"
        }
        
        results = {}
        unique_labels = np.unique(pred_seg)
        
        for label_id in unique_labels:
            if label_id == 0: continue # Skip background
            
            label_name = label_map.get(label_id, f"Unknown-{label_id}")
            
            # Binary mask for this label
            mask = (pred_seg == label_id).astype(np.uint8) * 255
            mask_img = Image.fromarray(mask, 'L')
            
            # Extract the actual segment from the original image
            # Create a transparent image
            segment = Image.new("RGBA", image.size)
            original_rgba = image.convert("RGBA")
            segment.paste(original_rgba, (0, 0), mask=mask_img)
            
            results[label_name] = segment
            
        return results

    def remove_background(self, image: Image.Image) -> Image.Image:
        # Use rembg to extract the cloth
        return remove(image)
