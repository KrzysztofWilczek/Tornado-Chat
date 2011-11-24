import os
import time
import logging
import tornado.httpserver
import tornado.websocket
import tornado.ioloop
import tornado.web

class PageHandler(tornado.web.RequestHandler):
	def get(self, page_id):
		self.write("Subpage: " + page_id)

class BaseHandler(tornado.web.RequestHandler):
	def get_current_user(self):
		return self.get_secure_cookie("user")

class MainHandler(BaseHandler):
	def get(self):
		if not self.current_user:
			self.redirect("/login")
			return
		name = tornado.escape.xhtml_escape(self.current_user)
		self.render("chat.html", user = name)

class WSHandler(tornado.websocket.WebSocketHandler):
    waiters = set()
    
    def open(self):
		WSHandler.waiters.add(self)
		#self.write_message("Hello World")
      
    def on_message(self, message):
		message = tornado.escape.json_decode(message)
		new_message = {
			'body': message['body'],
			'author': message['author'],
			'time': time.time(),
		}
		for waiter in WSHandler.waiters:
			try:
				waiter.write_message(new_message)
			except:
				logging.error('Error sending message', exc_info=True)
       
class LogoutHandler(BaseHandler):
	def get(self):
		self.clear_all_cookies()
		self.redirect("/")

class LoginHandler(BaseHandler):
	def get(self):
		self.render("login.html")

	def post(self):
		self.set_secure_cookie("user", self.get_argument("name"))
		self.redirect("/")

settings = {
	"debug": True,
	"cookie_secret": "61oETzKXQAGaYdkL5gEmGeJJFuYh7EQnp2XdTP1o/Vo=",
	"template_path": os.path.join(os.path.dirname(__file__), 'templates'),
	"static_path": os.path.join(os.path.dirname(__file__), 'static'),
}

application = tornado.web.Application([
	(r"/", MainHandler),
	(r"/login", LoginHandler),
	(r"/logout", LogoutHandler),
	(r"/chat", WSHandler),
	(r"/page/([0-9]+)", PageHandler),
	
], **settings)

if __name__ == "__main__":
    http_server = tornado.httpserver.HTTPServer(application)
    http_server.listen(8666)
    tornado.ioloop.IOLoop.instance().start()
    