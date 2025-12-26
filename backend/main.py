from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import shutil
import os

from fastapi.staticfiles import StaticFiles

app = FastAPI(title="Virtual Try-On API")

# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")


@app.get("/")
def read_root():
    return {"status": "online", "message": "Virtual Try-On API is running"}

@app.post("/try-on/image")
async def try_on_image(
    person_image: UploadFile = File(...),
    garment_image: UploadFile = File(...),
    category: str = Form("upper_body"),
    segmentation_model: str = Form("sam3") # Default to SAM3
):
    # Save uploaded files
    person_path = os.path.join(UPLOAD_DIR, person_image.filename)
    garment_path = os.path.join(UPLOAD_DIR, garment_image.filename)
    
    with open(person_path, "wb") as buffer:
        shutil.copyfileobj(person_image.file, buffer)
    with open(garment_path, "wb") as buffer:
        shutil.copyfileobj(garment_image.file, buffer)
        
    # 1. Run Segmentation
    from app.models.segmentation import SegmentationFactory
    from PIL import Image
    
    seg_model = SegmentationFactory.get_model(segmentation_model)
    person_pil = Image.open(person_path)
    mask = seg_model.segment(person_pil, category)
    
    # Save mask for debugging
    mask_path = person_path.replace(".jpg", "_mask.jpg").replace(".png", "_mask.png")
    mask.save(mask_path)

    # 2. Call VTO Inference Pipeline (Passing the mask if needed, or VTO does it internally)
    from app.models.vton import vton_pipeline
    
    # Ensure models are loaded (lazy loading or on startup)
    if vton_pipeline.pipe is None:
        vton_pipeline.load_models()
        
    result_path = vton_pipeline.process(person_path, garment_path, category)
    
    return {
        "status": "completed",
        "person_image": person_path,
        "garment_image": garment_path,
        "mask_image": mask_path, # Return mask to verify segmentation
        "result_image": result_path,
        "category": category,
        "segmentation_model": segmentation_model
    }


# Global Model Storage
segmentation_processor = None

@app.on_event("startup")
async def startup_event():
    print(" >>> Starting Model Initialization... (Please Wait) <<<")
    global segmentation_processor
    from app.models.segmentation.processor import SegmentationProcessor
    segmentation_processor = SegmentationProcessor()
    print(" >>> Segmentation Processor Ready! Server is up. <<<")

@app.post("/analyze")
async def analyze_images(
    person_image: UploadFile = File(...),
    model_type: str = Form("b2"),
):
    print(f" [Request Received] Analyze Image Request. Model: {model_type}")
    print(f"                  File: {person_image.filename}")
    from PIL import Image
    import uuid

    # Save uploaded file
    task_id = str(uuid.uuid4())[:8]
    person_filename = f"{task_id}_person_{person_image.filename}"
    person_path = os.path.join(UPLOAD_DIR, person_filename)
    
    with open(person_path, "wb") as buffer:
        shutil.copyfileobj(person_image.file, buffer)
        
    person_pil = Image.open(person_path).convert("RGB")
    
    # Analyze Person (Segmentation)
    person_segments = segmentation_processor.segment_person(person_pil, model_type=model_type)
    
    # Define Categories
    # Define Categories (normalized to lowercase for safety)
    body_labels = {"hair", "face", "left-arm", "right-arm", "left-leg", "right-leg"}
    # clothing_labels = ... (not strictly used for filter logic, everything else is clothing)
    clothing_labels = ["Hat", "Sunglasses", "Upper-clothes", "Skirt", "Pants", "Dress", "Belt", "Left-shoe", "Right-shoe", "Bag", "Scarf"]

    body_parts = []
    clothing_items = []

    for label, segment_img in person_segments.items():
        filename = f"{task_id}_seg_{label}.png"
        path = os.path.join(UPLOAD_DIR, filename)
        segment_img.save(path, format="PNG")
        
        item = {"label": label, "url": f"uploads/{filename}"}
        
        if label.lower() in body_labels:
            body_parts.append(item)
        else:
            # Default to clothing for anything else
            clothing_items.append(item)
    
    return {
        "status": "completed",
        "person_original": f"uploads/{person_filename}",
        "body_parts": body_parts,
        "clothing_items": clothing_items
    }

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
