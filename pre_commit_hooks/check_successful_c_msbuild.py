"""Pre-commit hook to check if the last C MSBuild was successfull."""
import argparse
import datetime
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict
from typing import List
from typing import Optional
from typing import Sequence
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


def file_in_project(filename: Path, project_file: Path) -> bool:
    """Check if the passed file is included in the passed
    project_file."""
    included = False

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
                if project_file.parent.joinpath(include_file) == filename:
                    included = True
                    break

    return included


def is_included_in_project(filename: Path) -> bool:
    """Check if the passed file (relative to the current directory) is
    part of a project file in the same or higher directory."""
    included = False
    curdir = Path()
    searchdir = filename.parent
    searchedroot = False
    while (not searchedroot) and (not included):
        for project_file in searchdir.glob('*.vcxproj'):
            included = file_in_project(filename, project_file)

        if searchdir == curdir:
            searchedroot = True
        else:
            searchdir = searchdir.parent
    return included


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


def check_builds_for_files(files: List[Path], buildtypes: List[str]) -> int:
    """Check if for the passed files the passed buildtypes are
    successfully build."""
    dirs = build_directory_check_list(files)
    print(dirs)

    problems = set()
    for filename in files:
        if filename.exists() and is_included_in_project(filename):
            file_date = get_file_modified_time(filename)
            for build in buildtypes:
                dir = filename.parent
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

                latest_files = dir.glob(f'**/{build}/*.tlog/*.lastbuildstate')
                for latest_file in latest_files:
                    build_date = get_file_modified_time(latest_file)
                    if build_date <= file_date:
                        # The project name is the stem (without the .tlog)
                        # of the parent directory
                        project = latest_file.parent.stem
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
