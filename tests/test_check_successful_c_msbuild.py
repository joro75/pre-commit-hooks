"""Unittests for successfull C MSBuild pre-commit hook"""
import time
import unittest
from pathlib import Path
from typing import Union

from pre_commit_hooks.check_successful_c_msbuild import DetectedProblem
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


class TestSuccessfulCMSBuild_case5(PathTestCase):
    r"""Testcase for testing the successful C MSBuild, where this
    testcase uses the file in the tests\case5\ subdirectory which
    reflects an successful build for the 'Release'.
    However the project file is only present in the intermediate
    directory and thus the top level file is assumed not to be
    present in the project and thus unrelevant.
    """

    _testCasePath = Path('tests/case5')

    def test_main_file_is_not_present_in_project(self):
        self.assertEqual(
            0, main(
                argv=[
                    str(self._testCasePath.joinpath('file5.c')),
                ],
            ),
        )

    def test_main_yaml_file_not_present_in_project(self):
        self.assertEqual(
            0, main(
                argv=[
                    str(self._testCasePath.joinpath('.some-config.yaml')),
                ],
            ),
        )

    def test_main_file_is_present_in_project(self):
        self.assertEqual(
            1, main(
                argv=[
                    str(
                        self._testCasePath.joinpath(
                            'intermediate',
                            'im_file5.c',
                        ),
                    ),
                ],
            ),
        )

    def test_main_multiple_files(self):
        self.assertEqual(
            1, main(
                argv=[
                    str(self._testCasePath.joinpath('file5.c')),
                    str(self._testCasePath.joinpath('.some-config.yaml')),
                    str(
                        self._testCasePath.joinpath(
                            'intermediate',
                            'im_file5.c',
                        ),
                    ),
                ],
            ),
        )


class TestDetectedProblem(unittest.TestCase):
    """Tests the DetectedProblem class"""

    def test_eq_to_other_type(self):
        compare = DetectedProblem('a', 'b', True) == 'other_data'
        self.assertEqual(False, compare)

    def test_eq_same(self):
        dp1 = DetectedProblem('a', 'b', outdated=False, build=True)
        dp2 = DetectedProblem('a', 'b', True, False)

        self.assertEqual(True, dp1 == dp2)

    def test_eq_different(self):
        dp = DetectedProblem('a', 'b', build=True, outdated=False)
        dp_diff1 = DetectedProblem('A', 'b', True, False)
        dp_diff2 = DetectedProblem('a', 'B', True, False)
        dp_diff3 = DetectedProblem('a', 'b', False, False)
        dp_diff4 = DetectedProblem('a', 'b', True, True)

        self.assertEqual(
            False, dp == dp_diff1,
            'Buildtype is not correctly compared.',
        )
        self.assertEqual(
            False, dp == dp_diff2,
            'Project is not correctly compared.',
        )
        self.assertEqual(
            False, dp == dp_diff3,
            'Build is not correctly compared.',
        )
        self.assertEqual(
            False, dp == dp_diff4,
            'Outdated is not correctly compared.',
        )

    def test_in_set(self):
        data = set()
        data.add(DetectedProblem('a', 'b', True))
        data.add(DetectedProblem('c', 'd', True))

        self.assertEqual(2, len(data))


if __name__ == '__main__':    # pragma: no cover
    unittest.main()
