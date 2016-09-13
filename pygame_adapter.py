from engine import AntEngine
import pygame
import time

class FieldHandler(object):

    def __init__(self, resolution = (800,800)):

        self.resoltuion = resolution

        self.grid_size = 25

        self.field_size = resolution[0] / self.grid_size

        self.engine = AntEngine(
            antcount = 50,
            grid_size_x = self.grid_size,
            grid_size_y = self.grid_size,
            food_quant = 10,
            inf_food = False,
            min_food = 10000,
            max_food = 50000,
            spawn_ants = True,
            ant_ai = True
        )

        self.grid = self.engine.grid
        self.ants = self.engine.ants

        self.run_engine = False

    def click(self, pos):
        x = pos[0] / self.field_size
        y = pos[1] / self.field_size
        for field in self.grid.fields:
            if not field.x == x:
                continue
            if not field.y == y:
                continue
            field.food += 10000

    def right_click(self, pos):
        x = pos[0] / self.field_size
        y = pos[1] / self.field_size
        for field in self.grid.fields:
            if not field.x == x:
                continue
            if not field.y == y:
                continue
            if not field.blocked:
                field.blocked = True
            else:
                field.blocked = False

    def draw_fields(self, display):
        #time.sleep(0.5)
        if self.run_engine:
            self.engine.tick()
        for field in self.grid.fields:
            red = 0
            green = 0
            blue = 0

            field_surface = pygame.Surface(
                (self.field_size, self.field_size)
            )

            if field.home:
                green = 255

            if field.food > 0:
                red = 255
                #print(field.food)
                #food_ant_count = self.engine.count_ants(field)
                #print(food_ant_count)

            ant_count = self.engine.count_ants(field)
            ants_count = float(self.engine.ants_count)
            if ants_count != 0:
                blue = int(10 * 255 * (ant_count / ants_count))
            if blue > 255:
                blue = 255

            if field.blocked:
                red = 255
                blue = 255
                green = 255

            pygame.draw.rect(
                field_surface,
                (red, green, blue),
                (0, 0, self.field_size, self.field_size)
            )
            field_surface = field_surface.convert()

            pos = (
                field.x * self.field_size,
                field.y * self.field_size
            )
            display.blit(field_surface, pos)

        return display
