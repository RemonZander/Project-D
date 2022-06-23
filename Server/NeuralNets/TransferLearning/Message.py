import json

class Message():
    def __init__(self, user_index: int, content, complex_case: bool, class_name: str):
        self.user_index = user_index
        self.content = content
        self.complex_case = complex_case
        self.class_name = class_name

    def __iter__(self):
        yield from {
            "user_index" : self.user_index,
            "content": self.content,
            "complex_case": self.complex_case,
            "class_name": self.class_name
        }.items()

    def __str__(self):
        return json.dumps(dict(self), ensure_ascii=False)
        
    def __repr__(self):
        return self.__str__()

    def to_json(self):
        return self.__str__()

    @staticmethod
    def from_json(json_dict):
        return Message(json_dict['user_index'], json_dict['content'], json_dict['complex_case'], json_dict['class_name'])

#https://levelup.gitconnected.com/how-to-deserialize-json-to-custom-class-objects-in-python-d8b92949cd3b