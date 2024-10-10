from typing import Optional

from development_analyzer.datasources.datasource import DataSource
from development_analyzer.reports.report import Report
from matplotlib import pyplot as plt
import numpy as np


class CycleTimeHistogramReport(Report):
    """
    This report will generate a histogram of the cycle times for the tasks
    """

    def __init__(self, data_source: DataSource, report_path: Optional[str], options: Optional[dict]):
        super().__init__(data_source, report_path, options)

    def generate_report(self):
        plt.figure(figsize=(10, 5))

        cycle_times_days = [task.cycle_time for task in self.data_source.tasks]

        num_bins = int((max(cycle_times_days) - min(cycle_times_days)) / 2)
        values, bins, bars = plt.hist(cycle_times_days, bins=num_bins, rwidth=0.9,
                                      label=f"Histogram of Task cycle times", color="#72cafc")
        if num_bins < 50:
            plt.bar_label(bars, fontsize=10)

        percentile = 95
        confidence_percentile = np.percentile(cycle_times_days, percentile)
        plt.axvline(x=confidence_percentile, color='green', linestyle='dashed', linewidth=2,
                    label=f"{percentile}% Percentile for Task completion = {confidence_percentile:.2f} days")
        percentile = 85
        confidence_percentile = np.percentile(cycle_times_days, percentile)
        plt.axvline(x=confidence_percentile, color='orange', linestyle='dashed', linewidth=2,
                    label=f"{percentile}% Percentile for Task completion = {confidence_percentile:.2f} days")
        percentile = 50
        confidence_percentile = np.percentile(cycle_times_days, percentile)
        plt.axvline(x=confidence_percentile, color='red', linestyle='dashed', linewidth=2,
                    label=f"{percentile}% Percentile for Task completion = {confidence_percentile:.2f} days")

        plt.xlim(left=0, right=self.data_source.max_cycle_time)
        plt.xlabel('Cycle Time in Days')

        # calculate the tick gap so that for 10 bins its 1, for 50 bins its 5, for 100 bins its 10, and for more than 100 its 20
        tick_gap = 1 if self.data_source.max_cycle_time < 30 \
            else 5 if self.data_source.max_cycle_time < 100 \
            else 10 if self.data_source.max_cycle_time < 200 \
            else 50
        plt.xticks(np.arange(1, self.data_source.max_cycle_time, tick_gap))
        plt.ylabel('Number of Tasks')
        plt.legend()

        plt.title(
            f"Cycle Time Distribution for {len(self.data_source.tasks)} completed tasks {self.estimated_only_label} "
            f"\n(history from {self.data_source.first_closing_date.strftime('%Y-%m-%d')} to "
            f"{self.data_source.last_closing_date.strftime('%Y-%m-%d')})")

        return self.save_report(plt)

    @property
    def report_name(self):
        return "cycle_times_distribution_plot.png"

    @property
    def estimated_only_label(self) -> str:
        return "(Estimated Stories/Tasks)" if self.data_source.filters["has_estimation"] else ""
