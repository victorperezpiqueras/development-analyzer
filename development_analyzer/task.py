import datetime
from dataclasses import dataclass
from typing import Optional


@dataclass
class Task:
    type: str
    status: str
    created_at: datetime.datetime
    closed_at: datetime.datetime
    started_at: Optional[datetime.datetime]
    estimation: Optional[int]
    description: Optional[str]

    @property
    def cycle_time(self) -> Optional[int]:
        if self.started_at:
            if self.closed_at is None or self.started_at is None:
                return None
            return (self.closed_at - self.started_at).days + 1
        else:  # not ideal, but we need to handle the case where the task does not have a started_at date
            if self.closed_at is None or self.created_at is None:
                return None
            return (self.closed_at - self.created_at).days + 1

    @property
    def full_label(self) -> str:
        estimation = f" ({self.estimation} points)" if self.estimation else ""
        return f"{self.description}{estimation}"

    @property
    def label(self) -> str:
        estimation = f" ({self.estimation} points)" if self.estimation else ""
        description = f"{self.description[:20] + '...'}" if self.description else "<no description>"
        return f"{description}{estimation}"
