import os
import time
import logging
import tornado.httpserver
import tornado.websocket
import tornado.ioloop
import tornado.web

# Other handler for some other pages display
class PageHandler(tornado.web.RequestHandler):
	def get(self, page_id):
		self.write("Subpage: " + page_id)

# Defines method for get user cookie
class BaseHandler(tornado.web.RequestHandler):
	def get_current_user(self):
		return self.get_secure_cookie("user")

# Main handler check is user logged in
class MainHandler(BaseHandler):
	def get(self):
		if not self.current_user:
			self.redirect("/login")
			return
		name = tornado.escape.xhtml_escape(self.current_user)
		self.render("chat.html", user = name)

# WebSockets handler add user to listeners set and push messages 
class WSHandler(tornado.websocket.WebSocketHandler):
    listeners = set()
    
    def open(self):
		self.listeners.add(self)
		
    def on_close(self):
		self.listeners.remove(self)
		
    def on_message(self, message):
		message = tornado.escape.json_decode(message)
		new_message = {
			'body': message['body'],
			'author': message['author'],
			'time': time.time(),
		}
		for waiter in self.listeners:
			try:
				waiter.write_message(new_message)
			except:
				logging.error('Error sending message', exc_info=True)


# User logut action
class LogoutHandler(BaseHandler):
	def get(self):
		self.clear_all_cookies()
		self.redirect("/")

# User login action via post data
class LoginHandler(BaseHandler):
	def get(self):
		self.render("login.html")

	def post(self):
		self.set_secure_cookie("user", self.get_argument("name"))
		self.redirect("/")

# Application settings
settings = {
	"debug": True,
	"cookie_secret": "61oETzKXQAGaYdkL5gEmGeJJFuYh7EQnp2XdTP1o/Vo=",
	"template_path": os.path.join(os.path.dirname(__file__), 'templates'),
	"static_path": os.path.join(os.path.dirname(__file__), 'static'),
}

# Application routing
application = tornado.web.Application([
	(r"/", MainHandler),
	(r"/login", LoginHandler),
	(r"/logout", LogoutHandler),
	(r"/chat", WSHandler),
	(r"/page/([0-9]+)", PageHandler),
	
], **settings)

# Application initialization on 8666 socket
if __name__ == "__main__":
    http_server = tornado.httpserver.HTTPServer(application)
    http_server.listen(8666)
    tornado.ioloop.IOLoop.instance().start()
    