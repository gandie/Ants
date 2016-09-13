import random
import time
from engine import AntEngine

from kivy.clock import Clock
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.graphics import *

class Screen_Widget(Widget):

    def __init__(self, **kwargs):
        super(Screen_Widget, self).__init__(**kwargs)
        self.engine = AntEngine(antcount = 500,grid_size_x = 25,
                                grid_size_y = 25, food_quant = 1)
        self.running = False
        self.grid = self.engine.grid
        self.ants = self.engine.ants

        self.colors = {
            'red' : Color(1,0,0,1),
            'green' : Color(0,1,0,1),
            'blue' : Color(0,0,1,.1),
            'white' : Color(1,1,1,.1),
            'black' : Color(0,0,0,.1)
        }
        self.mark_fields()
        self.tick_count = 0

    def draw_rect(self, field, color):
        self.canvas.add(self.colors[color])
        with self.canvas:
            #Color(0,0,1,.1)
            #self.colors[color]
            Rectangle(pos=(field.x*17,field.y*17), size=(16,16))

    def mark_fields(self):
        for field in self.grid.fields:
            if field.food > 0:
                self.draw_rect(field, 'red')
            if field.home:
                self.draw_rect(field, 'green')

    def on_touch_down(self, touch):
        if self.running:
            self.running = False
            #self.clear_screen()
            Clock.unschedule(self.update)
            Clock.unschedule(self.clear_screen)
        else:
            self.running = True
            Clock.schedule_interval(self.update, 1/10.0)
            Clock.schedule_interval(self.clear_screen, 3)

    def clear_screen(self, dt):
        self.canvas.clear()
        self.mark_fields()

    def update(self, dt):
        self.engine.tick()
        self.tick_count += 1
        #self.draw_rect()
        #grid_fields = self.grid.fields
        #if self.tick_count % 100 == 0:
            #self.clear_screen(1)
        for ant in self.ants:
            self.draw_rect(ant.field, 'blue')


class MyScreenApp(App):

    def build(self):
        return Screen_Widget()

if __name__ == '__main__':
    MyScreenApp().run()
    
