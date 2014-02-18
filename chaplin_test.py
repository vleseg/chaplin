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
        rejection_clauses = source['rejection_clauses']
        documents = Documents(source['documents'])

        documents.link_actual_answers(questions.answers)
        questions.link_answers()
        self.paths = questions.generate_paths()

    def runTest(self):
        self.assertEqual(repr(self.paths[0]), '0 -> 2')
        self.assertEqual(str(self.paths[1]), u'TA 1 -> TA 4 -> TA 5 -> TA 7')
        self.assertEqual(repr(self.paths[2]), '0 -> 3 -> 4 -> 7')
        self.assertEqual(str(self.paths[3]), u'TA 1 -> TO 4 -> TA 6 -> TA 7')