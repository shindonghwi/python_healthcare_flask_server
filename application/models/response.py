import json


class ApiResponse(object):
    __status: int
    __msg: str = None
    __data: dict = None

    def __init__(self, status, msg, data = None):
        self.__status = status
        self.__msg = msg
        self.__data = data

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)
