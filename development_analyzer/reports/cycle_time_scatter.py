from typing import Optional

from development_analyzer.datasources.datasource import DataSource
from development_analyzer.reports.report import Report
import datetime
from matplotlib import pyplot as plt
from matplotlib.dates import DateFormatter, WeekdayLocator, MonthLocator, YearLocator
import numpy as np


class CycleTimeScatterReport(Report):
    """
    This report will generate a scatter plot of the cycle times for the tasks.
    Attributes
    ----------
    show_labels : bool
        Whether to show the issue keys on the points of the scatter plot
    highlight_last_days : int
        Number of days to highlight in the scatter plot
    """
    show_labels: bool

    def __init__(self, data_source: DataSource, report_path: Optional[str], options: Optional[dict]):
        super().__init__(data_source, report_path, options)
        if not self.options:
            self.options = {"show_labels": False, "highlight_last_days": None}
        self.show_labels = self.options["show_labels"]
        self.highlight_last_days = self.options["highlight_last_days"]

    def generate_report(self):
        # fig = plt.figure(figsize=(10, 10))
        fig, (ax_scatter, ax_table) = plt.subplots(
            1, 2, gridspec_kw={'width_ratios': [2, 4]}, figsize=(30, 10))
        cycle_times_days = [task.cycle_time for task in self.data_source.tasks]

        # get datetimes for done issues:
        date_done_issues = [task.closed_at for task in self.data_source.tasks]

        ax_scatter.scatter(date_done_issues, cycle_times_days,
                           s=20, color='#72cafc')

        labels = []
        dates = []
        cycles = []
        tasks_ordered_by_done_time = sorted(
            self.data_source.tasks, key=lambda x: x.closed_at, reverse=True)
        # put issue keys on points:
        for task in tasks_ordered_by_done_time:
            labels.append(task.full_label)
            dates.append(task.closed_at)
            cycles.append(task.cycle_time)
            if self.show_labels:
                ax_scatter.annotate(
                    task.full_label, (task.closed_at, task.cycle_time))

        # Hide axes for the table subplot
        ax_table.axis('off')
        table = ax_table.table(cellText=[[d.strftime('%Y-%m-%d'), c, l] for d, c, l in zip(dates, cycles, labels)],
                               colWidths=[0.15, 0.10, 0.75], cellLoc='left',
                               colLabels=['Done Date',
                                          'CycleTime', 'Task names'],
                               bbox=[0, 0, 1, 1])
        table.auto_set_font_size(False)
        table.set_fontsize(12)

        today = datetime.datetime.now()
        for (row, col), cell in table.get_celld().items():
            cell.set_text_props(ha='left')

        if self.highlight_last_days:
            # Iterate over rows of the table and color rows based on the condition
            for i in range(1, len(dates) + 1):  # Start from 1 to skip the header row
                done_date = dates[i - 1]
                if done_date > (today - datetime.timedelta(days=self.highlight_last_days)):
                    # Set background color for the row
                    for j in range(3):  # len columns
                        table.get_celld()[i, j].set_facecolor('lightgreen')

        percentile = 95
        confidence_percentile = np.percentile(cycle_times_days, percentile)
        ax_scatter.axhline(y=confidence_percentile, color='green', linestyle='dashed', linewidth=2,
                           label=f"{percentile}% Percentile for Task completion = {confidence_percentile:.2f} days")
        percentile = 85
        confidence_percentile = np.percentile(cycle_times_days, percentile)
        ax_scatter.axhline(y=confidence_percentile, color='orange', linestyle='dashed', linewidth=2,
                           label=f"{percentile}% Percentile for Task completion = {confidence_percentile:.2f} days")
        percentile = 50
        confidence_percentile = np.percentile(cycle_times_days, percentile)
        ax_scatter.axhline(y=confidence_percentile, color='red', linestyle='dashed', linewidth=2,
                           label=f"{percentile}% Percentile for Task completion = {confidence_percentile:.2f} days")

        ax_scatter.set_xlabel('Date')
        ax_scatter.tick_params(axis='x', rotation=90)
        # display only one date per week in x axis:
        from matplotlib.dates import MO
        date_range_in_days = (
                self.data_source.last_closing_date - self.data_source.first_closing_date).days
        # if difference between first and last date is less than 7 days, then show all dates:
        if date_range_in_days < 7:
            ax_scatter.xaxis.set_major_locator(WeekdayLocator())
            ax_scatter.xaxis.set_major_formatter(DateFormatter('%Y-%m-%d'))
        elif date_range_in_days < 90:
            ax_scatter.xaxis.set_major_locator(WeekdayLocator(byweekday=(MO)))
        elif date_range_in_days < 365:
            ax_scatter.xaxis.set_major_locator(MonthLocator())
            ax_scatter.xaxis.set_major_formatter(DateFormatter('%Y-%m'))
        else:
            ax_scatter.xaxis.set_major_locator(YearLocator())
            ax_scatter.xaxis.set_major_formatter(DateFormatter('%Y'))

        ax_scatter.set_ylabel('Cycle Time in Days')
        ax_scatter.legend()

        # get min and max date of done issues:
        data_max_date = self.data_source.last_closing_date + \
                        datetime.timedelta(days=5)
        data_min_date = self.data_source.first_closing_date - \
                        datetime.timedelta(days=5)
        ax_scatter.set_xlim(left=data_min_date, right=data_max_date)

        ax_scatter.set_title(
            f"Cycle Time Scatter Plot for {len(cycle_times_days)} completed tasks {self.estimated_only_label} "
            f"\n(history from {self.data_source.first_closing_date.strftime('%Y-%m-%d')} to "
            f"{self.data_source.last_closing_date.strftime('%Y-%m-%d')})")

        return self.save_report(plt)

    @property
    def report_name(self):
        return "cycle_times_scatter_plot.png"

    @property
    def estimated_only_label(self) -> str:
        return "(Estimated Stories/Tasks)" if self.data_source.filters["has_estimation"] else ""
