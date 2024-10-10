from typing import Optional

from development_analyzer.datasources.datasource import DataSource
from development_analyzer.reports.report import Report
import datetime
from matplotlib import pyplot as plt
import numpy as np


class MonteCarloHowManyDoneReport(Report):
    """
    This report will simulate the number of tasks that will be completed in a given date using a Monte Carlo simulation
    Attributes
    ----------
        finish_date: datetime.date
            Date to simulate the number of tasks that will be completed
        num_simulations: int
            Number of simulations to run with the Monte Carlo simulation
    """
    finish_date: datetime.date
    num_simulations: int

    def __init__(self, data_source: DataSource, report_path: Optional[str], options: Optional[dict]):
        super().__init__(data_source, report_path, options)
        if not options:
            options = {
                "finish_date": datetime.datetime.now().date() + datetime.timedelta(days=30),
                "num_simulations": 1000
            }
        self.finish_date = options["finish_date"]
        self.num_simulations = options["num_simulations"]

    def generate_report(self):
        num_tasks = self._run_simulations()

        plt.figure(figsize=(14, 10))
        num_bins = int((max(num_tasks) - min(num_tasks)) / 2)

        values, bins, bars = plt.hist(num_tasks, bins=num_bins, rwidth=0.9,
                                      label=f"Histogram of Number of tasks done", color='#72cafc')
        if num_bins < 50:
            plt.bar_label(bars, fontsize=10)
        # percentiles are inverted, because closing 10 tasks is more probable than closing 100 tasks (inverse relationship)
        percentile = 95
        confidence_percentile = np.percentile(num_tasks, 100 - percentile)
        plt.axvline(x=confidence_percentile, color='green', linestyle='dashed', linewidth=2,
                    label=f"{percentile}% Percentile of Tasks done = {int(confidence_percentile)}")
        percentile = 85
        confidence_percentile = np.percentile(num_tasks, 100 - percentile)
        plt.axvline(x=confidence_percentile, color='orange', linestyle='dashed', linewidth=2,
                    label=f"{percentile}% Percentile of Tasks done = {int(confidence_percentile)}")
        percentile = 50
        confidence_percentile = np.percentile(num_tasks, 100 - percentile)
        plt.axvline(x=confidence_percentile, color='red', linestyle='dashed', linewidth=2,
                    label=f"{percentile}% Percentile of Tasks done = {int(confidence_percentile)}")

        plt.xlim(left=min(num_tasks), right=max(num_tasks))
        plt.xlabel('Number of Tasks done')
        plt.xticks(rotation=90)

        plt.ylabel('Frequency')
        plt.legend()

        plt.title(
            f"How many tasks will be done by {self.finish_date}\n"
            f"(MCS of {self.num_simulations} runs) "
            f"(history from {self.data_source.first_closing_date.strftime('%Y-%m-%d')} to "
            f"{self.data_source.last_closing_date.strftime('%Y-%m-%d')})")

        return self.save_report(plt)

    def _run_simulations(self) -> list[int]:
        num_tasks_simulations = []
        current_simulation = 0
        print(f"Running {self.num_simulations} simulations of the Monte Carlo simulation for finish date "
              f"{self.finish_date}. Progress: [", end="")
        while current_simulation < self.num_simulations:
            throughput_per_day = self._calculate_throughput_per_day()
            num_tasks = self._calculate_num_tasks(throughput_per_day)
            num_tasks_simulations.append(num_tasks)
            current_simulation += 1
            if current_simulation % 1000 == 0:
                end = "]\n" if current_simulation == self.num_simulations else ""
                print(f".", end=f"{end}")
        return num_tasks_simulations

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

    def _calculate_num_tasks(self, throughput_per_day: dict[datetime.date, int]) -> int:
        current_date = datetime.datetime.now().date()
        done_tasks = 0
        while current_date < self.finish_date:
            random_day = np.random.choice(list(throughput_per_day.keys()))
            random_throughput = throughput_per_day[random_day]
            done_tasks += random_throughput
            current_date += datetime.timedelta(days=1)
        return done_tasks

    @property
    def report_name(self):
        x_days_from_now = (self.finish_date -
                           datetime.datetime.now().date()).days
        return f"monte_carlo_how_many_done_plot_{x_days_from_now}.png"
