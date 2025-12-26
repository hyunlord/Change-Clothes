from .sam3 import SAM3Segmentation
from .schp import SCHPSegmentation

class SegmentationFactory:
    _models = {
        "sam3": SAM3Segmentation,
        "schp": SCHPSegmentation
    }
    
    _instances = {}

    @classmethod
    def get_model(cls, model_name: str):
        if model_name not in cls._models:
            raise ValueError(f"Unknown segmentation model: {model_name}")
            
        if model_name not in cls._instances:
            instance = cls._models[model_name]()
            instance.load_model()
            cls._instances[model_name] = instance
            
        return cls._instances[model_name]
