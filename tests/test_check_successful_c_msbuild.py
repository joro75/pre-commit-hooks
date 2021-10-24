"""Unittests for successfull C MSBuild pre-commit hook"""
import time
import unittest
from pathlib import Path
from typing import Union

from pre_commit_hooks.check_successful_c_msbuild import main


class PathTestCase(unittest.TestCase):
    r"""A unittest base class that also contains helper functions
    which provide functions that are used by the actual test cases"""

    @staticmethod
    def _touch_file(filename: Union[str, Path]) -> None:
        file = Path(filename)
        file.touch(exist_ok=True)


class TestSuccessfulCMSBuild_case1(PathTestCase):
    r"""Testcase for testing the successful C MSBuild, where this
    testcase uses the file in the tests\case1\ subdirectory which
    reflects an unsuccessful build for the 'Release' buildtype"""

    _testCasePath = Path('tests/case1')

    def test_main_unsuccessfulbuild(self):
        self.assertEqual(
            1, main(argv=[str(self._testCasePath.joinpath('file1.c'))]),
        )

    def test_main_unsuccessfulbuild_multiple_files(self):
        self.assertEqual(
            1, main(
                argv=[
                    str(self._testCasePath.joinpath('file1.c')),
                    str(self._testCasePath.joinpath('file2.c')),
                    str(self._testCasePath.joinpath('file3.c')),
                    str(self._testCasePath.joinpath('file4.c')),
                ],
            ),
        )

    def test_main_non_existing_file(self):
        self.assertEqual(
            0, main(
                argv=[str(self._testCasePath.joinpath('file_not_existing.c'))],
            ),
        )

    def test_main_non_existing_buildtype(self):
        self.assertEqual(
            0, main(
                argv=[
                    str(self._testCasePath.joinpath('file1.c')),
                    '--buildtype', 'Debug',
                ],
            ),
        )

    def test_main_multiple_buildtypes(self):
        self.assertEqual(
            1, main(
                argv=[
                    str(self._testCasePath.joinpath('file1.c')),
                    '--buildtype', 'Debug',
                    '--buildtype', 'Release',
                ],
            ),
        )

    def test_main_multiple_specified_buildtypes(self):
        self.assertEqual(
            1, main(
                argv=[
                    str(self._testCasePath.joinpath('file1.c')),
                    '--buildtype', 'Debug',
                    '--buildtype', 'Release',
                ],
            ),
        )


class TestSuccessfulCMSBuild_case2(PathTestCase):
    r"""Testcase for testing the successful C MSBuild, where this
    testcase uses the file in the tests\case2\ subdirectory which
    reflects an successful build for the 'Release' and the
    'Debug' buildtype"""

    _testCasePath = Path('tests/case2')

    def test_main_unsuccessfulbuild(self):
        self.assertEqual(
            0, main(
                argv=[
                    str(self._testCasePath.joinpath('file2.c')),
                    '--buildtype', 'Debug',
                    '--buildtype', 'Release',
                ],
            ),
        )


class TestSuccessfulCMSBuild_case3(PathTestCase):
    r"""Testcase for testing the successful C MSBuild, where this
    testcase uses the file in the tests\case3\ subdirectory which
    reflects an successful build for the 'Release' and the
    'Debug' buildtype.
    However the lastbuildstate of the Release is more recent then
    the file. The lastbuildstate of the Debug is older then the file.
    """

    _testCasePath = Path('tests/case3')

    @classmethod
    def setUpClass(cls):
        cls._touch_file(
            cls._testCasePath.joinpath(
                'intermediate', 'Debug',
                'project3.tlog',
                'project3.lastbuildstate',
            ),
        )
        time.sleep(1.2)
        cls._touch_file(cls._testCasePath.joinpath('file3.c'))
        time.sleep(1.2)
        cls._touch_file(
            cls._testCasePath.joinpath(
                'intermediate',
                'Release', 'project3.tlog',
                'project3.lastbuildstate',
            ),
        )

    def test_main_file_is_newer(self):
        self.assertEqual(
            1, main(
                argv=[
                    str(self._testCasePath.joinpath('file3.c')),
                    '--buildtype', 'Debug',
                ],
            ),
        )

    def test_main_build_is_newer(self):
        self.assertEqual(
            0, main(
                argv=[
                    str(self._testCasePath.joinpath('file3.c')),
                    '--buildtype', 'Release',
                ],
            ),
        )

    def test_main_multiple_build_types(self):
        self.assertEqual(
            1, main(
                argv=[
                    str(self._testCasePath.joinpath('file3.c')),
                    '--buildtype', 'Release',
                    '--buildtype', 'Debug',
                ],
            ),
        )


class TestSuccessfulCMSBuild_case4(PathTestCase):
    r"""Testcase for testing the successful C MSBuild, where this
    testcase uses the file in the tests\case4\ subdirectory which
    reflects an unsuccessful build for two different project
    directories with the 'Release' buildtype."""

    _testCasePath = Path('tests/case4')

    @classmethod
    def setUpClass(cls):
        cls._touch_file(cls._testCasePath.joinpath('file1.c'))
        cls._touch_file(
            cls._testCasePath.joinpath(
                'intermediate1', 'im1_file1.c',
            ),
        )
        time.sleep(1.2)
        cls._touch_file(
            cls._testCasePath.joinpath(
                'intermediate1', 'Release',
                'project4a.tlog',
                'project4a.lastbuildstate',
            ),
        )
        time.sleep(1.2)
        cls._touch_file(cls._testCasePath.joinpath('file2.c'))
        cls._touch_file(
            cls._testCasePath.joinpath(
                'intermediate2', 'im2_file1.c',
            ),
        )
        time.sleep(1.2)
        cls._touch_file(
            cls._testCasePath.joinpath(
                'intermediate2',
                'Release', 'project4b.tlog',
                'project4b.lastbuildstate',
            ),
        )

    def test_main_unsuccessfulbuild(self):
        self.assertEqual(
            2, main(argv=[str(self._testCasePath.joinpath('file1.c'))]),
        )

    def test_main_unsuccessfulbuild_multiple_files(self):
        self.assertEqual(
            3, main(
                argv=[
                    str(self._testCasePath.joinpath('file1.c')),
                    str(
                        self._testCasePath.joinpath(
                            'intermediate1', 'im1_file1.c',
                        ),
                    ),
                    str(self._testCasePath.joinpath('file2.c')),
                    str(
                        self._testCasePath.joinpath(
                            'intermediate2', 'im2_file1.c',
                        ),
                    ),
                ],
            ),
        )


if __name__ == '__main__':    # pragma: no cover
    unittest.main()
