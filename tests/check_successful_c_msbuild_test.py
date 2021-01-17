"""Unittests for successfull C MSBuild pre-commit hook"""
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
            1, main(('--filenames', 'tests\\case1\\file_not_existing.c')),
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


if __name__ == '__main__':    # pragma: no cover
    unittest.main()
