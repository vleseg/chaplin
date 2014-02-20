import unittest
import yaml
# Local imports
from chaplin import *


class TestChaplin(unittest.TestCase):
    def setUp(self):
        with open('test_schema.yaml', 'r') as f:
            source = yaml.load(f.read())
        self.questions = Questions(
            source['questions'], source["rejection_clauses"])
        self.documents = Documents(source['documents'])

        self.documents.link_answers(self.questions.get_all_aid_to_answer())
        self.questions.link_parent_answers()

    def testPathGeneration(self):
        paths = self.questions.generate_paths()
        self.assertEqual(
            [str(path) for path in paths.get_all()],
            ['TA 1', 'TA 2 -> TA 4', 'TA 2 -> TA 5 -> TA 6 -> TA 8',
             'TA 2 -> TA 5 -> TA 6 -> TA 9', 'TA 2 -> TA 5 -> TA 7 -> TA 8',
             'TA 2 -> TA 5 -> TA 7 -> TA 9', 'TA 3']
        )
        self.assertEqual(
            [repr(path) for path in paths.get_all()],
            ['0', '1 -> 3', '1 -> 4 -> 5 -> 7', '1 -> 4 -> 5 -> 8',
             '1 -> 4 -> 6 -> 7', '1 -> 4 -> 6 -> 8', '2']
        )

    def testPathFiltering(self):
        paths = self.questions.generate_paths()
        paths.trim_rejections()
        self.assertEqual(
            [str(path) for path in paths.get_all()],
            ['TA 1', 'TA 2 -> TA 4', 'TA 2 -> TA 5 -> TA 6 -> TA 8',
             'TA 2 -> TA 5 -> TA 7 -> TA 8']
        )
        self.assertEqual(
            [repr(path) for path in paths.get_all()],
            ['0', '1 -> 3', '1 -> 4 -> 5 -> 7', '1 -> 4 -> 6 -> 7']
        )

    # TODO; Write test to check generation of Cases -- anew!

if __name__ == "__main__":
    unittest.main()
