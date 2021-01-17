"""Unittests for successfull C MSBuild pre-commit hook"""
import pathlib
import time
import unittest

from pre_commit_hooks.check_successful_c_msbuild import main


class TestSuccessfulCMSBuild_case1(unittest.TestCase):
    r"""Testcase for testing the successful C MSBuild, where this
    testcase uses the file in the tests\case1\ subdirectory which
    reflects an unsuccessful build for the 'Release' buildtype"""

    def test_main_unsuccessfulbuild(self):
        self.assertEqual(1, main(('--filenames', 'tests\\case1\\file1.c')))

    def test_main_unsuccessfulbuild_multiple_files(self):
        self.assertEqual(
            4, main((
                '--filenames', 'tests\\case1\\file1.c',
                'tests\\case1\\file2.c', 'tests\\case1\\file3.c',
                'tests\\case1\\file4.c',
            )),
        )

    def test_main_non_existing_file(self):
        self.assertEqual(
            0, main(('--filenames', 'tests\\case1\\file_not_existing.c')),
        )

    def test_main_non_existing_buildtype(self):
        self.assertEqual(
            0, main((
                '--filenames', 'tests\\case1\\file1.c',
                '--buildtype', 'Debug',
            )),
        )

    def test_main_multiple_buildtypes(self):
        self.assertEqual(
            1, main(
                (
                    '--filenames', 'tests\\case1\\file1.c',
                    '--buildtype', 'Debug', 'Release',
                ),
            ),
        )

    def test_main_multiple_specified_buildtypes(self):
        self.assertEqual(
            1, main((
                '--filenames', 'tests\\case1\\file1.c',
                '--buildtype', 'Debug', '--buildtype', 'Release',
            )),
        )


class TestSuccessfulCMSBuild_case2(unittest.TestCase):
    r"""Testcase for testing the successful C MSBuild, where this
    testcase uses the file in the tests\case2\ subdirectory which
    reflects an successful build for the 'Release' and the
    'Debug' buildtype"""

    def test_main_unsuccessfulbuild(self):
        self.assertEqual(
            0, main((
                '--filenames', 'tests\\case2\\file2.c',
                '--buildtype', 'Debug', '--buildtype', 'Release',
            )),
        )


class TestSuccessfulCMSBuild_case3(unittest.TestCase):
    r"""Testcase for testing the successful C MSBuild, where this
    testcase uses the file in the tests\case3\ subdirectory which
    reflects an successful build for the 'Release' and the
    'Debug' buildtype.
    However the lastbuildstate of the Release is more recent then
    the file. The lastbuildstate of the Debug is older then the file.
    """

    @staticmethod
    def _touch_file(filename: str) -> None:
        file = pathlib.Path(filename)
        file.touch(exist_ok=True)

    @classmethod
    def setUpClass(cls):
        cls._touch_file(
            'tests\\case3\\intermediate\\Debug\\project3.tlog\\'
            'project3.lastbuildstate',
        )
        time.sleep(1.2)
        cls._touch_file('tests\\case3\\file3.c')
        time.sleep(1.2)
        cls._touch_file(
            'tests\\case3\\intermediate\\Release\\project3.tlog\\'
            'project3.lastbuildstate',
        )

    def test_main_file_is_newer(self):
        self.assertEqual(
            1, main((
                '--filenames', 'tests\\case3\\file3.c',
                '--buildtype', 'Debug',
            )),
        )

    def test_main_build_is_newer(self):
        self.assertEqual(
            0, main((
                '--filenames', 'tests\\case3\\file3.c',
                '--buildtype', 'Release',
            )),
        )

    def test_main_multiple_build_types(self):
        self.assertEqual(
            1, main((
                '--filenames', 'tests\\case3\\file3.c',
                '--buildtype', 'Release', '--buildtype', 'Debug',
            )),
        )


if __name__ == '__main__':    # pragma: no cover
    unittest.main()
