import unittest
import yaml
# Local imports
from chaplin import *


class TestChaplin(unittest.TestCase):
    def setUp(self):
        with open('test_schema.yaml', 'r') as f:
            source = yaml.load(f.read())
        questions = Questions(source['questions'], source["rejection_clauses"])
        self.documents = Documents(source['documents'])

        self.documents.link_answers(questions.get_all_aid_to_answer())
        questions.link_parent_answers()
        self.paths = questions.generate_paths()

    def testGeneratedPaths(self):
        self.assertEqual(
            [str(path) for path in self.paths.get_all()],
            ['TA 1', 'TA 2 -> TA 4', 'TA 2 -> TA 5 -> TA 6 -> TA 8',
             'TA 2 -> TA 5 -> TA 6 -> TA 9', 'TA 2 -> TA 5 -> TA 7 -> TA 8',
             'TA 2 -> TA 5 -> TA 7 -> TA 9', 'TA 3']
        )
        self.assertEqual(
            [repr(path) for path in self.paths.get_all()],
            ['0', '1 -> 3', '1 -> 4 -> 5 -> 7', '1 -> 4 -> 5 -> 8',
             '1 -> 4 -> 6 -> 7', '1 -> 4 -> 6 -> 8', '2']
        )

    def testPathFiltering(self):
        self.paths.trim_rejections()
        self.assertEqual(
            [str(path) for path in self.paths.get_all()],
            ['TA 1', 'TA 2 -> TA 4', 'TA 2 -> TA 5 -> TA 6 -> TA 8',
             'TA 2 -> TA 5 -> TA 7 -> TA 8']
        )
        self.assertEqual(
            [repr(path) for path in self.paths.get_all()],
            ['0', '1 -> 3', '1 -> 4 -> 5 -> 7', '1 -> 4 -> 6 -> 7']
        )

    # TODO; Figure out, why tests fail.
    def testCases(self):
        self.paths.trim_rejections()
        cases = self.paths.generate_cases()
        self.assertEqual(
            [str(case) for case in cases.get_all()],
            ['((0,), (1, 4, 5, 7)): Test document 1, Test document 3, '
             'Test document 4',
             '((1, 3),): Test document 1, Test document 2',
             '((1, 4, 6, 7),): Test document 1, Test document 3, '
             'Test document 5']
        )
        self.assertEqual(
            [repr(case) for case in cases.get_all()],
            ['((0,), (1, 4, 5, 7)): 0, 3, 4', '((1, 3),): 0, 1',
             '((1, 4, 6, 7),): 0, 2, 4']
        )


if __name__ == "__main__":
    unittest.main()
