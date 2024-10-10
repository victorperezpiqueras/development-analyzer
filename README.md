# Development Analyzer

<img src="https://img.shields.io/static/v1?label=Python&message=3.9&color=blue&logo=Python&logoColor=yellow">

This project provides a simple tool to analyze the flow of development of a project.
By defining the structure of your data, you can easily and periodically fetch, store and analyze it.
Reports provide you valuable insights on the pace of your team, the cycle time of your tasks,
as well as simulations on how would the team perform, giving a confidence interval of possible outcomes
in terms of finishing dates or number of tasks finished, using your historic data.

## Getting Started

### Define your project data structure using a ProjectSchema

To be able to load a json or csv dataset containing your tasks, you'll first need to define your project schema under
the
`/project_schemas` directory. This class defines which columns are mapped to the fields required to generate the
reports.

Example:

```python
from dataclasses import dataclass
from development_analyzer.project_schemas.field import Field
from development_analyzer.project_schemas.project_schema import ProjectSchema


@dataclass
class SampleProjectSchema(ProjectSchema):
    description: Field = Field(column_name="Task title")
    type: Field = Field(column_name="type")
    status: Field = Field(column_name="status", allowed_values=["TODO", "IN PROGRESS", "DONE"])
    created_at: Field = Field(column_name="Created At", format="%Y-%m-%d")
    closed_at: Field = Field(column_name="Closed At", format="%Y-%m-%d")
    estimation: Field = Field(column_name="Story Points")
```

Then, add the schema to the `project_schemas/project_schema_factory.py` file:

```python
from development_analyzer.project_schemas.project_schema import ProjectSchema


def create_project_schema(project_schema_type: str, **kwargs) -> ProjectSchema:
    # [...]
    if project_schema_type == "sample_schema":
        from development_analyzer.project_schemas import SampleProjectSchema
        return SampleProjectSchema(**kwargs)
    # [...]
```

### Optional: load the data automatically from an API using a DataSource:

Currently, there is only 1 datasource implemented for a project management tool: Airtable.
You can create your own datasource by implementing a class as follows:

```python
from development_analyzer.datasources.datasource import DataSource


class SampleApiDataSource(DataSource):
    def import_dataset(self, file_path: str):
        # implement data loading and storing into file_path
        pass
```

Then, add it to the `datasources/datasource_factory.py` file:

```python
from development_analyzer.datasources.datasource import DataSource
from development_analyzer.project_schemas.project_schema import ProjectSchema


def create_datasource(source: str, schema: ProjectSchema, **kwargs) -> DataSource:
    # [...]
    if source == "sample_source":
        from development_analyzer.datasources.sample_datasource import SampleDataSource
        return SampleDataSource(project_schema=schema, **kwargs)
    # [...]
```

You can opt to skip this part if you already have a dataset downloaded, but it can be useful
if it is desired to analyze the data periodically.

## Running the analyzer

### From the command line

To run the analyzer in the cli, simply execute the following command:

`python --source sample_source --project sample_project --dataset datasets/sample_project.csv`

You can find all the available options by running `python main.py --help`.

Upon execution, it will generate a folder such
as: `output/sample_project/<min_task_closing_date>-<max_task_closing_date>/`
that will contain a set of charts with the analysis of your project.

### Automatically in a cloud environment

Under `/serverless_resources`, you can find the code of an AWS Lambda that runs the script for a configuration
defined in environment variables locally, which is uploaded to the lambda on deployment.

The lambda stores the files on S3 and sends them to the desired recipients via email using SES.
The script is run every week using the `serverless-framework` library.

More info on how to deploy it in the `/serverless_resources` [readme](serverless_resources/README.md).

## Sample charts

### Cycle time scatter plot

Displays the tasks with their cycle times in a scatter for the given time frame.
It draws the 50, 85 and 95 percentiles.

How to use it: analyze outlier tasks and discuss the reason of the delays. Understand your team's cycle time,
that is, the number of days that it takes the team to deliver a task 85% of the times (or 50 or 95).

![cycle_times_scatter_plot](/output/sample_project/2024-02-07-2024-03-25/cycle_times_scatter_plot.png)

### Cycle time distribution plot

Similarly, shows the cycle time, but stacking the cycle times in bars, providing a simpler way of seeing
which is the distribution of cycle times of your tasks.
![cycle_times_distribution_plot](/output/sample_project/2024-02-07-2024-03-25/cycle_times_distribution_plot.png)

### Cumulative flow diagram

Allows to see the progress in number of tasks open, in progress and closed.
By analyzing the history, you can find if there is a given type that is increasing at an alarming rate
(for example, too many open tasks are piling up).
![cumulative_flow_diagram](/output/sample_project/2024-02-07-2024-03-25/cumulative_flow_diagram.png)

### Monte Carlo: when would we finish 100 tasks using our historic data

This method estimates a probability distribution of possible scenarios by randomly sampling simulations of your
development
using the data of your history. It then provides the percentiles of confidence of 50, 85, 95, so you can
see how much time would it take the team to finish N tasks with a high confidence.
![monte_carlo_when_will_be_finished_plot_100](/output/sample_project/2024-02-07-2024-03-25/monte_carlo_when_will_be_finished_plot_100.png)

### Monte Carlo: how many tasks can we do in 30 days from now

A similar method, applied to calculating how many tasks would be done in the next N days.
It provides the percentiles of confidence of 50, 85, 95, so you can
see how many tasks the team would do in the next N days with a high confidence.

![monte_carlo_how_many_done_plot_30](/output/sample_project/2024-02-07-2024-03-25/monte_carlo_how_many_done_plot_30.png)
