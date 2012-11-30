import pyglet
from pyglet.gl import *

class Signal:
	def __init__(self,n):self.sig=n
	@property
	def post_sig(self):return 'post-'+self.sig
	def __call__(self,func):
		def wrap(obj,*args,**kwargs):
			obj.broadcast(self.sig,*args,**kwargs)
			func(obj,*args,**kwargs)
			obj.broadcast(self.post_sig,*args,**kwargs)
		return wrap

class Eventer:
	def __init__(self):self.signals={}
	def broadcast(self,sig,*a,**k):
		for subscriber in self.signals.get(sig,[]):
			subscriber(*a,**k)
	def subscribe(self,sig,*h):
		a=self.signals.get(sig,[])
		a.extend(list(h))
		self.signals[sig] = a
	def unsubscribe(self,sig,*hs):
		a = self.signals.get(sig,[])
		if len(a)<1:return
		for handler in hs:
			if handler in a:
				a.remove(handler)
		self.signals[sig] = a

class Timer(Eventer):
	clock = pyglet.clock.Clock()
	def __init__(self,period):
		Eventer.__init__(self)
		self.clock.schedule_interval(self.elapse,period)
	@Signal("elapse")
	def elapse(self):pass

class Task(Eventer):
	def __init__(self,engine):
		self.engine = engine
		self.engine.register(self)
		Eventer.__init__(self)
	@property
	def running(self):return self in self.engine.tasks
	@running.setter
	def running(self,r):
		a = self.running
		if a and not r:self.stop()
		elif not a and r:self.start()
	@Signal("stop")
	def stop(self):self.engine.kill(self)
	@Signal("start")
	def start(self):self.engine.register(self)

class Engine(Eventer):
	frame_rate = 60
	def __init__(self,window):
		Eventer.__init__(self)
		self.window=window
		self.frame_timer = Timer(self.frame_rate)
		self.tasks = []
		self.frame_timer.subscribe("elapse",self.frame)
		window.set_handler('on_draw',self.draw)
		window.set_handler("on_resize",self.resize)
	@Signal("paint")
	def draw(self):pass
	@Signal("resize")
	def resize(self,width,height):pass
	@Signal("frame")
	def frame(self):pass
	@Signal("start-task")
	def register(self,task):
		if task not in self.tasks:
			self.tasks.append(task)
	@Signal("kill-task")
	def kill(self,task):
		if task in self.tasks:
			self.tasks.remove(task)

window = pyglet.window.Window(resizable = True)
engine = Engine(window)
pyglet.app.run()