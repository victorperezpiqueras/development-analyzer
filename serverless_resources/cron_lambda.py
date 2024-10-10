import json

import datetime
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import os

# set MPLCONFIGDIR to /tmp to avoid permission issues
# if lambda env:
if os.environ.get("AWS_EXECUTION_ENV") is not None:
    os.chdir("/tmp")
    os.environ["MPLCONFIGDIR"] = os.getcwd() + "/matplotlib"

from development_analyzer import DevelopmentAnalyzer
from development_analyzer.datasources.datasource_factory import create_datasource
from development_analyzer.project_schemas.project_schema_factory import (
    create_project_schema,
)
import boto3

if os.environ.get("AWS_EXECUTION_ENV") is None:  # testing
    # open .env_full.json
    with open("serverless_resources/.env_full.json") as f:
        data = json.load(f)
        os.environ["PROJECTS"] = json.dumps(data["projects"])
        os.environ["SENDER_EMAIL"] = data["sender_email"]


def handler(event, context):
    # TODO: use events to run specific plots
    projects = json.loads(os.environ["PROJECTS"])

    override_email_list = event.get("email_list", None)
    if override_email_list:
        for project in projects:
            project["email_list"] = override_email_list
        print(f"Email list overridden to {override_email_list}")

    for project in projects:
        os.environ["AIRTABLE_API_KEY"] = project["AIRTABLE_API_KEY"]
        os.environ["AIRTABLE_BASE"] = project["AIRTABLE_BASE"]
        os.environ["AIRTABLE_TABLE"] = project["AIRTABLE_TABLE"]
        try:
            files = _scan_project(
                project=project["name"],
                source=project["source"],
                dataset_file=project["dataset"],
                regenerate=project["regenerate"],
                max_cycle_time=project["max_cycle_time"],
                created_last=project["created_last"],
                closed_last=project["closed_last"],
                need_estimate=project["need_estimate"],
            )
        except Exception as e:
            print(f'Error processing project {project["name"]}: {str(e)}')
            _send_error_email(e)
            continue
        # send SES email with the reports
        _send_email(project, files)
        _store_reports(project, files)


def _scan_project(
    project,
    source,
    dataset_file,
    regenerate,
    max_cycle_time,
    created_last,
    closed_last,
    need_estimate,
):
    dataset_file = f"/tmp/{dataset_file}"
    project_schema = create_project_schema(project)

    datasource = create_datasource(source=source, schema=project_schema)
    if regenerate:
        datasource.import_dataset(dataset_file)

    datasource.load_dataset(dataset_file)

    created_until = (
        datetime.datetime.now() - datetime.timedelta(days=created_last)
        if created_last
        else datetime.datetime.now()
    )
    closed_since = (
        datetime.datetime.now() - datetime.timedelta(days=closed_last)
        if closed_last
        else None
    )
    closed_until = datetime.datetime.now()
    has_estimation = need_estimate
    max_cycle_time = max_cycle_time

    datasource.filter_by(
        created_until=created_until,
        closed_since=closed_since,
        closed_until=closed_until,
        max_cycle_time=max_cycle_time,
        has_estimation=has_estimation,
        valid_types=None,
    )

    analyzer = DevelopmentAnalyzer(datasource)
    reports = [
        analyzer.plot_scatter(show_labels=False, highlight_last_days=7),
        analyzer.plot_histogram(),
        analyzer.plot_cumulative_flow_diagram(),
    ]

    # return report names:
    return reports


def _send_email(project: dict, report_paths: list[str]):
    ses_client = boto3.client("ses", region_name=os.environ["AWS_REGION"])

    msg = MIMEMultipart()
    msg["Subject"] = f'Weekly report for {project["name"]}'
    # Add a text message to the email
    msg.attach(
        MIMEText(f'Plot using data of the last {project["closed_last"]} days', "plain")
    )

    for report_path in report_paths:
        with open(report_path, "rb") as buffer:
            # Add the plot file as an attachment
            attachment = MIMEApplication(buffer.read())
            attachment.add_header(
                "Content-Disposition",
                "attachment",
                filename=os.path.basename(report_path),
            )
            msg.attach(attachment)

    source = os.environ["SENDER_EMAIL"]
    destinations = project["email_list"]
    try:
        response = ses_client.send_raw_email(
            Source=source,
            Destinations=destinations,
            RawMessage={"Data": msg.as_string()},
        )
        print("Email sent successfully:", response["MessageId"])
    except Exception as e:
        print("Email sending failed:", str(e))


def _send_error_email(exception: Exception):
    ses_client = boto3.client("ses", region_name=os.environ["AWS_REGION"])

    msg = MIMEMultipart()
    msg["Subject"] = f"Error processing weekly reports"
    # Add a text message to the email
    msg.attach(
        MIMEText(
            f"Error processing weekly reports: {exception.__class__.__name__} - {str(exception)}",
            "plain",
        )
    )

    source = os.environ["SENDER_EMAIL"]
    destinations = [json.loads(os.environ["ERROR_EMAIL"])]
    try:
        response = ses_client.send_raw_email(
            Source=source,
            Destinations=destinations,
            RawMessage={"Data": msg.as_string()},
        )
        print("Email sent successfully:", response["MessageId"])
    except Exception as e:
        print("Email sending failed:", str(e))


def _store_reports(project: dict, report_paths: list[str]):
    s3_client = boto3.client("s3")
    s3_bucket = os.environ["S3_BUCKET"]
    for report_path in report_paths:
        with open(report_path, "rb") as buffer:
            s3_client.upload_fileobj(buffer, s3_bucket, f"{report_path}")
        print(
            f'Reports for project {project["name"]} stored in s3://{s3_bucket}/{report_path}/'
        )


if __name__ == "__main__":
    handler(
        {
            "email_list": ["email@email.com"],
        },
        {},
    )
