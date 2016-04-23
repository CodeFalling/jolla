

class HTTPError(Exception):
    error_code=None
    def __init__(self,info=None):
        self.info=info
        print self.info



class HTTP404Error(HTTPError):
    error_code=404

    def __str__(self):
        return "404 NOT FOUND"

class HTTP502Error(HTTPError):
    error_code=502

    def __str__(self):
        return "502 SERVER ERROR"