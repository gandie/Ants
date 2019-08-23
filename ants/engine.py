'''
engine.py - Main engine module of ants simulation.
'''

import random
import time


class Field(object):

    def __init__(self, x=0, y=0, food=0, blocked=False, is_home=False,
                 antcount=0):
        self.x = x
        self.y = y
        self.food = food
        self.blocked = blocked
        self.is_home = is_home
        self.antcount = antcount


class Grid(object):

    def __init__(self, size_x=10, size_y=10, food_quant=1,
                 min_food=1000, max_food=5000):
        self.size_x = size_x
        self.size_y = size_y
        self.food_quant = food_quant
        self.min_food = min_food
        self.max_food = max_food

        self.fields = {}
        self.neighbours = {}

        for xi in range(self.size_x):
            for yi in range(self.size_y):
                field = Field(
                    x=xi,
                    y=yi
                )
                self.fields[(xi, yi)] = field

        for field in self.fields.values():
            x = field.x
            y = field.y
            self.neighbours[field] = {}
            for nfield in self.get_nfields(x, y):
                self.neighbours[field][nfield] = {}

        for _ in range(self.food_quant):
            field = random.choice(list(self.fields.values()))
            field.food = random.randint(self.min_food, self.max_food)

    def init_traces(self, home_key, food_key):
        '''called from antcolony to initialize traces using a prefix to
        distinguish colonies'''
        for field in self.fields.values():
            for nfield in self.get_nfields(field.x, field.y):
                self.neighbours[field][nfield][food_key] = 0
                self.neighbours[field][nfield][home_key] = 0

    def get_nfields(self, nx, ny):
        '''return iterator yielding neighbouring field instances to given
        coordinates'''
        pos_x = [nx - 1, nx, nx + 1]
        pos_y = [ny - 1, ny, ny + 1]
        pos_comb = [(x, y) for x in pos_x for y in pos_y]
        for pos in pos_comb:
            field = self.fields.get((pos[0], pos[1]))
            if not field:
                continue
            if field.x == nx and field.y == ny:
                continue
            yield field

    def decay_paths(self):
        '''called for each tick to reduce trace values in neighbours structure.
        '''
        for field in self.neighbours:
            for neighbour in self.neighbours[field]:
                for key in self.neighbours[field][neighbour]:
                    self.neighbours[field][neighbour][key] *= 0.9


class Ant(object):

    def __init__(self, colony, field=None, origin=None, home=None,
                 engine=None, grid=None, state='food', inventory_size=5):

        self.colony = colony

        self.field = field
        self.origin = origin

        self.home = home
        self.engine = engine

        self.state = state
        self.grid = grid

        self.inventory = 0
        self.inventory_size = inventory_size

        self.excitement = 100000

        self.state_map = {
            'food': self.search_food,
            'take_food': self.take_food,
            'go_home': self.go_home,
            'return_home': self.return_home
        }

    def run(self):

        pfields = []
        neighbours = self.grid.neighbours[self.field]
        for field in neighbours:
            if field == self.origin or field.blocked:
                continue
            field_d = {
                'field': field,
                'food_trace': neighbours[field][self.colony.food_key],
                'home_trace': neighbours[field][self.colony.home_key],
            }
            pfields.append(field_d)

        if self.excitement > 0:
            self.excitement *= 0.75

        if pfields:
            self.state_map[self.state](pfields)

    def move(self, new_field):
        self.put_trace(new_field)
        self.origin = self.field
        self.field = new_field

        self.field.antcount += 1
        self.origin.antcount -= 1

    def search_food(self, pfields):
        new_field = None

        # look for food in neighbouring fields
        food_fields = [
            field_d for field_d in pfields if field_d['field'].food > 0
        ]
        if food_fields:
            new_field = food_fields[0]['field']
            self.state = 'take_food'

        # look for strongest food_trace if no field has been found yet
        if self.engine.ant_ai and new_field is None:
            path_field = max(pfields, key=lambda field: field['food_trace'])
            if path_field['food_trace'] > 1:
                new_field = path_field['field']

        # pick randomly
        if not new_field or random.randint(0, 4) == 0:
            new_field = random.choice(pfields)['field']

        self.move(new_field)

    def go_home(self, pfields):
        new_field = None

        # look for home in neighbouring fields
        home_field = [
            field for field in pfields if field['field'] == self.home
        ]
        if home_field:
            new_field = home_field[0]['field']
            self.state = 'return_home'

        # look for strongest home path if home has not been found
        if self.engine.ant_ai and new_field is None:
            path_field = max(pfields, key=lambda field: field['home_trace'])
            if path_field['home_trace'] > 1:
                new_field = path_field['field']

        # pick randomly
        if not new_field or random.randint(0, 4) == 0:
            new_field = random.choice(pfields)['field']

        self.move(new_field)

    def return_home(self, pfields):
        if self.inventory > 0:
            self.colony.food_count += self.inventory
            self.inventory = 0
        else:
            self.excitement = 100000
            self.state = 'food'
            self.origin = None

    def take_food(self, pfields):
        if self.field.food > 0 and self.inventory < self.inventory_size:
            if not self.engine.inf_food:
                self.field.food -= 1
            self.inventory += 1
        else:
            self.state = 'go_home'
            self.excitement = 100000
            self.origin = None

    def put_trace(self, new_field):
        '''access neighbours dict of new_field, put trace to current field on
        it depnding on current state'''
        neighbours = self.grid.neighbours[new_field]
        if self.state == 'go_home' or self.state == 'return_home':
            neighbours[self.field][self.colony.food_key] += self.excitement
        if self.state == 'food' or self.state == 'take_food':
            neighbours[self.field][self.colony.home_key] += self.excitement


