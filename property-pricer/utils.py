import json
import numpy as np

class CustomEncoder(json.JSONEncoder):
    """
    Helper class to override default data structures
    to make them JSON serializable.
    """
    def default(self, obj):
        if isinstance(obj, set):
            return list(obj)
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return json.JSONEncoder.default(self, obj)

def save_json(filepath : str, json_data : dict)-> None:
    """
    Saves json data to a relative filepath
    
    Parameters
    ----------
    filepath : str
        Specifies the relative path to save the 
        json file
    json_data : dict
        JSON data to be saved
    """
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(
            json_data, f, cls=CustomEncoder, 
            ensure_ascii=False, indent=4
        )
    return