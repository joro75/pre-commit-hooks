"""Pre-commit hook to check if the last C MSBuild was successfull."""
import argparse
import datetime
import glob
import os.path
import re
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Optional
from typing import Sequence


class DetectedProblem:
    """Class that contains a single instance of a detected problem"""

    def __init__(
        self, buildtype: str, project: str,
        build: bool = True, outdated: bool = False,
    ):
        self.buildtype = buildtype
        self.project = project
        self.build = build
        self.outdated = outdated

    def __hash__(self) -> int:
        return hash((self.buildtype, self.project, self.build, self.outdated))

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, type(self)):
            return NotImplemented
        return (
            self.buildtype == other.buildtype and
            self.project == other.project and
            self.build == other.build and
            self.outdated == other.outdated
        )

    def report(self) -> None:
        """Reports the problem that is detected"""
        if not self.build:
            print(
                f'Unsuccessful build for {self.buildtype} '
                f'in {self.project}.',
            )
        if self.outdated:
            print(
                f'Build for {self.buildtype} in {self.project} '
                f'is older than the file.',
            )


def get_file_modified_time(filename: str) -> datetime.datetime:
    """Determine the file modified time of the passed file."""
    filestat = os.stat(filename)
    mtime = datetime.datetime.fromtimestamp(filestat.st_mtime)
    return mtime


def file_in_project(filename: Path, project_file: Path) -> bool:
    """Check if the passed file is included in the passed
    project_file."""
    included = False

    # Load the file
    tree = ET.parse(str(project_file))
    root = tree.getroot()
    if root:
        # Use the XPath expression to find all nodes
        # with an 'Include' attribute
        items = root.findall(
            './{http://schemas.microsoft.com/developer/msbuild/2003}'
            'ItemGroup/*[@Include]',
        )
        print(items)
        for item in items:
            print(item)
            include_file = item.attrib['Include']
            if include_file:
                print(include_file)
                if project_file.parent.joinpath(include_file) == filename:
                    included |= True

    return included


def is_included_in_project(filename: str) -> bool:
    """Check if the passed file (relative to the current directory) is
    part of a project file in the same or higher directory."""
    included = False
    curdir = Path(os.curdir)
    fullfile = curdir.joinpath(filename)
    searchdir = fullfile.parent
    searchedroot = False
    while (not searchedroot) and (not included):
        for project_file in searchdir.glob('*.vcxproj'):
            included = file_in_project(fullfile, project_file)

        if searchdir == curdir:
            searchedroot = True
        else:
            searchdir = searchdir.parent
    return included


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('filenames', nargs='*', help='Filenames to check.')
    parser.add_argument(
        '--buildtype', action='append',
        help='Build types that should be checked.',
    )
    args = parser.parse_args(argv)

    buildtypes = args.buildtype or ('Release',)

    problems = set()

    for filename in args.filenames:
        fullpath = os.path.join(os.curdir, filename)
        if os.path.exists(fullpath) and is_included_in_project(filename):
            file_date = get_file_modified_time(fullpath)
            for build in buildtypes:
                dir = os.path.dirname(fullpath)
                failed_search = os.path.join(
                    dir, '**', build, '*.tlog', 'unsuccessfulbuild',
                )
                failed_files = glob.glob(failed_search, recursive=True)
                for buildfile in failed_files:
                    m = re.match(
                        r'.*\\(.*)\.tlog\\unsuccessfulbuild', buildfile, re.I,
                    )
                    if m:
                        project = m.group(1)
                        problems.add(
                            DetectedProblem(
                                build, project, build=False,
                            ),
                        )

                latest_search = os.path.join(
                    dir, '**', build, '*.tlog', '*.lastbuildstate',
                )
                latest_files = glob.glob(latest_search, recursive=True)
                for latest_file in latest_files:
                    build_date = get_file_modified_time(latest_file)
                    if build_date <= file_date:
                        m = re.match(
                            r'.*\\(.*)\.tlog\\.*\.lastbuildstate',
                            latest_file, re.I,
                        )
                        if m:
                            project = m.group(1)
                            problems.add(
                                DetectedProblem(
                                    build, project, outdated=True,
                                ),
                            )

    retval = 0
    for problem in problems:
        problem.report()
        retval += 1

    return retval


if __name__ == '__main__':    # pragma: no cover
    exit(main())
