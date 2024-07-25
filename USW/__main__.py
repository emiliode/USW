import argparse
import datetime
import math
import tomllib
from pathlib import Path
from typing import Any, Optional

import icalendar
import recurring_ical_events
import requests

from .config import Config, Course, Source, SourceType


def formatdd(begin: datetime.datetime, end: datetime.datetime) -> str:
    minutes = math.ceil((end - begin).total_seconds() / 60)

    if minutes == 1:
        return '1 minute'

    if minutes < 60:
        return f'{minutes}min'

    hours = math.floor(minutes/60)
    rest_minutes = minutes % 60

    if hours > 5 or rest_minutes == 0:
        return f'{hours}h'

    return '{}:{:02d}h'.format(hours, rest_minutes)


def load_config_file(config_file: Path) -> dict[str, Any]:
    with open(config_file, "rb") as f:
        return tomllib.load(f)


def get_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="usw",
        description="Util to list your uni schedule",
        epilog="Help finished"
    )
    parser.add_argument("-c", "--config", nargs="?", dest="config_file", default="~/.config/usw/usw.cfg")
    parser.add_argument("-t", "--time", nargs="?", type=lambda s: datetime.datetime.strptime(s,
                        "%Y-%m-%dT%H:%M").astimezone(),
                        dest="current_time", default=datetime.datetime.now().astimezone())
    parser.add_argument("--print-config", action="store_true", dest="print_config")
    parser.add_argument("sources", nargs='*')
    return parser.parse_args()


def load_sources(sources: list[Source]) -> icalendar.Calendar:
    calendar = icalendar.Calendar()
    for source in sources:
        if source.type == SourceType.WEB:
            ical_string = requests.get(source.path).text
        else:
            with open(source.path) as f:
                ical_string = f.read()
        temp_cal: icalendar.Calendar = icalendar.Calendar.from_ical(ical_string)
        for event in temp_cal.walk('VEVENT'):
            calendar.add_component(event)
    return calendar


def main() -> None:
    args = get_args()

    config = Config(args, load_config_file(Path(args.config_file).expanduser()))

    now = config.current_time
    if (args.print_config):
        print(config)
        return

    today: tuple[int, int, int] = (now.year, now.month, now.day)

    calendar:  icalendar.Calendar = load_sources(config.sources)
    events = recurring_ical_events.of(calendar).at(today)
    events.sort(key=lambda event: event["DTSTART"].dt)
    currentCourse: Optional[Course] = None
    nextCourse: Optional[Course] = None
    for event in events:
        start = event["DTSTART"].dt
        end = event["DTEND"].dt
        summary = event["SUMMARY"]
        loc = event["LOCATION"]
        try:
            course = next(course for course in config.courses if course.eventSummary == summary)
        except StopIteration:
            print(f"{summary} not found")
            continue
        course.start = start
        course.end = end
        course.location = loc
        if start < now and end > now:
            currentCourse = course
        elif start >= now:
            nextCourse = course
            break

    if currentCourse is not None:
        if nextCourse is None:
            print(f"{currentCourse.shortName} ends in {formatdd(now,currentCourse.end)}!")
        else:
            breakTimeInMinutes = (nextCourse.start - currentCourse.end).total_seconds() / 60
            if breakTimeInMinutes > 15:
                print(f"{currentCourse.shortName} ends in {formatdd(now,currentCourse.end)}. " +
                      f"Next: {nextCourse.name} in {nextCourse.location}" +
                      f" after {formatdd(currentCourse.end, nextCourse.start)} break.")
            else:
                print("{} Ends in {} minutes. Next: {} in {} ".format(
                    currentCourse.shortName,
                      formatdd(now, currentCourse.end), nextCourse.name, currentCourse.location))
    else:
        if nextCourse is not None:
            print(f"{nextCourse.name} in {formatdd(now,nextCourse.start)}. in {nextCourse.location}")
        else:
            print("finished for the day")
