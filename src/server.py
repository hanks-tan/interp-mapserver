
#!/usr/bin/env python
# -*- coding: utf-8 -*-
from tornado.httpserver import HTTPServer
from tornado.wsgi import WSGIContainer
from app import app
from tornado.ioloop import IOLoop
if __name__ == '__main__':
    s = HTTPServer(WSGIContainer(app))
    service = s.listen(9900)
    IOLoop.current().start()
