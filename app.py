#-*-coding: utf-8-*-
import os
import json
from tornado import escape
import tornado.ioloop
import config
from tornado import web
from tornado import gen
from tornado import httpclient
from tornado.web import asynchronous
from tornado.options import parse_command_line, options, define


define("port", default=8000)


class TornadoDataRequest(httpclient.HTTPRequest):
    def __init__(self, url, **kwargs):
        super(TornadoDataRequest, self).__init__(url, **kwargs)
        self.method = "GET"
        self.auth_username = config.username
        self.auth_password = config.password
        self.user_agent = "Tornado-data"


class HelloHandler(web.RequestHandler):
    def get(self):
        self.write("Hello world!")


class LoveHandler(web.RequestHandler):
    def get(self):
        self.write("Love world!")


class GithubPageHandler(web.RequestHandler):
    @asynchronous
    @gen.coroutine
    def get(self):
        client = httpclient.AsyncHTTPClient()
        request = TornadoDataRequest("https://github.com/cloudaice")
        resp = yield client.fetch(request)
        #resp = resp.encode("utf-8")
        self.write(resp.body)
        self.finish()


class GithubHandler(web.RequestHandler):
    @asynchronous
    @gen.coroutine
    def get(self):
        client = httpclient.AsyncHTTPClient()
        request = TornadoDataRequest("https://api.github.com/gists/4524946")
        resp = yield client.fetch(request)
        resp = escape.json_decode(resp.body)
        users_url = resp["files"]["github-users-stats.json"]["raw_url"]
        languages_url = resp["files"]["github-languages-stats.json"]["raw_url"]
        users, languages = yield [client.fetch(TornadoDataRequest(users_url)),
                                  client.fetch(TornadoDataRequest(languages_url))]
        users_stats = escape.json_decode(users.body)
        languages_stats = escape.json_decode(languages.body)
        print len(users_stats)
        print len(languages_stats)
        if isinstance(resp, dict):
            self.set_header('Content-Type', 'application/json; charset=UTF-8')
            self.write(json.dumps(users_stats, indent=4, separators=(',', ': ')))
            self.write(json.dumps(languages_stats, indent=4, separators=(',', ': ')))
        else:
            self.write("hello world")
        self.finish()


settings = {
    "static_path": os.path.join(os.path.dirname(__file__), 'static'),
    "debug": True
}

app = web.Application([
    (r"/", HelloHandler),
    (r"/love", LoveHandler),
    (r"/github", GithubHandler),
    (r"/githubpage", GithubPageHandler),
    (r"/favicon.ico", web.StaticFileHandler, dict(path=settings["static_path"])),
], **settings)


if __name__ == "__main__":
    parse_command_line()
    app.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()
