from datetime import datetime
from typing import Any

import pytz

EASTERN = pytz.timezone("America/New_York")


def _is_leap(year: int) -> bool:
    return year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)


def convert_time(time_input: str) -> dict[str, Any]:
    """Parse `time_input` from a Postgres timestamp, ISO-8601, or epoch (s/ms) and
    return the same dict shape the legacy Flask route produced."""
    parsed: datetime | None = None

    if " " in time_input and "-" in time_input and ":" in time_input:
        try:
            naive = datetime.strptime(time_input, "%Y-%m-%d %H:%M:%S")
            parsed = EASTERN.localize(naive, is_dst=None)
        except ValueError:
            parsed = None

    if parsed is None:
        try:
            parsed = datetime.fromisoformat(time_input)
            parsed = parsed.astimezone(EASTERN)
        except ValueError:
            pass

    if parsed is None:
        try:
            parsed = datetime.fromtimestamp(float(time_input), tz=pytz.utc).astimezone(EASTERN)
        except ValueError:
            try:
                parsed = datetime.fromtimestamp(
                    float(time_input) / 1000, tz=pytz.utc
                ).astimezone(EASTERN)
            except ValueError:
                parsed = None

    if parsed is None:
        raise ValueError("Input time format not recognized.")

    et = parsed.astimezone(EASTERN)
    return {
        "Local Time": et.strftime("%m/%d/%Y, %I:%M:%S %p"),
        "UTC Time": et.astimezone(pytz.utc).strftime("%a, %d %b %Y %H:%M:%S GMT"),
        "UNIX Time": str(int(et.timestamp())),
        "Day of week": et.strftime("%A"),
        "Day of year": str(et.timetuple().tm_yday),
        "Is leap year?": "Yes" if _is_leap(et.year) else "No",
        "Other date formats (local time)": [
            et.strftime("%Y-%m-%d"),
            et.strftime("%m-%d-%Y"),
            et.strftime("%Y/%m/%d"),
            et.strftime("%m/%d/%Y"),
            et.strftime("%a %B %d, %Y"),
            et.strftime("%A %B %d, %Y"),
            et.strftime("%a %b %d, %Y"),
            et.strftime("%A %b %d, %Y"),
        ],
        "ISO Format": et.strftime("%Y-%m-%dT%H:%M:%S") + "Z",
    }
