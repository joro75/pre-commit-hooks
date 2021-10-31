"""Pre-commit hook to check if the last C MSBuild was successfull."""
import argparse
import datetime
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict
from typing import List
from typing import Optional
from typing import Sequence
from typing import Set
from typing import Tuple


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


def get_file_modified_time(filename: Path) -> datetime.datetime:
    """Determine the file modified time of the passed file."""
    return datetime.datetime.fromtimestamp(filename.stat().st_mtime)


def get_included_files_from_project(project_file: Path) -> List[Path]:
    """Gets a list of all the files that are included by the passed
    projectfile."""

    files = []

    # Load the file
    tree = ET.parse(str(project_file))
    root = tree.getroot()
    if root:
        namespace = 'http://schemas.microsoft.com/developer/msbuild/2003'

        # Use the XPath expression to find all nodes
        # with an 'Include' attribute
        items = root.findall(
            f'./{{{namespace}}}ItemGroup/'
            '*[@Include]',
        )
        for item in items:
            include_file = item.attrib['Include']
            if include_file:
                files.append(project_file.parent.joinpath(include_file))
    return files


def build_directory_check_list(files: List[Path]) -> Dict[
        Path, List[Tuple[Path, datetime.datetime]],
]:
    """Builds the list of directories that should be checked based on
    the passed list of files."""
    dirs: Dict[Path, List[Tuple[Path, datetime.datetime]]] = {}
    for file in files:
        if file.exists():
            file_date = get_file_modified_time(file)
            for checkdir in file.parents:
                # Retrieve the directory from the dictionary
                # Which is a list of file/change-date pairs
                dir_data = dirs.get(checkdir, [])
                dir_data.append((file, file_date))
                dirs[checkdir] = dir_data
    return dirs


def build_project_check_list(
    dirs: Dict[
        Path, List[
            Tuple[
                Path,
                datetime.datetime,
            ]
        ],
    ],
) -> Dict[
        Path, datetime.datetime,
]:
    """Builds the list of the MS VS project files that should be checked
    based ont he passed list of files."""
    projects: Dict[Path, datetime.datetime] = {}
    for dir in dirs:
        if dirs[dir]:
            for project_file in dir.glob('*.vcxproj'):
                included_files = get_included_files_from_project(project_file)
                if included_files:
                    for filename, change_date in dirs[dir]:
                        if filename in included_files:
                            date_check = projects.get(
                                project_file,
                                datetime.datetime
                                (1900, 1, 1),
                            )
                            if change_date > date_check:
                                projects[project_file] = change_date
    return projects


def check_if_projects_build(
    projects: Dict[Path, datetime.datetime],
    buildtypes: List[str],
) -> Set[DetectedProblem]:
    """Checks for the passed list of projects and build types if
    the output is build."""

    problems: Set[DetectedProblem] = set()
    for project_file in projects:
        file_change_date = projects[project_file]
        for build in buildtypes:
            dir = project_file.parent
            failed_files = dir.glob(f'**/{build}/*.tlog/unsuccessfulbuild')
            for buildfile in failed_files:
                # The project name is the stem (without the .tlog)
                # of the parent directory
                project = buildfile.parent.stem
                problems.add(
                    DetectedProblem(
                        build, project, build=False,
                    ),
                )

            # found_build = False
            latest_files = dir.glob(f'**/{build}/*.tlog/*.lastbuildstate')
            for latest_file in latest_files:
                # found_build = True
                build_date = get_file_modified_time(latest_file)
                if build_date <= file_change_date:
                    # The project name is the stem (without the .tlog)
                    # of the parent directory
                    project = latest_file.parent.stem
                    problems.add(
                        DetectedProblem(
                            build, project, outdated=True,
                        ),
                    )
            # if not found_build:
            #    problems.add(DetectedProblem(
            #                    build, project_file.stem, build=False
            #                 ),
            #    )
    return problems


def check_builds_for_files(files: List[Path], buildtypes: List[str]) -> int:
    """Check if for the passed files the passed buildtypes are
    successfully build."""
    dirs = build_directory_check_list(files)
    projects = build_project_check_list(dirs)
    problems = check_if_projects_build(projects, buildtypes)

    retval = 0
    for problem in problems:
        problem.report()
        retval += 1

    return retval


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('filenames', nargs='*', help='Filenames to check.')
    parser.add_argument(
        '--buildtype', action='append',
        help='Build types that should be checked.',
    )
    args = parser.parse_args(argv)

    buildtypes = list(args.buildtype or ('Release',))
    files = []
    curdir = Path()
    for filename in args.filenames:
        files.append(curdir.joinpath(filename))

    problem_count = check_builds_for_files(
        files,
        buildtypes,
    )
    return problem_count


if __name__ == '__main__':    # pragma: no cover
    exit(main())
