from user.routes import app as user
from notes.routes import app as note
from label.routes import app as label

if __name__ == '__main__':
    user.run()
    note.run()
    label.run()