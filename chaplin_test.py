# coding=utf-8
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
        documents = Documents(source['documents'])

        documents.link_actual_answers(self.questions.answers)
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