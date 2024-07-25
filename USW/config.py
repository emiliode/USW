import argparse
import datetime
from enum import Enum
from typing import Any


class Course:
    eventSummary: str
    name: str
    shortName: str
    start: datetime.datetime
    end: datetime.datetime
    location: str

    def __init__(self, eventSummary: str, name: str, shortName: str):
        self.eventSummary = eventSummary
        self.name = name
        self.shortName = shortName

    def __str__(self) -> str:
        try:
            return (f"{self.name=} {self.shortName=} {self.eventSummary=} "
                    "{self.location=} {self.start=} {self.end=}")
        except AttributeError:
            return f"{self.name=} {self.shortName=} {self.eventSummary=}"


class SourceType(Enum):
    WEB = 1
    LOCAL = 2


class Source:
    type: SourceType
    path: str

    def __init__(self, type: SourceType, path: str):
        self.type = type
        self.path = path


class Config:
    courses: list[Course]
    sources: list[Source]
    current_time: datetime.datetime

    def __init__(self, args: argparse.Namespace, loadedConfigFile: dict[str, Any]):
        self.courses = [Course(course["event-name"], course["course-name"], course["short-name"])
                        for course in loadedConfigFile["courses"]]
        self.current_time = args.current_time
        if len(args.sources) == 0:
            self.sources = [Source(SourceType[source["type"].upper()], source["path"])
                            for source in loadedConfigFile["sources"]]
        else:
            self.sources = [Source(SourceType.WEB if source.startswith(
                "http") else SourceType.LOCAL, source)for source in args.sources]

    def __str__(self) -> str:
        return f"{self.current_time=} \n {self.courses=} \n {self.sources=}"
