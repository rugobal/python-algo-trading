import os
from typing import Any, Dict
import yaml

def get_config(strategy: str) -> Dict[str, Any]:
    dir_path = os.path.dirname(os.path.realpath(__file__))
    file_path = os.path.join(dir_path, '..', 'config.yaml')
    with open(file_path, 'r') as file:
        return yaml.safe_load(file)[strategy]