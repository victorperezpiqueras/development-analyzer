import datetime

from development_analyzer.datasources.datasource import DataSource
import os

from development_analyzer.reports.cumulative_flow_diagram import CumulativeFlowDiagramReport
from development_analyzer.reports.cycle_time_estimation_relationship import CycleTimeEstimationRelationshipReport
from development_analyzer.reports.cycle_time_histogram import CycleTimeHistogramReport
from development_analyzer.reports.cycle_time_scatter import CycleTimeScatterReport
from development_analyzer.reports.monte_carlo_how_many_done import MonteCarloHowManyDoneReport
from development_analyzer.reports.monte_carlo_when_will_be_finished import MonteCarloWhenWillBeFinishedReport


class DevelopmentAnalyzer:
    def __init__(self, data_source: DataSource, show_plots: bool = False,
                 output_folder: str = None):
        self.data_source = data_source
        self.show_plots = show_plots
        if output_folder:
            self.output_folder = output_folder
        else:
            filename = self.data_source.file_path.split("/")[-1].split(".")[0]
            self.output_folder = (f"output/{filename}/{self.data_source.first_creation_date.strftime('%Y-%m-%d')}-"
                                  f"{self.data_source.last_closing_date.strftime('%Y-%m-%d')}")
        # check if output folder exists, if not create it:
        if not os.path.exists(self.output_folder):
            os.makedirs(self.output_folder)

    def plot_scatter(self, show_labels: bool = False, highlight_last_days: int = None):
        try:
            report = CycleTimeScatterReport(self.data_source, self.output_folder, {
                "show_labels": show_labels,
                "highlight_last_days": highlight_last_days})
            return report.generate_report()
        except Exception as e:
            print(f"Error plotting scatter: {e}")

    def plot_histogram(self):
        try:
            report = CycleTimeHistogramReport(self.data_source, self.output_folder, None)
            return report.generate_report()
        except Exception as e:
            print(f"Error plotting scatter: {e}")

    def plot_cycle_time_estimation_relationship(self):
        try:
            report = CycleTimeEstimationRelationshipReport(self.data_source, self.output_folder, None)
            return report.generate_report()
        except Exception as e:
            print(f"Error plotting scatter: {e}")

    def plot_monte_carlo_when_will_be_finished(self, num_tasks: int = 100, num_simulations: int = 10000):
        try:
            report = MonteCarloWhenWillBeFinishedReport(self.data_source, self.output_folder,
                                                        options={"num_tasks": num_tasks,
                                                                 "num_simulations": num_simulations})
            return report.generate_report()
        except Exception as e:
            print(f"Error plotting scatter: {e}")

    def plot_monte_carlo_how_many_done(self, next_x_days: int = 30, num_simulations: int = 10000):
        try:
            finish_date = datetime.datetime.now().date() + datetime.timedelta(days=next_x_days)
            report = MonteCarloHowManyDoneReport(self.data_source, self.output_folder,
                                                 options={"finish_date": finish_date,
                                                          "num_simulations": num_simulations})
            return report.generate_report()
        except Exception as e:
            print(f"Error plotting scatter: {e}")

    def plot_cumulative_flow_diagram(self):
        try:
            report = CumulativeFlowDiagramReport(self.data_source, self.output_folder, None)
            return report.generate_report()
        except Exception as e:
            print(f"Error plotting scatter: {e}")
