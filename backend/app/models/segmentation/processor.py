from PIL import Image
import torch
from transformers import SegformerImageProcessor, SegformerForSemanticSegmentation
from rembg import remove
import numpy as np
import io

class SegmentationProcessor:
    def __init__(self):
        print(" [1/7] Initializing Segmentation Processor...")
        
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.processors = {}
        self.models = {}

        # Load B2 (Fast)
        print(" [2/7] Preloading Segformer B2 (Fast)...")
        self.processors['b2'] = SegformerImageProcessor.from_pretrained("mattmdjaga/segformer_b2_clothes")
        self.models['b2'] = SegformerForSemanticSegmentation.from_pretrained("mattmdjaga/segformer_b2_clothes")
        self.models['b2'].to(self.device)

        # Load B5 (Quality)
        print(" [3/7] Preloading Segformer B5 (Quality)...")
        # replaced invalid mattmdjaga b5 with matei-dorian/segformer-b5-finetuned-human-parsing
        self.processors['b5'] = SegformerImageProcessor.from_pretrained("matei-dorian/segformer-b5-finetuned-human-parsing")
        self.models['b5'] = SegformerForSemanticSegmentation.from_pretrained("matei-dorian/segformer-b5-finetuned-human-parsing")
        self.models['b5'].to(self.device)

        # Load SAM (Segment Anything)
        print(" [4/7] Checking SAM Checkpoint...")
        import os
        import urllib.request
        from segment_anything import sam_model_registry, SamAutomaticMaskGenerator
        
        sam_checkpoint = "sam_vit_b_01ec64.pth"
        if not os.path.exists(sam_checkpoint):
            print("       Downloading SAM ViT-B (375MB)... This may take a while.")
            url = "https://dl.fbaipublicfiles.com/segment_anything/sam_vit_b_01ec64.pth"
            urllib.request.urlretrieve(url, sam_checkpoint)
            print("       Download Complete.")
            
        print(" [5/7] Loading SAM Model...")
        sam = sam_model_registry["vit_b"](checkpoint=sam_checkpoint)
        sam.to(device=self.device)
        self.sam_generator = SamAutomaticMaskGenerator(sam)
        
        print(f" [6/7] All Models Successfully Loaded on: {self.device}")
        print(" [7/7] Processor Ready.")

    def segment_person(self, image: Image.Image, model_type: str = "b2"):
        if model_type == 'sam':
            print("Running Segmentation with Model: SAM (Segment Anything)")
            # Convert to numpy array
            image_np = np.array(image)
            masks = self.sam_generator.generate(image_np)
            
            # Sort by area (largest first)
            masks = sorted(masks, key=(lambda x: x['area']), reverse=True)
            
            results = {}
            for i, mask_data in enumerate(masks):
                # Skip tiny segments
                if mask_data['area'] < 500: continue
                
                label_name = f"Region_{i+1}"
                
                # Create mask image
                mask = (mask_data['segmentation'].astype(np.uint8) * 255)
                mask_img = Image.fromarray(mask, 'L')
                
                # Extract segment
                segment = Image.new("RGBA", image.size)
                original_rgba = image.convert("RGBA")
                segment.paste(original_rgba, (0, 0), mask=mask_img)
                
                results[label_name] = segment
                
            return results

        # Segformer Inference
        processor = self.processors.get(model_type, self.processors['b2'])
        model = self.models.get(model_type, self.models['b2'])
        
        print(f"Running Segmentation with Model: Segformer {model_type.upper()}")

        inputs = processor(images=image, return_tensors="pt").to(self.device)
        with torch.no_grad():
            outputs = model(**inputs)
            logits = outputs.logits.cpu()
        
        upsampled_logits = torch.nn.functional.interpolate(
            logits,
            size=image.size[::-1], # PIL size is (W, H), torch needs (H, W)
            mode="bilinear",
            align_corners=False,
        )
        pred_seg = upsampled_logits.argmax(dim=1)[0].numpy()
        
        # Dynamic Label Map from Model Config
        id2label = model.config.id2label
        
        results = {}
        unique_labels = np.unique(pred_seg)
        
        for label_id in unique_labels:
            if label_id == 0: continue # Skip background
            
            # Use dynamic label from config, fallback to Unknown
            label_name = id2label.get(label_id, f"Unknown-{label_id}")
            
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
