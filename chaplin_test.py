import unittest
import yaml
# Local imports
from chaplin import *


class TestChaplin(unittest.TestCase):
    def setUp(self):
        with open('test_schema.yaml', 'r') as f:
            source = yaml.load(f.read())
        self.questions = Questions(source['questions'])
        self.rejection_clauses = source['rejection_clauses']
        self.documents = Documents(source['documents'])

        self.documents.link_actual_answers(self.questions.answers)
        self.questions.link_answers()

    def testPathGeneration(self):
        paths = self.questions.generate_paths()
        self.assertEqual(repr(paths[0]), '0 -> 2')
        self.assertEqual(str(paths[1]), 'TA 1 -> TA 4 -> TA 5 -> TA 7')
        self.assertEqual(repr(paths[2]), '0 -> 3 -> 4 -> 7')
        self.assertEqual(str(paths[3]), 'TA 1 -> TA 4 -> TA 6 -> TA 7')
        self.assertEqual(repr(paths[4]), '0 -> 3 -> 5 -> 7')
        self.assertEqual(str(paths[5]), 'TA 2')

    def testPathFiltering(self):
        paths = self.questions.generate_paths()
        paths.filter_out_rejections(self.rejection_clauses)
        self.assertEqual(str(paths[0]), 'TA 1 -> TA 3')
        self.assertEqual(str(paths[1]), 'TA 1 -> TA 4 -> TA 5 -> TA 7')
        self.assertEqual(str(paths[2]), 'TA 1 -> TA 4 -> TA 6 -> TA 7')

    def testDocuments(self):
        paths = self.questions.generate_paths()
        paths.filter_out_rejections(self.rejection_clauses)
        paths.generate_cases()
        test_str = lambda i: str(paths[i].case)
        test_repr = lambda i: repr(paths[i].case)
        self.assertEqual(test_str(0), 'Test document 1 -> Test document 2')
        self.assertEqual(test_repr(1), '0 -> 2 -> 3')
        self.assertEqual(test_str(2),
            'Test document 1 -> Test document 3 -> Test document 5')


if __name__ == "__main__":
    unittest.main()
