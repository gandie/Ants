import random
import time
import pprint


class Field(object):

    def __init__(self, x=0, y=0, food=0,
                 blocked=False, is_home=False, antcount=0
                 ):
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
        self.create()
        self.add_food()
        # self.add_home()

        # self.init_neighbours()

        self.neighbours = {}
        for field in self.fields.values():
            x = field.x
            y = field.y
            self.neighbours[field] = {}
            for nfield in self.get_nfields(x, y):
                self.neighbours[field][nfield] = {}

    def create(self):
        for xi in range(self.size_x):
            for yi in range(self.size_y):
                field = Field(
                    x=xi,
                    y=yi
                )
                self.fields[(xi, yi)] = field

    def add_food(self):
        for _ in range(self.food_quant):
            field = random.choice(list(self.fields.values()))
            field.food = random.randint(self.min_food, self.max_food)

    def add_home(self):
        assert False, 'Deprecated!'
        # field = random.choice(self.fields)
        x = int(self.size_x / 2)
        y = int(self.size_y / 2)
        field = self.get_field_c(x, y)
        field.home = True
        self.home_field = field

    def init_traces(self, prefix):
        food_key = '%s_food_trace' % prefix
        home_key = '%s_home_trace' % prefix
        for field in self.fields.values():
            x = field.x
            y = field.y
            # self.neighbours[field] = {}
            for nfield in self.get_nfields(x, y):
                self.neighbours[field][nfield][food_key] = 0
                self.neighbours[field][nfield][home_key] = 0

    def get_field_c(self, cx, cy):
        return self.fields.get((cx, cy))

    def get_nfields(self, nx, ny):
        pos_x = [nx - 1, nx, nx + 1]
        pos_y = [ny - 1, ny, ny + 1]
        pos_comb = [(x, y) for x in pos_x for y in pos_y]
        for pos in pos_comb:
            field = self.get_field_c(pos[0], pos[1])
            if not field:
                continue
            if field.x == nx and field.y == ny:
                continue
            yield field

    def decay_paths(self):
        for field in self.neighbours:
            for neighbour in self.neighbours[field]:
                '''
                self.neighbours[field][neighbour]['food_trace'] *= 0.9
                self.neighbours[field][neighbour]['home_trace'] *= 0.9
                '''
                for key in self.neighbours[field][neighbour]:
                    self.neighbours[field][neighbour][key] *= 0.9


class Ant(object):

    def __init__(self, colony, prefix, field=None, origin=None, home=None, engine=None,
                 grid=None, state='food', inventory_size=5):

        self.colony = colony
        self.prefix = prefix
        self.food_key = '%s_food_trace' % self.prefix
        self.home_key = '%s_home_trace' % self.prefix

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
            'idle': self.do_nothing,
            'take_food': self.take_food,
            'go_home': self.go_home,
            'return_home': self.return_home
        }

    def run(self):

        pfields = []
        neighbours = self.grid.neighbours[self.field]
        for field in neighbours:
            field_d = {
                'field': field,
                'food_trace': neighbours[field][self.food_key],
                'home_trace': neighbours[field][self.home_key],
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

        # remove blocked
        pfields = [field_d for field_d in pfields if not field_d['field'].blocked]

        # remove origin
        if len(pfields) != 1:
            pfields = [field_d for field_d in pfields if field_d['field'] != self.origin]

        # look for food
        food_fields = [field_d for field_d in pfields if field_d['field'].food > 0]
        if len(food_fields) >= 1:
            new_field = food_fields[0]['field']
            self.state = 'take_food'

        # lookup food path
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

        # remove blocked
        pfields = [field_d for field_d in pfields if not field_d['field'].blocked]

        # remove origin
        if len(pfields) != 1:
            pfields = [field_d for field_d in pfields if field_d['field'] != self.origin]

        # look for home
        home_field = [field for field in pfields if field['field'] == self.home]
        if home_field:
            new_field = home_field[0]['field']
            self.state = 'return_home'

        # lookup home path
        if self.engine.ant_ai and new_field is None:
            path_field = max(pfields, key=lambda field: field['home_trace'])
            if path_field['home_trace'] > 1:
                new_field = path_field['field']

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

    def do_nothing(self, pfields):
        pass

    def put_trace(self, new_field):
        neighbours = self.grid.neighbours[new_field]
        for field in neighbours:
            if field != self.field:
                continue
            if self.state == 'go_home' or self.state == 'return_home':
                neighbours[field][self.food_key] += self.excitement
            if self.state == 'food' or self.state == 'take_food':
                neighbours[field][self.home_key] += self.excitement


class AntColony(object):

    def __init__(self, engine, index, food_count=0, start_ants=50, ant_ai=True,
                 ant_cost=100, spawn_ants=True):

        self.prefix = 'AntColony%s' % index
        self.engine = engine
        self.food_count = food_count
        self.ant_ai = ant_ai
        self.ant_cost = ant_cost
        self.spawn_ants = spawn_ants
        self.ants = []

        self.pick_home()

        for _ in range(start_ants):
            self.spawn_ant()

        self.engine.grid.init_traces(self.prefix)
        print('Colony {} initialized'.format(self.prefix))

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
            prefix=self.prefix,
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

        print('Colony {prefix} has {ant_count} ants, food available: {food}'.format(
            prefix=self.prefix,
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

        '''
        pprint.pprint(self.grid.neighbours)
        assert False, '...and then die'
        self.grid_home = self.grid.home_field
        self.ants = []
        for _ in range(self.ant_count):
            self.spawn_ant()
        '''

    def spawn_ant(self):
        assert False, 'Deprecated'
        if not self.ants_count > 15000:
            new_ant = Ant(
                home=self.grid_home,
                field=self.grid_home,
                grid=self.grid,
                engine=self
            )
            self.ants.append(new_ant)

    def tick(self):
        # self.ants_count = len(self.ants)
        # print('Ants:', self.ants_count)
        self.grid.decay_paths()

        ants_count = 0
        for colony in self.colonys:
            colony.run()
            ants_count += len(colony.ants)
        self.ants_count = ants_count
        '''
        for ant in self.ants:
            ant.run()
            f = ant.field

        if self.spawn_ants:
            while self.food_count > 100:
                self.spawn_ant()
                self.food_count -= 100
        '''


    def count_ants(self, antfield):
        assert False, 'whos calling you?'
        ant_list = [
            ant for ant in self.ants if ant.field == antfield
        ]
        return len(ant_list)


if __name__ == '__main__':
    engine = AntEngine(colony_count=20)
    # engine = AntEngine()

    while True:
        try:
            engine.tick()
            time.sleep(0.2)
        except KeyboardInterrupt:
            break
