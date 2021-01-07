import os.path
import argparse
import glob
from typing import Optional
from typing import Sequence


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('filenames', nargs='*', help='XML filenames to check.')
    args = parser.parse_args(argv)

    buildtypes = ['Release']

    retval = 0
    for filename in args.filenames:
        for build in buildtypes:
            try:
                dir = os.path.dirname(filename)
                search = os.path.join(dir, '**', build, '*.tlog', 'unsuccessfulbuild')
                files = glob.glob(search, recursive = True)
                if len(files):
                    dir = os.path.join('.', dir)
                    print(f'Unsuccessfulbuild for {build} is present in: {dir}')
                    retval = 1
            except Exception as exc:
                print(f'{filename}: Exception raised: {exc}')
                retval = 1
    return retval

if __name__ == '__main__':
    exit(main())