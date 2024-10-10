from development_analyzer.project_schemas.project_schema import ProjectSchema


def create_project_schema(project_schema_type: str) -> ProjectSchema:
    if project_schema_type in ["sample_project"]:
        from development_analyzer.project_schemas.sample_project_schema import SampleProjectSchema
        return SampleProjectSchema()
    else:
        raise ValueError(f"Invalid type: {project_schema_type}")
