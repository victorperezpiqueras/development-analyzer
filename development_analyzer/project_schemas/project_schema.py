from abc import ABC
from dataclasses import dataclass

from development_analyzer.project_schemas.field import Field


@dataclass
class ProjectSchema(ABC):
    description: Field
    type: Field
    status: Field
    created_at: Field
    closed_at: Field

    @property
    def fields(self) -> dict:
        return {key: value for key, value in self.__dict__.items() if isinstance(value, Field)}
