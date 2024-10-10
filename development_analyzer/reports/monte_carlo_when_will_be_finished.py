from typing import Optional

from development_analyzer.datasources.datasource import DataSource
from development_analyzer.reports.report import Report
import datetime
from matplotlib import pyplot as plt
from matplotlib.dates import DateFormatter, WeekdayLocator, MonthLocator, YearLocator
import numpy as np


class MonteCarloWhenWillBeFinishedReport(Report):
    """
    This report will simulate the finish date of the project using a Monte Carlo simulation
    Attributes
    ----------
        num_tasks: int
            Number of tasks that are expected to be completed
        num_simulations: int
            Number of simulations to run with the Monte Carlo simulation
    """
    num_tasks: int
    num_simulations: int

    def __init__(self, data_source: DataSource, report_path: Optional[str], options: Optional[dict]):
        super().__init__(data_source, report_path, options)
        if not options:
            options = {
                "num_tasks": 100,
                "num_simulations": 1000
            }
        self.num_tasks = options["num_tasks"]
        self.num_simulations = options["num_simulations"]

    def generate_report(self):
        finish_dates = self._run_simulations()

        plt.figure(figsize=(14, 10))
        # display only one date per week in x axis:
        from matplotlib.dates import MO
        # if difference between first and last date is less than 7 days, then show all dates:
        max_date = max(set(finish_dates))
        min_date = min(set(finish_dates))
        date_range_in_days = (max_date - min_date).days
        if date_range_in_days < 60:
            num_bins = date_range_in_days
        else:
            num_bins = 60

        values, bins, bars = plt.hist(finish_dates, bins=num_bins, rwidth=0.9, label=f"Histogram of Finish Dates",
                                      color='#72cafc')
        if num_bins < 50:
            plt.bar_label(bars, fontsize=10)

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

        percentile = 95
        confidence_percentile = np.percentile(finish_dates, percentile)
        plt.axvline(x=confidence_percentile, color='green', linestyle='dashed', linewidth=2,
                    label=f"{percentile}% Percentile for Finish Date = {confidence_percentile.strftime('%Y-%m-%d')}")
        percentile = 85
        confidence_percentile = np.percentile(finish_dates, percentile)
        plt.axvline(x=confidence_percentile, color='orange', linestyle='dashed', linewidth=2,
                    label=f"{percentile}% Percentile for Finish Date = {confidence_percentile.strftime('%Y-%m-%d')}")
        percentile = 50
        confidence_percentile = np.percentile(finish_dates, percentile)
        plt.axvline(x=confidence_percentile, color='red', linestyle='dashed', linewidth=2,
                    label=f"{percentile}% Percentile for Finish Date = {confidence_percentile.strftime('%Y-%m-%d')}")

        plt.xlim(left=min_date, right=max_date)
        plt.xlabel('Finish Date')
        plt.xticks(rotation=90)

        plt.ylabel('Frequency')
        plt.legend()

        plt.title(
            f"When will {self.num_tasks} tasks be finished\n"
            f"(MCS of {self.num_simulations} runs) "
            f"(history from {self.data_source.first_closing_date.strftime('%Y-%m-%d')} to "
            f"{self.data_source.last_closing_date.strftime('%Y-%m-%d')})")

        return self.save_report(plt)

    def _run_simulations(self) -> list[datetime.date]:
        finish_date_simulations = []
        current_simulation = 0
        print(f"Running {self.num_simulations} simulations of the Monte Carlo simulation for {self.num_tasks} tasks."
              f" Progress: [",
              end='')
        while current_simulation < self.num_simulations:
            throughput_per_day = self._calculate_throughput_per_day()
            finish_date = self._calculate_finish_date(throughput_per_day)
            finish_date_simulations.append(finish_date)
            current_simulation += 1
            if current_simulation % 1000 == 0:
                end = "]\n" if current_simulation == self.num_simulations else ""
                print(f".", end=f"{end}")
        return finish_date_simulations

    def _calculate_throughput_per_day(self) -> dict[datetime.date, int]:
        throughput_per_day = {}
        for task in self.data_source.tasks:
            if not task.closed_at:
                continue
            if task.closed_at.date() in throughput_per_day:
                throughput_per_day[task.closed_at.date()] += 1
            else:
                throughput_per_day[task.closed_at.date()] = 1

        return throughput_per_day

    def _calculate_finish_date(self, throughput_per_day: dict[datetime.date, int]) -> datetime.date:
        current_date = datetime.datetime.now().date()
        remaining_tasks = self.num_tasks
        while remaining_tasks > 0:
            random_day = np.random.choice(list(throughput_per_day.keys()))
            random_throughput = throughput_per_day[random_day]
            remaining_tasks -= random_throughput
            current_date += datetime.timedelta(days=1)
        return current_date

    @property
    def report_name(self):
        return f"monte_carlo_when_will_be_finished_plot_{self.num_tasks}.png"
