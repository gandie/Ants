from ants.engine import AntEngine
import pygame
import time


class FieldHandler(object):

    def __init__(self, resolution=(800, 800), grid_size=25, food_quant=100,
                 spawn_ants=True, startants=25, colony_count=1):

        self.grid_size = grid_size

        # assuming square grid!!
        self.field_size = resolution[0] / self.grid_size

        self.engine = AntEngine(
            start_ants=startants,
            grid_size_x=self.grid_size,
            grid_size_y=self.grid_size,
            food_quant=food_quant,
            inf_food=False,
            min_food=5000,
            max_food=5000,
            spawn_ants=spawn_ants,
            ant_ai=True,
            colony_count=colony_count
        )

        self.grid = self.engine.grid

        self.run_engine = False

    def get_field(self, pos):
        '''calculate coordinates from click pos and return corresponding field
        from engine grid'''
        x = int(pos[0] / self.field_size)
        y = int(pos[1] / self.field_size)
        return self.grid.fields.get((x, y))

    def click(self, pos):
        '''add food to clicked field'''
        field = self.get_field(pos)
        if field is not None:
            field.food += 1000

    def right_click(self, pos):
        '''toggle clicked field blocked attribute'''
        field = self.get_field(pos)
        if field is not None:
            field.blocked = not field.blocked

    def colour_field(self, field):
        '''calculate colour of field from ant count, food and blocked attribute
        '''

        red = 0
        green = 0
        blue = 0

        field_surface = pygame.Surface(
            (self.field_size, self.field_size)
        )

        if field.is_home:
            green = 255

        if field.food > 0:
            red = 255

        if field.antcount < 0:
            field.antcount = 0

        ant_count = field.antcount
        ants_count = float(self.engine.ants_count)
        if ants_count != 0 and ant_count > 0:
            blue = int(10 * 255 * (ant_count / ants_count ** (0.7)))
        if blue > 255:
            blue = 255

        # blocked fields are white!
        if field.blocked:
            red = 255
            blue = 255
            green = 255

        pygame.draw.rect(
            field_surface,
            (red, green, blue, 0),
            (0, 0, self.field_size, self.field_size)
        )
        field_surface = field_surface.convert_alpha()

        pos = (
            field.x * self.field_size,
            field.y * self.field_size
        )

        return field_surface, pos

    def draw_fields(self, display):
        '''called from pygame_main, run engine and put coloured fields on
        display'''

        if self.run_engine:
            self.engine.tick()

        for field in self.grid.fields.values():
            field_surface, pos = self.colour_field(field)
            display.blit(field_surface, pos)

        return display
