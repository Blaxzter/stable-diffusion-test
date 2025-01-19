import json
from enum import Enum
import numpy as np
from typing import Any, Dict


class ComplexEncoder(json.JSONEncoder):
    def default(self, obj: Any) -> Any:
        if isinstance(obj, Enum):
            return obj.value
        if isinstance(obj, np.bool):
            return bool(obj)
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        if isinstance(obj, (bool, int, float, str)):
            return obj
        if hasattr(obj, "__dict__"):
            return self._clean_dict(obj.__dict__)
        
        # log the type of obj that was not serialized
        print(f"Type not serializable: {type(obj)}")
        
        return super().default(obj)

    def _clean_dict(self, d: Dict) -> Dict:
        cleaned = {}
        for k, v in d.items():
            if isinstance(v, (Enum, np.integer, np.floating, np.ndarray)):
                cleaned[k] = self.default(v)
            elif isinstance(v, dict):
                cleaned[k] = self._clean_dict(v)
            elif isinstance(v, list):
                cleaned[k] = [self.default(item) for item in v]
            else:
                cleaned[k] = v
        return cleaned
