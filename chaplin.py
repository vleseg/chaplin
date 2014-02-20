from collections import OrderedDict
from itertools import chain


class Case:
    def __init__(self, path, footprint, documents):
        self.footprint = footprint
        self.paths = [path]
        self.did_to_document = OrderedDict(zip(self.footprint, documents))

    def __eq__(self, other):
        return self.footprint == other.footprint

    def get_paths_footprint(self):
        return tuple([path.footprint for path in self.paths])

    def add_path(self, path):
        self.paths.append(path)

    @staticmethod
    def get_footprint_and_documents(path):
        documents = list(chain(
            *[answer.linked_documents for answer in path.get_answers()]
        ))
        return tuple(document.did for document in documents), documents


class Cases:
    def __init__(self):
        self.paths_to_case = OrderedDict()
        self.footprint_to_case = OrderedDict()

    def handle_path(self, path):
        footprint, documents = Case.get_footprint_and_documents(path)
        if footprint not in self.footprint_to_case:
            case = Case(path, footprint, documents)
            self.footprint_to_case[footprint] = case
        else:
            case = self.footprint_to_case[footprint]
            case.add_path()
        self.paths_to_case[case.get_paths_footprint] = case


class Path:
    def __init__(self, raw_path):
        self.footprint = tuple(answer.aid for answer in raw_path)
        self.aid_to_answer = OrderedDict(zip(self.footprint, raw_path))
        self.leads_to_rejection = raw_path[-1].is_rejection_clause

    def __repr__(self):
        return ' -> '.join(map(str, self.footprint))

    def __str__(self):
        return ' -> '.join(answer.short for answer in self.get_answers())

    def get_answers(self):
        return self.aid_to_answer.values()


class Paths:
    def __init__(self):
        self.footprint_to_path = OrderedDict()

    def add_path(self, raw_path):
        path = Path(raw_path)
        self.footprint_to_path[path.footprint] = path

    def get_all(self):
        return self.footprint_to_path.values()

    def trim_rejections(self):
        for path in self.values():
            if path.leads_to_rejection:
                del self.footprint_to_path[path.footprint]

    def values(self):
        return self.footprint_to_path.values()

    def generate_cases(self):
        cases = Cases()
        for footprint in self.footprint_to_path:
            cases.handle_path(self.footprint_to_path[footprint])

        return cases


class Answer:
    def __init__(self, raw_answer, is_rejection_clause):
        self.aid = raw_answer["id"]
        self.text = raw_answer["text"]
        self.short = raw_answer["short"]
        self.is_rejection_clause = is_rejection_clause
        # Will be filled later.
        self.child_question = None
        self.linked_documents = []

    def attach_document(self, document):
        self.linked_documents.append(document)


class Answers:
    def __init__(self, raw_answers, rejections, aid_to_answer_common):
        self.aid_to_answer = OrderedDict()

        for raw_answer in raw_answers:
            aid = raw_answer["id"]
            is_rejection_clause = aid in rejections
            self[aid] = Answer(raw_answer, is_rejection_clause)
            aid_to_answer_common.update(self.aid_to_answer)

    def __setitem__(self, key, value):
        self.aid_to_answer[key] = value

    def __iter__(self):
        return self.aid_to_answer.__iter__()

    def get_all(self):
        return self.aid_to_answer.values()


class Question:
    def __init__(self, raw_question, rejections, aid_to_answer_common):
        self.qid = raw_question["id"]
        self.text = raw_question["text"]
        self.answers = Answers(
            raw_question["answers"], rejections, aid_to_answer_common)
        self.raw_parent_answers = raw_question["parent_answers"]

    def get_answers(self):
        return self.answers.get_all()


class Questions:
    def __init__(self, raw_questions, rejections):
        self.qid_to_question = OrderedDict()
        self.aid_to_answer = OrderedDict()
        self.paths = Paths()

        for raw_question in raw_questions:
            question = Question(raw_question, rejections, self.aid_to_answer)
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


class Document:
    def __init__(self, raw_document):
        self.did = raw_document["id"]
        self.text = raw_document["text"]
        self.raw_linked_answers = raw_document["linked_answers"]
        # Will be filled later.
        self.linked_answers = []


class Documents:
    def __init__(self, raw_documents):
        self.did_to_document = OrderedDict()

        for raw_document in raw_documents:
            document = Document(raw_document)
            self[document.did] = document

    def __setitem__(self, key, value):
        self.did_to_document[key] = value

    def values(self):
        return self.did_to_document.values()

    def link_answers(self, aid_to_answer):
        for document in self.values():
            for aid in document.raw_linked_answers:
                aid_to_answer[aid].attach_document(document)