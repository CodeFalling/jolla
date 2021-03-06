import gevent.monkey
gevent.monkey.patch_all()

from gevent.pywsgi import WSGIServer
import re
from HTTPerror import HTTP404Error, HTTP403Error
from plugins import render_media


class RouteError(Exception):

    def __init__(self, info):
        if(info == 'too many re'):
            print "TOO MORE REGULAR SEARCH"
        if(info == 'route error'):
            print 'WRONG ROUTE DESIGN'
        if(info == 'query already in request'):
            print "IT HAS ALREADY IN REQUEST VALUE"


class WebApp():

    urls = []

    _parsed_urls = []

    setting = {
        'statics': r'/statics',
        'templates': r'/templates'
    }

    def __init__(self, environ):

        self._environ = environ

        self._path = self._environ['PATH_INFO']
        if self._path[-1]!='/':
            self._path=self._path+'/'

        self.request = {}

        try:
            self.request['cookies'] = self._environ['HTTP_COOKIE']
        except KeyError:
            self.request['cookies'] = None

        self.request['http_protocol'] = self._environ['SERVER_PROTOCOL']

        self.request['user_agent'] = self._environ['HTTP_USER_AGENT']

        self.request['http_connect'] = self._environ['HTTP_CONNECTION']

        self.request['http_port'] = self._environ['HTTP_HOST']

        self.request['method'] = self._environ['REQUEST_METHOD']

        try:
            self.request['content_length'] = self._environ['CONTENT_LENGTH']
            self.request['content_type'] = self._environ['CONTENT_TYPE']
        except KeyError:
            self.request['content_length']=None
            self.request['content_type']=None



        self.request['http_accept_encoding'] = self._environ[
            'HTTP_ACCEPT_ENCODING']

        self.request['data'] = {}
        line = self._environ['QUERY_STRING']
        request_data = environ['wsgi.input'].read()
        if request_data:
            for data_pair in request_data.split('&'):
                key, value = data_pair.split('=')
                self.request['data'][key] = value
        query_string = self._environ['QUERY_STRING']
        if query_string:
            for data_pair in query_string.split('&'):
                key, value = data_pair.split('=')
                self.request['data'][key] = value


        for url in self.urls:
            res=self.url_parse(url[0])
            if isinstance(res,tuple):
                self._parsed_urls.append((res[0],url[1],res[1]))
            else:
                self._parsed_urls.append((res,url[1]))


    def parse(self):
        for url_handler in self._parsed_urls:
            if url_handler[0] == r'/':
                if self._path != '/':
                    continue
                else:
                    html_code = url_handler[1](self.request)

            if self.setting['statics'] in self._path:
                path = self._path.replace(
                    self.setting['statics'], '')

                try:
                    res = render_media(path)
                except IOError:
                    raise HTTP404Error("NOT FOUND THIS FILE")
                return res

            url_reg=re.compile(url_handler[0])
            if url_reg.match(self._path):
                re_query=re.findall(url_reg,self._path)
                if re_query[0]:
                    self.request[url_handler[2]]=re_query[0]
                    html_code=url_handler[1](self.request)
                else:
                    html_code=url_handler[1](self.request)

                return html_code

        raise HTTP404Error('REQUEST NOT FOUND IN ROUTE CONFIGURATION')

    def url_parse(self, path):
        path = path.replace(' ', '')
        if path[-1] != '/':
            path = path + '/'
        if '<' in path and '>' in path:
            if path.count("<") != path.count(">"):
                raise RouteError("route error")
            if path.count("<") > 1:
                raise RouteError("too many re")

            reg = re.compile(r'<(\w+)>')
            url_query = re.findall(reg, path)[0]
            if url_query in self.request:
                raise RouteError("query already in request")
            else:
                self.request[url_query] = None
            the_url = path.replace('<' + url_query + '>',
                                   r'(?P<' + url_query + '>\w*)')
            return (the_url,url_query)
        return path


class jolla_server(WSGIServer):

    def __init__(self, app, port=8000, host="127.0.0.1", debug=False):
        self.port = port
        self.host = host
        self.app = app
        WSGIServer.__init__(self, listener=(
            self.host, self.port), application=self.application)

    def application(self, environ, start_response):

        the_app = self.app(environ)

        try:
            html_code = the_app.parse()
            status = '200 OK'
        except HTTP404Error:
            status = '404 NOT FOUND'
            html_code = '404 NOT FOUND'

        header = [
            ('Content-Type', 'text/html'),
            ('Server', 'Jolla/1.0')
        ]

        start_response(status, header)

        return html_code

    def run_server(self):
        print "the server is running on the {} in the port {}".format(self.host, self.port)

        self.serve_forever()
