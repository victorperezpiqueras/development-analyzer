import argparse
import datetime

from development_analyzer import DevelopmentAnalyzer
from development_analyzer.datasources.datasource_factory import create_datasource
from development_analyzer.project_schemas.project_schema_factory import (
    create_project_schema,
)

if __name__ == "__main__":
    # read params from command line
    parser = argparse.ArgumentParser(
        description=f"Development Analyzer of a dataset of tasks. "
        f"It will read a dataset from a source and project schema,"
        f"and will plot some charts to analyze the development process."
    )
    parser.add_argument("--source", "-s", type=str, help="Data source (airtable, others)")
    parser.add_argument("--project", "-p", type=str, help="Project schema code")
    parser.add_argument(
        "--dataset",
        "-d",
        type=str,
        help="Dataset file path from current directory. Valid formats: csv, json",
    )
    parser.add_argument(
        "--regenerate",
        "-r",
        action="store_true",
        help="Regenerate the dataset from the external source",
    )
    parser.add_argument(
        "--max_cycle_time",
        type=int,
        default=None,
        help="Filter out tasks that had a cycle time in days greater than the given value",
    )
    parser.add_argument(
        "--created_last",
        type=int,
        default=None,
        help="Filter out tasks that were created more than the given number of days ago",
    )
    parser.add_argument(
        "--closed_last",
        type=int,
        default=None,
        help="Filter out tasks that were closed more than the given number of days ago",
    )
    parser.add_argument(
        "--need_estimate",
        "-e",
        action="store_true",
        help="Filter out tasks that do not have an estimation",
    )
    args = parser.parse_args()

    project_schema = create_project_schema(args.project)

    datasource = create_datasource(source=args.source, schema=project_schema)
    if args.regenerate:
        datasource.import_dataset(args.dataset)

    datasource.load_dataset(args.dataset)

    created_until = (
        datetime.datetime.now() - datetime.timedelta(days=args.created_last)
        if args.created_last
        else datetime.datetime.now()
    )
    closed_since = (
        datetime.datetime.now() - datetime.timedelta(days=args.closed_last)
        if args.closed_last
        else None
    )
    closed_until = datetime.datetime.now()
    has_estimation = args.need_estimate
    max_cycle_time = args.max_cycle_time

    datasource.filter_by(
        created_until=created_until,
        closed_since=closed_since,
        closed_until=closed_until,
        max_cycle_time=max_cycle_time,
        has_estimation=has_estimation,
        valid_types=None,
    )

    analyzer = DevelopmentAnalyzer(datasource)
    analyzer.plot_scatter(show_labels=False)
    analyzer.plot_histogram()
    analyzer.plot_cycle_time_estimation_relationship()
    analyzer.plot_monte_carlo_when_will_be_finished(num_tasks=100)
    analyzer.plot_monte_carlo_how_many_done(next_x_days=30)
    analyzer.plot_cumulative_flow_diagram()
