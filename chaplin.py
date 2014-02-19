class Answer:
    def __init__(self, source):
        self.aid = source["id"]
        self.text = source["text"]
        self.short = source["short"]
        self.linked_question = None
        self.linked_documents = []

    def attach_document(self, document):
        self.linked_documents.append(document)


class Question:
    def __init__(self, source):
        self.aid_to_answer_mapping = {}
        self.text = source["text"]
        self.raw_linked_answers = source["linked_answers"]
        self.linked_answers = None

        for raw_a in source["answers"]:
            self.aid_to_answer_mapping[raw_a["id"]] = Answer(raw_a)
    
    def get_answers_dict(self):
        return self.aid_to_answer_mapping

    def get_answers(self):
        return self.aid_to_answer_mapping.values()


class Case:
    def __init__(self, raw_case):
        self.case = raw_case

    def __repr__(self):
        return ''.join([str(d.did) for d in self.case])

    def __str__(self):
        return ''.join(d.text for d in self.case)


class Path:
    def __init__(self, seed):
        self.path = seed
        self.case = []

    def __getitem__(self, item):
        return self.path[item]

    def __str__(self):
        return ' -> '.join([a.short for a in self.path])

    def __repr__(self):
        return ' -> '.join([str(a.aid) for a in self.path])

    def append(self, item):
        self.path.append(item)

    def generate_case(self):
        reduction_lambda = lambda x, y: x + y.linked_documents
        raw_case = reduce(reduction_lambda, self.path, [])
        self.case = Case(raw_case)


# TODO: implement unification of paths of identical cases at output time
class Paths:
    def __init__(self):
        self.paths = []

    def __getitem__(self, item):
        return self.paths[item]

    def append(self, item):
        self.paths.append(item)

    # Rejection clauses have to be a list of ints (aid).
    def filter_out_rejections(self, rejection_clauses):
        filter_func = lambda path: path[-1].aid not in rejection_clauses
        self.paths = filter(filter_func, self.paths)

    def generate_cases(self):
        for p in self.paths:
            p.generate_case()


class Questions:
    def __init__(self, source):
        self.questions = []
        self.answers = {}
        self.paths = None

        for raw_q in source:
            self.questions.append(Question(raw_q))
        for q in self.questions:
            self.answers.update(q.get_answers_dict())
        
    def __iter__(self):
        return self.questions.__iter__()
        
    def __getitem__(self, i):
        return self.questions[i]

    def link_answers(self):
        # First question already has a None Answer linked to it.
        q_list = self.questions[1:]
        for q in q_list:
            q.linked_answers = [
                self.answers[aid] for aid in q.raw_linked_answers]
            for a in q.linked_answers:
                a.linked_question = q

    def generate_paths(self):
        def recursive_helper(current_question, current_path):
            for a in current_question.get_answers():
                if a.linked_question is None:
                    self.paths.append(Path(current_path + [a]))
                else:
                    recursive_helper(a.linked_question, current_path + [a])

        self.paths = Paths()
        recursive_helper(self.questions[0], [])

        return self.paths


class Document:
    def __init__(self, source):
        self.did = source["id"]
        self.text = source["text"]
        self.raw_linked_answer = source["linked_answer"]
        self.linked_answer = None
        
    def get_linked_answer(self):
        return self.linked_answer
    
        
class Documents:
    def __init__(self, source):
        self.documents = []
        
        for raw_d in source:
            self.documents.append(Document(raw_d))
        
    def __iter__(self):
        return self.documents.__iter__()
        
    def __getitem__(self, i):
        return self.documents[i]
        
    def link_actual_answers(self, answers):
        for d in self.documents:
            d.linked_answer = answers[d.raw_linked_answer]
            d.linked_answer.attach_document(d)
