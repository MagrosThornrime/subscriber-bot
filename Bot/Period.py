from datetime import timedelta


class Period:
    def _parse_arguments(self, arguments: str) -> list[int]:
        parsed = []
        for argument in arguments.split(":"):
            argument_as_number = int(argument)  # may raise ValueError
            if argument_as_number < 0:
                raise ValueError("Period arguments must be positive integers")
            parsed.append(argument_as_number)
        return parsed

    def __init__(self, arguments: str):
        parsed = self._parse_arguments(arguments)
        self.days = parsed[0]
        self.hours = parsed[1]
        self.minutes = parsed[2]
        self.seconds = parsed[3]

    def as_timedelta(self) -> timedelta:
        return timedelta(
            days=self.days,
            hours=self.hours,
            minutes=self.minutes,
            seconds=self.seconds
        )

    def __str__(self) -> str:
        return f"{self.days}:{self.hours}:{self.minutes}:{self.seconds}"
