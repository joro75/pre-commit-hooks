"""Pre-commit hook to check if the last C MSBuild was successfull."""
import argparse
import glob
import os.path
import re
from typing import Optional
from typing import Sequence


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--filenames', nargs='*', help='Filenames to check.')
    parser.add_argument(
        '--buildtype', nargs='*',
        help='Build types that should be checked.',
    )
    args = parser.parse_args(argv)

    buildtypes = args.buildtype or ['Release']

    retval = 0
    for filename in args.filenames:
        for build in buildtypes:
            dir = os.path.dirname(filename)
            search = os.path.join(
                dir, '**', build, '*.tlog', 'unsuccessfulbuild',
            )
            files = glob.glob(search, recursive=True)
            for buildfile in files:
                m = re.match(
                    r'.*\\(.*)\.tlog\\unsuccessfulbuild', buildfile, re.I,
                )
                if m:
                    project = m.group(1)
                    print(
                        f'Unsuccessful build for {build} in {project}',
                    )
                retval += 1
    return retval


if __name__ == '__main__':    # pragma: no cover
    exit(main())
