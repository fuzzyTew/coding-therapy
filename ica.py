from sklearn.decomposition import FastICA
import numpy as np
import sys

from kivy.app import App

from kivy.graphics.context_instructions import Color
from kivy.graphics.fbo import Fbo
from kivy.graphics.texture import Texture
from kivy.graphics.vertex_instructions import Line, Point, Rectangle

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.camera import Camera
from kivy.uix.image import Image
from kivy.uix.togglebutton import ToggleButton

def tex2darray(texture):
        return np.frombuffer(texture.pixels, dtype=np.uint8).reshape(texture.height, texture.width * 4)

class Graph(Image):
    def __init__(self, colors=(Color(1,0,1)), *args, **kwargs):
        if 'height' not in kwargs:
            kwargs['height'] = 32
        self.fbo = Fbo()
        with self.fbo:
            Color(1, 1, 1)
            self.fboscrollrect = Rectangle(pos=(-1,0))
            Color(0, 0, 0)
            self.fboclearrect = Rectangle()
            self.points = []
            self.colors = []
            for color in colors:
                self.colors.append(Color(*color.rgba))
                self.points.append(Point(points=(), pointsize=0.5))
        super().__init__(*args, **kwargs)
    @staticmethod
    def to2pow(x):
        return 1<<(int(x)-1).bit_length()
    def on_size(self, instance, size):
        self.fbo.size = (*(self.to2pow(v) for v in size),)
        self.fboscrollrect.size = self.fbo.size
        self.fboclearrect.pos = (self.fbo.size[0]-1,0)
        self.fboclearrect.size = (1, self.fbo.size[1])
        # this quick call to draw while the old texture is still attached stretches the old image instead of
        # preserving it at the proper scale, but at least it keeps the old data visible in some manner
        self.fbo.draw()
        self.fboscrollrect.texture = self.fbo.texture
        self.fboscrollrect.tex_coords = self.fbo.texture.tex_coords
        self.texture = self.fbo.texture
    def add(self, *values):
        for point, value in zip(self.points, values):
            point.points = (self.fbo.size[0] - 0.5,(value + 1) / 2 * self.fbo.size[1])
        self.fbo.draw()
        self.canvas.ask_update()
        
class TestApp(App):
    def build(self):
        parent = BoxLayout(orientation = 'vertical')
        self.graph = Graph(colors=[Color(1,0,0),Color(0,1,0),Color(0,0,1),Color(1,0,1),Color(0,1,1),Color(1,1,0)],height='32dp', size_hint = (1,None))
        self.index = 0
        self.cameras = {}
        #self.camera = Camera(index = 1, play = True)
        self.gobutton = ToggleButton(text = 'Go', height = '48dp', size_hint = (1, None), on_press = self.on_gobutton)
        self.switchcambutton = ToggleButton(text = 'Alternate camera', height = '48dp', size_hint = (1, None), on_press = self.on_switchcambutton)
        parent.add_widget(self.graph, index = 0)
        #parent.add_widget(self.camera)
        parent.add_widget(self.gobutton, index = 2)
        parent.add_widget(self.switchcambutton, index = 3)
        self.parent = parent
        self.on_gobutton(self.gobutton)
        return parent
    def on_gobutton(self, gobutton):
        if self.index not in self.cameras:
            self.cameras[self.index] = Camera(index = self.index, play = True)
            self.cameras[self.index]._camera.bind(on_texture = self.on_camtexture)
            self.parent.add_widget(self.cameras[self.index], index=1)
        elif not self.cameras[self.index].play:
            self.parent.add_widget(self.cameras[self.index], index=1)
            self.cameras[self.index].play = not self.cameras[self.index].play
        else:
            self.cameras[self.index].play = False
            self.parent.remove_widget(self.cameras[self.index])
    def on_switchcambutton(self, switchcambutton):
        play = False
        if self.cameras[self.index].play:
            play = True
            self.on_gobutton(self.gobutton)
        self.index = 1 - self.index
        if play:
            self.on_gobutton(self.gobutton)
    def on_camtexture(self, camera):
        center = np.array(camera.texture.size)//2
        image = tex2darray(camera.texture)
        values = []
        for x in range(2):
            for y in range(2):
                values.append(image[center[1] + y, center[0] + x] / 127.5 - 1)
        self.graph.add(*values)


app = TestApp()
app.run()
