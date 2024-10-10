from dataclasses import dataclass

from development_analyzer.project_schemas.field import Field
from development_analyzer.project_schemas.project_schema import ProjectSchema


@dataclass
class SampleProjectSchema(ProjectSchema):
    description: Field = Field(column_name="Name")
    type: Field = Field(column_name="Type")
    status: Field = Field(
        column_name="Status", allowed_values=["Todo", "In Progress", "Done"]
    )
    created_at: Field = Field(column_name="createdAt", format="%Y-%m-%dT%H:%M:%S.%fZ")
    started_at: Field = Field(
        column_name="toInProgress", format="%Y-%m-%dT%H:%M:%S.%fZ"
    )
    closed_at: Field = Field(column_name="toDone", format="%Y-%m-%dT%H:%M:%S.%fZ")
    estimation: Field = Field(column_name="Points")
