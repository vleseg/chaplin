# coding=utf-8
from collections import OrderedDict
from itertools import chain


DOCUMENT = 0
REJECTION = 1


class ChaplinException(BaseException):
    pass


class Case(object):
    def __init__(self, path, footprint, results):
        self.footprint = footprint
        if path.is_rejection_path:
            self.is_rejection_case = True
            self.rid_to_rejection = {self.footprint, results}
        self.paths = [path]
        self.did_to_document = OrderedDict(zip(self.footprint, results))
        # Will be filled later.
        self.is_rejection_case = False

    def __eq__(self, other):
        return self.footprint == other.footprint

    def __str__(self):
        return str(self.get_multipath_footprint()) + ': ' + ', '.join([
            document.text for document in self.get_all_documents()])

    def __repr__(self):
        return str(self.get_multipath_footprint()) + ': ' + ', '.join(
            map(str, self.footprint))

    def get_multipath_footprint(self):
        return tuple(path.footprint for path in self.paths)

    def add_path(self, path):
        self.paths.append(path)

    def get_all_documents(self):
        return self.did_to_document.values()

    @staticmethod
    def get_footprint_and_results(path):
        results = list(chain(
            *[answer.linked_results for answer in path.get_answers()]
        ))
        return tuple(sorted(result.rid for result in results)), results


class Cases(object):
    def __init__(self):
        self.paths_to_case = {}
        self.footprint_to_case = OrderedDict()

    def __str__(self):
        sorted_cases = sorted(
            self.get_all(), key=lambda case: case.get_multipath_footprint())
        return '\n'.join(unicode(case) for case in sorted_cases)

    def handle_path(self, path):
        footprint, results = Case.get_footprint_and_results(path)
        if footprint not in self.footprint_to_case:
            case = Case(path, footprint, results)
            self.footprint_to_case[footprint] = case
        else:
            case = self.footprint_to_case[footprint]
            del self.paths_to_case[case.get_multipath_footprint()]
            case.add_path(path)
        self.paths_to_case[case.get_multipath_footprint()] = case

    def get_all(self):
        return self.paths_to_case.values()


# FIXME: reimplement collapse routine
class Path(object):
    def __init__(self, raw_path, collapse_rejection):
        # if collapse_rejection:
        #     only_answer = raw_path.last_answer
        #     self.footprint = only_answer.aid
        #     self.aid_to_answer = {only_answer.aid: only_answer}
        #     self.is_rejection_path = True
        # else:
        self.footprint = tuple(answer.aid for answer in raw_path)
        self.aid_to_answer = OrderedDict(zip(self.footprint, raw_path))
        self.last_answer = raw_path[-1]
        self.is_rejection_path = False

    def __repr__(self):
        return ' -> '.join(map(str, self.footprint))

    def __str__(self):
        return ' -> '.join(answer.short for answer in self.get_answers())

    def get_answers(self):
        return self.aid_to_answer.values()


class Paths(object):
    def __init__(self):
        self.footprint_to_path = OrderedDict()

    def add_path(self, raw_path, collapse_rejection=False):
        path = Path(raw_path, collapse_rejection)
        self.footprint_to_path[path.footprint] = path

    def collapse_rejections(self):
        last_answers_pool = []
        for path in self.values():
            if path.last_answer.is_rejection_clause:
                if path.last_answer not in last_answers_pool:
                    last_answers_pool.append(path.last_answer)
                    self.add_path(path, collapse_rejection=True)
                del self.footprint_to_path[path.footprint]

    def get_all(self):
        return self.footprint_to_path.values()

    def trim_rejections(self):
        for path in self.values():
            if path.last_answer.is_rejection_clause:
                del self.footprint_to_path[path.footprint]

    def values(self):
        return self.footprint_to_path.values()

    # 'mode' resembles how rejections should be treated.
    def generate_cases(self, mode):
        if mode == "trim":
            self.trim_rejections()
        elif mode == "collapse":
            self.collapse_rejections()
        else:
            raise ChaplinException(
                "Unknown case generation mode: {}".format(mode))

        cases = Cases()
        for footprint in self.footprint_to_path:
            cases.handle_path(self.footprint_to_path[footprint])

        return cases


class Answer(object):
    def __init__(self, raw_answer):
        self.aid = raw_answer["id"]
        self.text = raw_answer["text"]
        self.short = raw_answer["short"]
        # Will be filled later.
        self.child_question = None
        self.linked_results = []
        self.is_rejection_clause = False

    def attach_result(self, result):
        self.linked_results.append(result)
        self.is_rejection_clause = result.type == REJECTION


class Answers(object):
    def __init__(self, raw_answers, aid_to_answer_common):
        self.aid_to_answer = OrderedDict()

        for raw_answer in raw_answers:
            aid = raw_answer["id"]
            self[aid] = Answer(raw_answer)
            aid_to_answer_common.update(self.aid_to_answer)

    def __setitem__(self, key, value):
        self.aid_to_answer[key] = value

    def __iter__(self):
        return self.aid_to_answer.__iter__()

    def get_all(self):
        return self.aid_to_answer.values()


class Question(object):
    def __init__(self, raw_question, aid_to_answer_common):
        self.qid = raw_question["id"]
        self.text = raw_question["text"]
        self.answers = Answers(
            raw_question["answers"], aid_to_answer_common)
        self.raw_parent_answers = raw_question["parent_answers"]

    def get_answers(self):
        return self.answers.get_all()


class Questions(object):
    def __init__(self, raw_questions):
        self.qid_to_question = OrderedDict()
        self.aid_to_answer = OrderedDict()
        self.paths = Paths()

        for raw_question in raw_questions:
            question = Question(raw_question, self.aid_to_answer)
            self[question.qid] = question

    def __setitem__(self, key, value):
        self.qid_to_question[key] = value

    def __getitem__(self, item):
        return self.qid_to_question[item]

    def get_all_aid_to_answer(self):
        return self.aid_to_answer

    def link_parent_answers(self):
        for question in self.values():
            if question.raw_parent_answers is not None:
                for aid in question.raw_parent_answers:
                    self.aid_to_answer[aid].child_question = question

    def values(self):
        return self.qid_to_question.values()

    def generate_paths(self):
        def recursive_helper(current_question, current_path):
            for answer in current_question.get_answers():
                if answer.child_question is None:
                    self.paths.add_path(current_path + [answer])
                else:
                    recursive_helper(
                        answer.child_question, current_path + [answer])

        recursive_helper(self[0], [])

        return self.paths


class Result(object):
    def __init__(self, raw_result, type):
        self.type = type
        self.rid = str(raw_result["id"])
        if type == REJECTION:
            self.rid += 'r'
        self.text = raw_result["text"]
        self.raw_linked_answers = raw_result["linked_answers"]
        # Will be filled later.
        self.linked_answers = []


class Results(object):
    def __init__(self, raw_documents, raw_rejections):
        self.rid_to_result = OrderedDict()

        for raw_document in raw_documents:
            document = Result(raw_document, type=DOCUMENT)
            self.rid_to_result[document.rid] = document

        for raw_rejection in raw_rejections:
            rejection = Result(raw_rejection, type=REJECTION)
            self.rid_to_result[rejection.rid] = rejection

    def get_all(self):
        return self.rid_to_result.values()

    def link_answers(self, aid_to_answer):
        for result in self.get_all():
            for aid in result.raw_linked_answers:
                aid_to_answer[aid].attach_result(result)