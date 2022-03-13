from typing import Dict
from pydantic import BaseModel


class AnyObject(BaseModel):
    """Any JSON mapping object"""

    __root__: Dict
