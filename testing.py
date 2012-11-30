import pyglet
from pyglet.gl import *

# Direct OpenGL commands to this window.
window = pyglet.window.Window(resizable = True)

vertices = [
	0, 0,
	window.width, 0,
	window.width, window.height]
vertices_gl = (GLfloat * len(vertices))(*vertices)
label = pyglet.text.Label('Hello, world',
                          font_name='Times New Roman',
                          font_size=36,
                          x=window.width//2, y=window.height//2,
                          anchor_x='center', anchor_y='center')

glEnableClientState(GL_VERTEX_ARRAY)
glVertexPointer(2, GL_FLOAT, 0, vertices_gl)

@window.event
def on_draw():
	glClear(GL_COLOR_BUFFER_BIT)
	glLoadIdentity()
	glDrawArrays(GL_TRIANGLES, 0, len(vertices) // 2)
	label.draw()

@window.event
def on_resize(width, height):
	vertices_gl[2:6] = width,0,width,height

pyglet.app.run()