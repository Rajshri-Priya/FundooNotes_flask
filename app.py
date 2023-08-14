from user.routes import app as user
from notes.routes import app as note

if __name__ == '__main__':
    user.run()
    note.run()