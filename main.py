import yaml
from itertools import chain

class Answer:
    def __init__(self, source):
        self.aid = source["id"]
        self.text = source["text"]
        self.short = source["short"]
        

class Question:
    def __init__(self, source):
        self.aid_to_answer_mapping = {}
        self.text = source["text"]
        
        for raw_a in source["answers"]:
            self.aid_to_answer_mapping[raw_a["id"]] = Answer(raw_a)
    
    def get_answers(self):
        return self.aid_to_answer_mapping
        
class Questions:
    def __init__(self, source):
        self.qid_to_question_mapping = {}
        self.answers = {}
        
        for i, raw_q in enumerate(source):
            self.qid_to_question_mapping[i] = Question(raw_q)
        q_dict = self.qid_to_question_mapping
        for qid in q_dict:
            self.answers.update(q_dict[qid].get_answers())
        
    def __iter__(self):
        return self.qid_to_question_mapping.__iter__()
        
    def __getitem__(self, i):
        return self.qid_to_question_mapping[i]
    
        
class Document:
    def __init__(self, source):
        self.text = source["text"]
        self.raw_linked_answer = source["linked_answer"]
        
    def get_linked_answer(self):
        return self.linked_answer
    
        
class Ducuments:
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
        
        
def main(text):
    source = yaml.load(text)
    questions = Questions(source["questions"])
    rejection_clauses = source["rejection_clauses"]
    documents = Ducuments(source["documents"])
    
    documents.link_actual_answers(questions.answers)
    
    return documents[1].get_linked_answer().text

# To use with notepad++ PythonScript
# try:
    # text = editor.getText().decode('utf-8').strip()
    # editor.clearAll()
    # backup = text
    # text = main(text)
# except BaseException as e:
    # print 'SOMETHING BAD HAPPENED: {}'.format(e)
    # editor.addText(backup.encode('utf-8'))
    # raise e
# else:
    # editor.addText(text.encode('utf-8'))
    
# To use with notepad++ PythonScript (without additional try...except wrapping)
# text = editor.getText().decode('utf-8').strip()
# editor.clearAll()
# text = main(text)
# editor.addText(text.encode('utf-8'))
