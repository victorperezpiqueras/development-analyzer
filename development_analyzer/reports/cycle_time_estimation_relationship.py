from scipy.stats import stats

from development_analyzer.reports.report import Report
from matplotlib import pyplot as plt
import numpy as np


class CycleTimeEstimationRelationshipReport(Report):
    """
    This report will generate a relationship between the cycle time and the estimation of the tasks
    """

    def generate_report(self):
        plt.figure(figsize=(14, 8))
        estimations = [task.estimation for task in self.data_source.tasks if task.estimation and
                       task.cycle_time]
        cycle_times_days = [task.cycle_time for task in self.data_source.tasks if task.estimation and
                            task.cycle_time]
        plt.scatter(estimations, cycle_times_days, color='#72cafc')

        # add a linear regression
        regression_label = ""
        if len(estimations) > 1:
            slope, intercept, r_value, p_value, std_err = stats.linregress(
                estimations, cycle_times_days)
            line = slope * np.array(estimations) + intercept
            plt.plot(estimations, line, 'r-', label='Regression line')
            regression_label = "(R^2= {:.2f})".format(r_value ** 2)

        plt.xticks([1, 2, 3, 5, 8, 13, 20])
        plt.xlabel('Estimation')
        plt.ylabel('Cycle Time in Days')
        plt.title(f"Cycle Time vs Estimation {regression_label}"
                  f"\n(history from {self.data_source.first_closing_date.strftime('%Y-%m-%d')} to "
                  f"{self.data_source.last_closing_date.strftime('%Y-%m-%d')})")

        return self.save_report(plt)

    @property
    def report_name(self):
        return "cycle_time_vs_story_points.png"
