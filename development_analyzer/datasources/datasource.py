import datetime
from abc import ABC, abstractmethod
from typing import Optional

from development_analyzer.project_schemas.project_schema import ProjectSchema
from development_analyzer.task import Task
import pandas as pd
import numpy as np


class DataSource(ABC):
    tasks: list[Task] = []
    filters: dict = {}
    file_path: str
    project_schema: ProjectSchema

    def __init__(self, project_schema: ProjectSchema, **kwargs):
        self.project_schema = project_schema

    def load_dataset(self, file_path: str, file_format: str = "csv"):
        self.file_path = file_path
        if file_format == "csv":
            dataset = pd.read_csv(file_path)
        elif file_format == "json":
            dataset = pd.read_json(file_path)
        else:
            raise ValueError("Invalid format")
        dataset = dataset.replace({np.nan: None})

        def _get_or_default(row, key, default_value=None, converter=None):
            if key not in self.project_schema.fields:
                return default_value

            column_name = self.project_schema.fields[key].column_name
            if column_name in row and row[column_name] is not None:
                if self.project_schema.fields[key].format is not None:
                    return datetime.datetime.strptime(row[column_name], self.project_schema.fields[key].format)
                else:
                    return converter(row[column_name]) if converter else row[column_name]
            else:
                return default_value

        self.tasks = []
        for index, row in dataset.iterrows():
            task = Task(
                type=_get_or_default(row, "type", default_value=None),
                status=_get_or_default(row, "status", default_value=None),
                created_at=_get_or_default(row, "created_at", default_value=None),
                closed_at=_get_or_default(row, "closed_at", default_value=None),
                started_at=_get_or_default(row, "started_at", default_value=None),
                estimation=_get_or_default(row, "estimation", default_value=None, converter=int),
                description=_get_or_default(row, "description", default_value=None)
            )
            self.tasks.append(task)

    def export_dataset(self, file_path: str, file_format: str = "csv"):
        dataset = pd.DataFrame([task.__dict__ for task in self.tasks])
        if file_format == "csv":
            dataset.to_csv(file_path, index=False)
        elif file_format == "json":
            dataset.to_json(file_path, orient="records")
        else:
            raise ValueError("Invalid format")

    @abstractmethod
    def import_dataset(self, file_path: str):
        self.file_path = file_path

    def filter_by(self, created_until: Optional[datetime.datetime],
                  closed_since: Optional[datetime.datetime],
                  closed_until: Optional[datetime.datetime],
                  max_cycle_time: Optional[int],
                  has_estimation: Optional[bool],
                  valid_types: Optional[list[str]]) -> None:
        self.filters = {
            "created_until": created_until,
            "closed_since": closed_since,
            "closed_until": closed_until,
            "max_cycle_time": max_cycle_time,
            "has_estimation": has_estimation,
            "valid_types": valid_types
        }
        new_tasks = []
        for task in self.tasks:
            # logical checks: closed_at > started_at > created_at
            if task.created_at is None or task.closed_at is None:
                continue
            if task.closed_at < task.created_at:
                continue
            if task.started_at and task.started_at < task.created_at:
                continue
            if task.started_at and task.closed_at < task.started_at:
                continue
            # condition checks:
            # created_at < created_until
            if created_until is not None and task.created_at > created_until:
                continue
            # closed_since < closed_at < closed_until
            if closed_since is not None and task.closed_at < closed_since:
                continue
            if closed_until is not None and task.closed_at > closed_until:
                continue
            if max_cycle_time is not None and task.cycle_time > max_cycle_time:
                continue
            if has_estimation and not task.estimation:
                continue
            if valid_types is not None and task.type not in valid_types:
                continue
            new_tasks.append(task)
        self.tasks = new_tasks

    @property
    def have_tasks_started_at(self):
        return "started_at" in self.project_schema.fields

    @property
    def first_creation_date(self):
        if len(self.tasks) == 0:
            return None
        return min(task.created_at for task in [task for task in self.tasks if task.created_at is not None])

    @property
    def first_closing_date(self):
        if len(self.tasks) == 0:
            return None
        return min(task.closed_at for task in [task for task in self.tasks if task.closed_at is not None])

    @property
    def last_closing_date(self):
        if len(self.tasks) == 0:
            return None
        return max(task.closed_at for task in [task for task in self.tasks if task.closed_at is not None])

    @property
    def max_cycle_time(self):
        if len(self.tasks) == 0:
            return None
        return max(task.cycle_time for task in self.tasks if task.cycle_time is not None)
