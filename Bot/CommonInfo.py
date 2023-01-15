from dataclasses import dataclass


@dataclass
class CommonInfo:
    tag: str
    channel: str
    when_to_start: str
    period: str
    count: str

    def __str__(self):
        return f"Tag: {self.tag}\n" \
                f"Channel: {self.channel}\n" \
                f"When to start: {self.when_to_start}\n" \
                f"Period: {self.period}\n" \
                f"Count: {self.count}"
