# coding=utf-8
import yaml
# Local imports
from chaplin import *

if __name__ == '__main__':
    with open('test_schema.yaml', 'r') as f:
        source = yaml.load(f.read())
    questions = Questions(source['questions'])
    rejection_clauses = source['rejection_clauses']
    documents = Documents(source['documents'])

    documents.link_actual_answers(questions.answers)
    questions.link_answers()
    paths = questions.generate_paths()



# Two following snippets are to be used with Notepad++ PythonScript.
# Uncomment the preferred one.

# To use with Notepad++ PythonScript.
# try:
#     text = editor.getText().decode('utf-8').strip()
#     editor.clearAll()
#     backup = text
#     text = main(text)
# except BaseException as e:
#     print 'SOMETHING BAD HAPPENED: {}'.format(e)
#     editor.addText(backup.encode('utf-8'))
#     raise e
# else:
#     editor.addText(text.encode('utf-8'))

# To use with Notepad++ PythonScript (without additional error handling.
# text = editor.getText().decode('utf-8').strip()
# editor.clearAll()
# text = main(text)
# editor.addText(text.encode('utf-8'))