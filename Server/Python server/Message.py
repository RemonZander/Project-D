import json

class Message():
    def __init__(self, type, content):
        self.type = type
        self.content = content

    def __iter__(self):
        yield from {
            "type": self.type,
            "content": self.content,
        }.items()

    def __str__(self):
        return json.dumps(dict(self), ensure_ascii=False)
        
    def __repr__(self):
        return self.__str__()

    def to_json(self):
        return self.__str__()

    @staticmethod
    def from_json(json_dict):
        return Message(json_dict['type'], json_dict['content'])

#https://levelup.gitconnected.com/how-to-deserialize-json-to-custom-class-objects-in-python-d8b92949cd3b