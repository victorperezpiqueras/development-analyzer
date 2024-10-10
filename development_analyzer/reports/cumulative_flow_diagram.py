from typing import Optional
from development_analyzer.datasources.datasource import DataSource
from development_analyzer.reports.report import Report
import datetime
from matplotlib import pyplot as plt
from matplotlib.dates import DateFormatter, WeekdayLocator, MonthLocator, YearLocator


class CumulativeFlowDiagramReport(Report):
    """
    Cumulative Flow Diagram (CFD) report. 
    Attributes
    ----------
    """
    show_labels: bool

    def __init__(self, data_source: DataSource, report_path: Optional[str], options: Optional[dict]):
        super().__init__(data_source, report_path, options)

    def generate_report(self):
        frequencies = self._calculate_frequencies()
        bands = self._calculate_bands(frequencies)
        plt.figure(figsize=(12, 10))

        dates = [band[0] for band in bands["To Do"]]
        data = {
            key: [band[1] for band in bands[key]] for key, item in bands.items()
        }

        plt.fill_between(dates, data["To Do"], data["In Progress"], label="To Do", color="#e60049", alpha=1)
        plt.fill_between(dates, data["In Progress"], data["Done"], label="In Progress", color="#ef9b20", alpha=1)
        plt.fill_between(dates, data["Done"], label="Done", color="#87bc45", alpha=1)

        plt.xlabel('Date')
        plt.xticks(rotation=90)
        # display only one date per week in x axis:
        from matplotlib.dates import MO
        date_range_in_days = (
                self.data_source.last_closing_date - self.data_source.first_closing_date).days
        # if difference between first and last date is less than 7 days, then show all dates:
        if date_range_in_days < 7:
            plt.gca().xaxis.set_major_locator(WeekdayLocator())
            plt.gca().xaxis.set_major_formatter(DateFormatter('%Y-%m-%d'))
        elif date_range_in_days < 90:
            plt.gca().xaxis.set_major_locator(WeekdayLocator(byweekday=(MO)))
        elif date_range_in_days < 365:
            plt.gca().xaxis.set_major_locator(MonthLocator())
            plt.gca().xaxis.set_major_formatter(DateFormatter('%Y-%m'))
        else:
            plt.gca().xaxis.set_major_locator(YearLocator())
            plt.gca().xaxis.set_major_formatter(DateFormatter('%Y'))

        plt.ylabel('Work Item Frequency')
        plt.legend()

        # get min and max date of done issues:
        data_max_date = self.data_source.last_closing_date
        data_min_date = self.data_source.first_closing_date
        plt.xlim(left=data_min_date.date(), right=data_max_date.date())
        plt.ylim(bottom=0)
        # add grid:
        plt.grid(True)

        plt.title(
            f"Cumulative Flow Diagram\n"
            f"(history from {self.data_source.first_closing_date.strftime('%Y-%m-%d')} to "
            f"{self.data_source.last_closing_date.strftime('%Y-%m-%d')})")

        return self.save_report(plt)

    def _calculate_frequencies(self) -> dict[str, list[tuple[str, int]]]:
        frequencies = {
            "Done": [],
            "In Progress": [],
            "To Do": [],
        }
        for i, day in enumerate(
                range((self.data_source.last_closing_date - self.data_source.first_creation_date).days + 1)):
            day = self.data_source.first_creation_date + datetime.timedelta(days=day)
            todo = frequencies["To Do"][i - 1][1] if i > 0 else 0
            in_progress = frequencies["In Progress"][i - 1][1] if i > 0 else 0
            done = frequencies["Done"][i - 1][1] if i > 0 else 0
            for task in self.data_source.tasks:
                if task.created_at is not None and task.created_at.date() == day.date():
                    todo += 1
                if task.started_at is not None and task.started_at.date() == day.date():
                    in_progress += 1
                if task.closed_at is not None and task.closed_at.date() == day.date():
                    done += 1
            frequencies["To Do"].append((day, todo))
            frequencies["In Progress"].append((day, in_progress))
            frequencies["Done"].append((day, done))

        return frequencies

    def _calculate_bands(self, frequencies: dict[str, list[tuple[str, int]]]) -> dict[str, list[tuple[str, int]]]:
        bands = {
            "Done": [],
            "In Progress": [],
            "To Do": [],
        }

        for i, day in enumerate(
                range((self.data_source.last_closing_date - self.data_source.first_creation_date).days + 1)):
            day = self.data_source.first_creation_date + datetime.timedelta(days=day)
            todo = frequencies["To Do"][i][1]
            in_progress = frequencies["In Progress"][i][1]
            done = frequencies["Done"][i][1]
            bands["To Do"].append((day, todo + in_progress + done))
            bands["In Progress"].append((day, in_progress + done))
            bands["Done"].append((day, done))

        return bands

    @property
    def report_name(self):
        return "cumulative_flow_diagram.png"
