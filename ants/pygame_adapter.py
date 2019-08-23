from ants.engine import AntEngine
import pygame
import time


class FieldHandler(object):

    def __init__(self, resolution=(800, 800), grid_size=25, food_quant=100,
                 spawn_ants=True, startants=25, colony_count=1):

        self.resoltuion = resolution

        self.grid_size = grid_size

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

    def click(self, pos):
        x = int(pos[0] / self.field_size)
        y = int(pos[1] / self.field_size)
        field = self.grid.fields.get((x, y))
        if field is not None:
            field.food += 1000

    def right_click(self, pos):
        x = int(pos[0] / self.field_size)
        y = int(pos[1] / self.field_size)
        field = self.grid.fields.get((x, y))
        if field is not None:
            if not field.blocked:
                field.blocked = True
            else:
                field.blocked = False

    def draw_fields(self, display):
        # time.sleep(0.5)
        if self.run_engine:
            self.engine.tick()

        for field in self.grid.fields.values():
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

            ant_count = abs(field.antcount)
            ants_count = float(self.engine.ants_count)
            if ants_count != 0 and ant_count > 0:
                blue = int(10 * 255 * (ant_count / ants_count ** (0.7)))
            if blue > 255:
                blue = 255

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
            display.blit(field_surface, pos)
        '''
        '''
        return display
