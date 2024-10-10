from abc import ABC, abstractmethod
from typing import Optional

from development_analyzer.datasources.datasource import DataSource


class Report(ABC):

    def __init__(self, data_source: DataSource, report_path: Optional[str], options: Optional[dict]):
        self.data_source = data_source
        self.report_path = report_path
        self.options = options

    @abstractmethod
    def generate_report(self):
        pass

    @property
    @abstractmethod
    def report_name(self):
        pass

    def save_report(self, plt) -> Optional[str]:
        if self.report_path:
            filename = f"{self.report_path}/{self.report_name}"
            plt.savefig(filename)
            print(f"Saved report plot to {filename}")
            return filename
