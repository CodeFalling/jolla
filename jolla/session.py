

class buffer(object):

    def __init__(self):
        self._data = {}


class SessionError(Exception):

    def __str__(self):
        return "NO SUCH SESSION"


class session(buffer):

    def add_value(self, key, value):
        self._data[key] = value
        return True

    def check_value(self, key, value=None):
        if key in self._data.keys():
            if value:
                if self._data[key] == value:
                    return True
                else:
                    return False
            else:
                return False
        else:
            return False

    def del_value(self, key):
        if key in self._data.keys():
            del self._data[key]
            return True
        else:
            raise SessionError

    def get_value(self, key):
        if key in self._data.keys():
            return self._data[key]
        else:
            raise SessionError
