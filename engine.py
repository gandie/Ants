import random
import time

class Field(object):

    def __init__(self, x = 0, y = 0,
                 foodpath = 0, food = 0,
                 homepath = 0,
                 blocked = False, home = False
    ):
        self.x = x
        self.y = y
        self.foodpath = foodpath
        self.homepath = homepath
        self.food = food
        self.blocked = blocked
        self.home = home

        self.neighbours = []

class Grid(object):
    def __init__(self, size_x = 10, size_y = 10, food_quant = 1, 
                 min_food = 1000, max_food = 5000):
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
                    x = xi,
                    y = yi
                )
                self.fields.append(field)

    def add_food(self):
        for f in range(self.food_quant):
            field = random.choice(self.fields)
            field.food = random.randint(self.min_food, self.max_food)

    def add_home(self):
        field = random.choice(self.fields)
        field.home = True
        self.home_field = field

    def init_neighbours(self):
        for field in self.fields:
            x = field.x
            y = field.y
            nfields = self.get_nfields(x, y)
            field.neighbours = [
                [f, 0, 0] for f in nfields
            ]

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
        result = []
        pos_x = [nx-1,nx,nx+1]
        pos_y = [ny-1,ny,ny+1]
        pos_comb = [(x,y) for x in pos_x for y in pos_y]
        for pos in pos_comb:
            field = self.get_field_c(pos[0],pos[1])
            if not field:
                continue
            if field.x == nx and field.y == ny:
                continue
            result.append(field)
        return result

    def decay_paths(self):
        for field in self.fields:
            for neighbour in field.neighbours:
                if neighbour[1] > 0:
                    neighbour[1] *= 0.5
                if neighbour[2] > 0:
                    neighbour[2] *= 0.5


class Ant(object):
    def __init__(self, field = None, origin = None, home = None, engine = None,
                 grid = None, state = 'food', inventory_size = 5):
        self.field = field
        self.origin = origin
        self.home = home
        self.engine = engine

        self.state = state
        self.grid = grid

        self.inventory = 0
        self.inventory_size = inventory_size

        self.excitement = 10000

        self.state_map = {
            'food' : self.search_food,
            'idle' : self.do_nothing,
            'take_food' : self.take_food,
            'go_home' : self.go_home,
            'return_home' : self.return_home
        }
    
    def run(self):
        
        pfields = self.field.neighbours

        if self.excitement > 0:
            self.excitement *= 0.5

        if pfields:
            self.state_map[self.state](pfields)

    def move(self, new_field):
        self.put_trace(new_field)
        self.origin = self.field
        self.field = new_field

    def search_food(self, pfields): 
        new_field = None

        # remove blocked
        pfields = [field for field in pfields if not field[0].blocked]

        # remove origin
        if not len(pfields) == 1:
            pfields = [field for field in pfields if field[0] != self.origin]

        # lookup food path
        if self.engine.ant_ai:
            path_field = max(pfields, key = lambda field: field[1]) # 1 means food
            if path_field[1] > 10:
                new_field = path_field[0] # 0 means object

        # look for food
        food_field = [field for field in pfields if field[0].food > 0]
        if food_field:
            new_field = food_field[0][0]
            self.state = 'take_food'

        # pick randomly
        if not new_field or random.randint(0, 4) == 0:
            new_field = random.choice(pfields)[0]

        self.move(new_field)

    def go_home(self, pfields):
        new_field = None

        # remove blocked
        pfields = [field for field in pfields if not field[0].blocked]

        # remove origin
        if len(pfields) != 1:
            pfields = [field for field in pfields if field[0] != self.origin]

        # lookup home path
        if self.engine.ant_ai:
            path_field = max(pfields, key = lambda field: field[2]) # 2 means home
            if path_field[2] > 10:
                new_field = path_field[0] # 0 means object

        # look for home
        home_field = [field for field in pfields if field[0].home]
        if home_field:
            new_field = home_field[0][0]
            self.state = 'return_home'

        if not new_field or random.randint(0, 4) == 0:
            new_field = random.choice(pfields)[0]

        self.move(new_field)        

    def return_home(self, pfields):
        if self.inventory > 0:
            self.engine.food_count += self.inventory
            self.engine.returns += 1
            self.inventory = 0
        else:
            self.excitement = 10000
            self.state = 'food'
            self.origin = None

    def take_food(self, pfields):
        if self.field.food > 0 and self.inventory < self.inventory_size:
            if not self.engine.inf_food:
                self.field.food -= 1
            self.inventory += 1
        else:
            self.state = 'go_home'
            self.excitement = 10000
            self.origin = None

    def do_nothing(self, pfields):
        pass

    def put_trace(self, new_field):
        for triple in new_field.neighbours:
            #print triple
            if triple[0] != self.field:
                continue
            if self.state == 'go_home' or self.state == 'return_home':
                triple[1] += self.excitement # [1] means food trace!
            if self.state == 'food' or self.state == 'take_food':
                triple[2] += self.excitement # [2] means home trace!
            
class AntEngine(object):

    def __init__(self, antcount = 1, grid_size_x = 10, grid_size_y = 10, 
                 food_quant = 1, inf_food = True, min_food = 1000, 
                 max_food = 5000, spawn_ants = True, ant_ai = True):

        self.ant_ai = ant_ai

        self.food_count = 0
        self.ants_count = 0
        self.grid_size = grid_size_x # !!
        self.returns = 0

        self.spawn_ants = spawn_ants
        self.ant_count = antcount
        
        self.inf_food = inf_food
        self.grid = Grid(
            size_x = grid_size_x,
            size_y = grid_size_y,
            food_quant = food_quant,
            min_food = min_food,
            max_food = max_food
        )
        self.grid_home = self.grid.home_field

        self.ants = []
        for _ in range(self.ant_count):
            self.spawn_ant()

    def spawn_ant(self):
        new_ant = Ant(
            home = self.grid_home,
            field = self.grid_home,
            grid = self.grid,
            engine = self
        )
        self.ants.append(new_ant)

    def tick(self):
        self.ants_count = len(self.ants)

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
        for field in self.grid.fields:
            if not field == antfield:
                continue
            ant_list = [
                ant for ant in self.ants if ant.field == field
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
