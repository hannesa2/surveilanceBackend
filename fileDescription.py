from json import JSONEncoder

class FileDescription:

    def __init__(self, name, webcam, size, created):
        self.name = name
        self.webcam = webcam
        self.size = size
        self.created = created

    def __lt__(self, other):
        return self.size < other.size

class FileDescriptionEncoder(JSONEncoder):
        def default(self, o):
            return o.__dict__
