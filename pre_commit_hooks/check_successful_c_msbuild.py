"""Pre-commit hook to check if the last C MSBuild was successfull."""
import argparse
import datetime
import glob
import os.path
import re
from typing import Optional
from typing import Sequence


def get_file_modified_time(filename: str) -> datetime.datetime:
    """Determine the file modified time of the passed file."""
    filestat = os.stat(filename)
    mtime = datetime.datetime.fromtimestamp(filestat.st_mtime)
    return mtime


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('filenames', nargs='*', help='Filenames to check.')
    parser.add_argument(
        '--buildtype', action='append',
        help='Build types that should be checked.',
    )
    args = parser.parse_args(argv)

    buildtypes = args.buildtype or ('Release',)

    retval = 0
    for filename in args.filenames:
        fullpath = os.path.join(os.curdir, filename)
        if os.path.exists(fullpath):
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
                        print(
                            f'Unsuccessful build for {build} in {project}.',
                        )
                    retval += 1

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
                            print(
                                f'Build for {build} in {project} is '
                                'older then the file.',
                            )
                        retval += 1

    return retval


if __name__ == '__main__':    # pragma: no cover
    exit(main())