class AntColony(object):

    def __init__(self, engine, index, food_count=0, start_ants=50, ant_ai=True,
                 ant_cost=100, spawn_ants=True):

        self.index = index
        self.home_key = 'ht_%s' % index  # ht = home trace
        self.food_key = 'ft_%s' % index  # ft = food trace
        self.engine = engine
        self.food_count = food_count
        self.ant_ai = ant_ai
        self.ant_cost = ant_cost
        self.spawn_ants = spawn_ants
        self.ants = []

        self.pick_home()

        for _ in range(start_ants):
            self.spawn_ant()

        self.engine.grid.init_traces(self.home_key, self.food_key)
        print('Colony %s initialized' % self.index)

    def pick_home(self):
        self.home = None
        while self.home is None:
            # XXX: maybe do more complicated stuff here later
            home = random.choice(list(self.engine.grid.fields.values()))
            if not home.is_home:
                home.is_home = True
                self.home = home

    def spawn_ant(self):
        new_ant = Ant(
            colony=self,
            home=self.home,
            field=self.home,
            grid=self.engine.grid,
            engine=self.engine
        )
        self.ants.append(new_ant)

    def run(self):
        '''run all ants and spawn new ones'''
        for ant in self.ants:
            ant.run()

        if self.spawn_ants:
            while self.food_count > self.ant_cost:
                self.spawn_ant()
                self.food_count -= self.ant_cost

        print('Colony {index} has {ant_count} ants, food available: {food}'.format(
            index=self.index,
            ant_count=len(self.ants),
            food=self.food_count
        ))


class AntEngine(object):

    def __init__(self, colony_count=1, start_ants=50, grid_size_x=10, grid_size_y=10,
                 food_quant=25, inf_food=True, min_food=1000, ant_cost=100,
                 max_food=5000, spawn_ants=True, ant_ai=True):

        self.ant_ai = ant_ai

        self.food_count = 0
        self.ants_count = 0
        self.grid_size = grid_size_x  # !!

        self.spawn_ants = spawn_ants

        self.inf_food = inf_food
        self.grid = Grid(
            size_x=grid_size_x,
            size_y=grid_size_y,
            food_quant=food_quant,
            min_food=min_food,
            max_food=max_food
        )

        self.colonys = []
        for index in range(colony_count):
            colony = AntColony(
                index=index,
                engine=self,
                food_count=0,
                start_ants=start_ants,
                ant_ai=ant_ai,
                ant_cost=ant_cost,
                spawn_ants=spawn_ants
            )
            self.colonys.append(colony)

    def tick(self):
        self.grid.decay_paths()

        ants_count = 0
        for colony in self.colonys:
            colony.run()
            ants_count += len(colony.ants)
        self.ants_count = ants_count


if __name__ == '__main__':
    engine = AntEngine(colony_count=20)

    while True:
        try:
            engine.tick()
            time.sleep(0.2)
        except KeyboardInterrupt:
            break
