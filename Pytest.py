import logging
import tornado.escape
import tornado.ioloop
import tornado.options
import tornado.websocket
import tornado.web
import os.path
import uuid

from tornado.options import define, options

define("port", default=8888, help="run on the given port", type=int)


class Application(tornado.web.Application):
    """docstring for Applicationtornado.web.RequestHandler"""

    def __init__(self):
        handlers = [
            (r"/", MainHandler),
            (r"/websocket", ChatSocketHndler),

        ]
        settings = dict(
            cookie_secret="__TODO_GENARATE_YOUR_OWN_RANDOM_VALUE_HERE__",
            template_path=os.path.join(os.path.dirname(__file__), "templats"),
            static_path=os.path.join(os.path.dirname(__file__), "static"),
            xsrf_cookies=True,
        )
        tornado.web.Application.__init__(self, handlers, **settings)


class MainHandler(tornado.web.RequestHandler):

    def get(self):
        self.render("index.html", messages=ChatSocketHndler.cache)


class ChatSocketHndler(tornado.websocket.WebSocketHandler):

    waiters = set()
    cache = []
    cache_size = 200

    def allow_draft76(self):
        return True

    def open(self):
        print('a new client has been opened')
        ChatSocketHndler.waiters.add(self)

    def on_close(self):
        ChatSocketHndler.waiters.remove(self)

        def update_cache(cls, chat):
            cls.cache.append(chat)
            if len(cls.cache) > cls.cache_size:
                cls.cache = cls.cache[-cls.cache_size:]

        def sned_updates(cls, chat):
            logging.info("sending message to %d waiters", len(cls.waiters))
            for waiters in cls.waiters:
                try:
                    waiter.write_message(chat)
                except:
                    logging.error("error sending message", exc_info=True)

        def on_message(self, message):
            logging.info("got message %r", message)
            ChatSocketHndler.sned_updates(message)


def main():
    tornado.options.parse_command_line()
    app = Application()
    app.listen(8890)
    tornado.ioloop.IOLoop.instance().start()

if __name__ == '__main__':
    main()
