from development_analyzer.datasources.datasource import DataSource
from development_analyzer.project_schemas.project_schema import ProjectSchema


def create_datasource(source: str, schema: ProjectSchema, **kwargs) -> DataSource:
    if source == "airtable":
        from development_analyzer.datasources.airtable_datasource import AirtableDataSource
        return AirtableDataSource(project_schema=schema, **kwargs)
    else:
        raise ValueError(f"Invalid type: {source}")
