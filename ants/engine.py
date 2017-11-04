import random
import time


class Field(object):

    def __init__(self, x=0, y=0, food=0,
                 blocked=False, home=False, antcount=0
                 ):
        self.x = x
        self.y = y
        self.food = food
        self.blocked = blocked
        self.home = home
        self.neighbours = []
        self.antcount = antcount


class Grid(object):

    def __init__(self, size_x=10, size_y=10, food_quant=1,
                 min_food=1000, max_food=5000):
        self.size_x = size_x
        self.size_y = size_y
        self.food_quant = food_quant
        self.min_food = min_food
        self.max_food = max_food

        self.fields = []
        self.create()
        self.add_food()
        self.add_home()

        self.init_neighbours()

    def create(self):
        for xi in range(self.size_x):
            for yi in range(self.size_y):
                field = Field(
                    x=xi,
                    y=yi
                )
                self.fields.append(field)

    def add_food(self):
        for _ in range(self.food_quant):
            field = random.choice(self.fields)
            field.food = random.randint(self.min_food, self.max_food)

    def add_home(self):
        # field = random.choice(self.fields)
        x = int(self.size_x / 2)
        y = int(self.size_y / 2)
        field = self.get_field_c(x, y)
        field.home = True
        self.home_field = field

    def init_neighbours(self):
        for field in self.fields:
            x = field.x
            y = field.y
            for nfield in self.get_nfields(x, y):
                field_d = {
                    'field': nfield,
                    'food_trace': 0,
                    'home_trace': 0
                }
                field.neighbours.append(field_d)

    def get_field_c(self, cx, cy):
        result = None
        for field in self.fields:
            if not field.x == cx:
                continue
            if not field.y == cy:
                continue
            result = field
        return result

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
        for field in self.fields:
            for neighbour in field.neighbours:
                if neighbour['food_trace'] > 0:
                    neighbour['food_trace'] *= 0.9
                if neighbour['home_trace'] > 0:
                    neighbour['home_trace'] *= 0.9


class Ant(object):

    def __init__(self, field=None, origin=None, home=None, engine=None,
                 grid=None, state='food', inventory_size=5):
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

        pfields = self.field.neighbours

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
            # 1 means food
            path_field = max(pfields, key=lambda field: field['food_trace'])
            if path_field['food_trace'] > 1:
                new_field = path_field['field']  # 0 means object

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
        home_field = [field for field in pfields if field['field'].home]
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
            self.engine.food_count += self.inventory
            self.engine.returns += 1
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
        for field_d in new_field.neighbours:
            # print field_d
            if field_d['field'] != self.field:
                continue
            if self.state == 'go_home' or self.state == 'return_home':
                field_d['food_trace'] += self.excitement
            if self.state == 'food' or self.state == 'take_food':
                field_d['home_trace'] += self.excitement


class AntEngine(object):

    def __init__(self, antcount=1, grid_size_x=10, grid_size_y=10,
                 food_quant=1, inf_food=True, min_food=1000,
                 max_food=5000, spawn_ants=True, ant_ai=True):

        self.ant_ai = ant_ai

        self.food_count = 0
        self.ants_count = 0
        self.grid_size = grid_size_x  # !!
        self.returns = 0

        self.spawn_ants = spawn_ants
        self.ant_count = antcount

        self.inf_food = inf_food
        self.grid = Grid(
            size_x=grid_size_x,
            size_y=grid_size_y,
            food_quant=food_quant,
            min_food=min_food,
            max_food=max_food
        )
        self.grid_home = self.grid.home_field

        self.ants = []
        for _ in range(self.ant_count):
            self.spawn_ant()

    def spawn_ant(self):
        if not self.ants_count > 15000:
            new_ant = Ant(
                home=self.grid_home,
                field=self.grid_home,
                grid=self.grid,
                engine=self
            )
            self.ants.append(new_ant)

    def tick(self):
        self.ants_count = len(self.ants)
        print('Ants:', self.ants_count)
        self.grid.decay_paths()
        for ant in self.ants:
            ant.run()
            f = ant.field
            status = 'state: {0} pos: {1} inv: {2}'.format(
                ant.state, (f.x, f.y), ant.inventory
            )

        if self.spawn_ants:
            while self.food_count > 100:
                self.spawn_ant()
                self.food_count -= 100

    def count_ants(self, antfield):
        ant_list = [
            ant for ant in self.ants if ant.field == antfield
        ]
        return len(ant_list)


if __name__ == '__main__':
    engine = AntEngine()
    while True:
        try:
            engine.tick()
            time.sleep(0.2)
        except KeyboardInterrupt:
            break
