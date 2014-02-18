class Answer:
    def __init__(self, source):
        self.aid = source["id"]
        self.text = source["text"]
        self.short = source["short"]
        self.linked_question = None


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


class Path:
    def __init__(self, seed=None):
        if seed is None:
            seed = []
        self.path = seed

    def __iter__(self):
        return self.path.__iter__()

    def __str__(self):
        return ' -> '.join([a.short for a in self.path])

    def __repr__(self):
        return ' -> '.join([str(a.aid) for a in self.path])

    def append(self, item):
        self.path.append(item)


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

    # TODO: Rewrite recursive helper so that it correctly handles endpoint
    # answers
    def generate_paths(self):
        def recursive_helper(current_question, current_path):
            if current_question is not None:
                for a in current_question.get_answers():
                    recursive_helper(
                        a.linked_question, Path(current_path.path + [a]))

            self.paths.append(current_path)

        self.paths = []
        recursive_helper(self.questions[0], Path())

        return self.paths


class Document:
    def __init__(self, source):
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
