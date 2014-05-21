# coding=utf-8
import unittest
import yaml
# Local imports
from chaplin import *


class TestChaplin(unittest.TestCase):
    def setUp(self):
        with open('test_schema.yaml', 'r') as f:
            source = yaml.load(f.read())
        questions = Questions(source['questions'])
        self.results = Results(source['documents'], source['rejections'])

        self.results.link_answers(questions.get_all_aid_to_answer())
        questions.link_parent_answers()
        self.paths = questions.generate_paths()

    def testGeneratedPaths(self):
        self.assertEqual(
            [str(path) for path in self.paths.get_all()],
            ['TA 0', 'TA 1 -> TA 3', 'TA 1 -> TA 4 -> TA 5 -> TA 7',
             'TA 1 -> TA 4 -> TA 5 -> TA 8', 'TA 1 -> TA 4 -> TA 6 -> TA 7',
             'TA 1 -> TA 4 -> TA 6 -> TA 8', 'TA 2']
        )
        self.assertEqual(
            [repr(path) for path in self.paths.get_all()],
            ['0', '1 -> 3', '1 -> 4 -> 5 -> 7', '1 -> 4 -> 5 -> 8',
             '1 -> 4 -> 6 -> 7', '1 -> 4 -> 6 -> 8', '2']
        )

    def testPathFiltering(self):
        self.paths.exclude_rejections()
        self.assertEqual(
            [str(path) for path in self.paths.get_all()],
            ['TA 0', 'TA 1 -> TA 3', 'TA 1 -> TA 4 -> TA 5 -> TA 7',
             'TA 1 -> TA 4 -> TA 6 -> TA 7']
        )
        self.assertEqual(
            [repr(path) for path in self.paths.get_all()],
            ['0', '1 -> 3', '1 -> 4 -> 5 -> 7', '1 -> 4 -> 6 -> 7']
        )

    def testCasesWithTrimmedRejections(self):
        cases = self.paths.generate_cases(mode="trim")
        sorted_cases = sorted(
            cases.get_all(), key=lambda case: case.get_multipath_footprint())
        self.assertEqual(
            [str(case) for case in sorted_cases],
            ['((0,), (1, 4, 5, 7)): Test document 0, Test document 2, '
             'Test document 3',
             '((1, 3),): Test document 0, Test document 1',
             '((1, 4, 6, 7),): Test document 0, Test document 2, '
             'Test document 4']
        )
        self.assertEqual(
            [repr(case) for case in sorted_cases],
            ['((0,), (1, 4, 5, 7)): 0, 2, 3', '((1, 3),): 0, 1',
             '((1, 4, 6, 7),): 0, 2, 4']
        )

    def testCasesWithRejectionsIntact(self):
        cases = self.paths.generate_cases(mode="collapse")
        sorted_cases = sorted(
            cases.get_all(), key=lambda case: case.get_multipath_footprint())
        self.assertEqual(
            [str(case) for case in sorted_cases],
            ['((0,), (1, 4, 5, 7)): Test document 0, Test document 2, '
             'Test document 3',
             '((1, 3),): Test document 0, Test document 1',
             '((1, 4, 6, 7),): Test document 0, Test document 2, '
             'Test document 4',
             '((2,),): Test rejection 0',
             '((8,),): Test rejection 1']
        )
        self.assertEqual(
            [repr(case) for case in sorted_cases],
            ['((0,), (1, 4, 5, 7)): 0, 2, 3', '((1, 3),): 0, 1',
             '((1, 4, 6, 7),): 0, 2, 4', '((2,),): 0r', '((8,),): 1r']
        )


if __name__ == "__main__":
    unittest.main()
