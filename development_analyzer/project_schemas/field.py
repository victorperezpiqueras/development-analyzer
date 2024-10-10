from dataclasses import dataclass
from typing import Optional


@dataclass
class Field:
    column_name: str
    format: Optional[str] = None
    allowed_values: Optional[list] = None
