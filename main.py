"""
##########################
# Battleships  game (SF) #
#         2022           #
##########################
"""

from random import randint
from functools import lru_cache, cached_property
from utils import cls

# Exceptions


class BoardOutException(Exception):
    pass


class ShipDotsOverlap(Exception):
    pass


class DotAlreadyUsed(Exception):
    pass


# Classes


class Dot:
    """Smallest element"""
    @property
    def y(self):
        return self._y

    @y.setter
    def y(self, y):
        if y >= 0 and isinstance(y, int):
            self._y = y
        else:
            raise ValueError('y must be positive <int>')

    @property
    def x(self):
        return self._x

    @x.setter
    def x(self, x):
        if x >= 0 and isinstance(x, int):
            self._x = x
        else:
            raise ValueError('x must be positive <int>')

    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __repr__(self):
        return f'Dot <{self.x!r}, {self.y!r}>'

    def __hash__(self):
        """Simple hash. Needed to add Dot to set"""
        return hash((self.x, self.y, self.x - self.y))

    def __str__(self):
        """Human friendly string, where count begin from 1 instead of 0"""
        return f'{self.x+1}, {self.y+1}'


class Ship:
    """Group of Dots"""
    @property
    def origin(self):
        return self._origin

    @origin.setter
    def origin(self, new_origin):
        if isinstance(new_origin, Dot):
            self._origin = new_origin
        else:
            raise ValueError('Ship origin must be <Dot>')

    @property
    def size(self):
        return self._size

    @size.setter
    def size(self, new_size):
        if isinstance(new_size, int) and new_size >= 1:
            self._size = new_size
        else:
            raise ValueError('Ship size must be greater than 1')

    @property
    def orientation(self):
        return self._orientation

    @orientation.setter
    def orientation(self, new_orientation):
        if isinstance(new_orientation, int) and new_orientation in (0, 1):
            self._orientation = new_orientation
        else:
            raise ValueError('Ship orientation must be either 0 for horizontal or 1 for vertical')

    @property
    def health(self):
        return len(self.dots.difference(self.wreck))

    # It was not in the course, but Battleships is very fast-paced game where even nanoseconds is count
    # Этого не было в курсе, но Морской Бой - очень динамичная игра, где каждая наносекунда на счету
    @cached_property
    def dots(self):
        """Return set of ship Dots"""
        ship_dots = set()
        for i in range(self.size):
            if self.orientation:
                new_dot = Dot(self.origin.x, self.origin.y + i)
            else:
                new_dot = Dot(self.origin.x + i, self.origin.y)
            ship_dots.add(new_dot)
        return ship_dots

    # n a n o s e c o n d s
    @lru_cache
    def margins(self, size=1):
        """Compute margins of 'size' around ship
        Returns set of margin Dots including ship Dots"""
        if size < 1:
            raise ValueError('Ship margin size must be greater than 1')
        margin_dots = set()
        for d in self.dots:
            for c in [[d.x+i, d.y+j] for i in range(-size, size+1) for j in range(-size, size+1)]:
                try:
                    margin_dots.add(Dot(*c))
                except ValueError:
                    pass
        return margin_dots

    def __init__(self, origin=Dot(), size=1, orientation=1):
        self.origin = origin
        self.size = size
        self.orientation = orientation
        self.wreck = set()

    def __repr__(self):
        return f' {"Vertical" if self.orientation else "Horizontal"}' \
               f'Ship at {self.origin!r}, size: {self.size!r}, HP: {self.health!r}'

    def isalive(self):
        """Returns amount of intact ship Dots"""
        return self.health > 0

    def hit(self, hit):
        """Returns true if any ship Dots was hit, otherwise False"""
        if hit in self.dots:
            self.wreck.add(hit)
            return True
        else:
            return False


class Board:
    """Game board"""

    @property
    def size(self):
        return self._size

    @size.setter
    def size(self, new_size):
        if new_size < 10:
            raise ValueError('Board too small, min size 10')
        self._size = new_size

    @property
    def hidden(self):
        return self._hidden

    @hidden.setter
    def hidden(self, new_hidden=False):
        self._hidden = new_hidden

    def __init__(self, size=10, hidden=False):
        self.size = size
        self.unavailable_dots = set()  # contain all ship's dots including they margins
        self.used_dots = set()
        self.ships = []
        self.hidden = hidden

    def out(self, dot):
        """Returns True if dot is outside of board, otherwise False"""
        return not((0 <= dot.x < self.size) and (0 <= dot.y < self.size))

    def add_ship(self, ship):
        """Placing ship"""
        if self.unavailable_dots.intersection(ship.margins()):
            raise ShipDotsOverlap('Ship overlapping with another')
        elif any([self.out(d) for d in ship.dots]):
            raise BoardOutException('Ship outside board')
        else:
            self.ships.append(ship)
            self.unavailable_dots = self.unavailable_dots.union(ship.margins())

    def live_ships(self):
        """Returns number of alive ships on board"""
        return len([ship for ship in self.ships if ship.isalive()])

    def shot(self, target):
        """Return True if any ship was hit, otherwise False"""
        result = False  # Might be referenced before assignment?
        if self.out(target):
            raise BoardOutException

        if target in self.used_dots:
            raise DotAlreadyUsed

        for ship in self.ships:
            result = ship.hit(target)
        self.used_dots.add(target)
        return result

    def display(self):
        """Prints board"""
        result = ''
        d = [['_'] * self.size for _ in range(self.size)]

        for dot in self.used_dots:
            d[dot.y][dot.x] = '✸'

        for ship in self.ships:
            for dot in ship.dots:
                if not self.hidden:
                    d[dot.y][dot.x] = '☐'  # ⊡ ◻ ◼ ⨀ ⨁ ⨂ ⨉ ⨅ □ ▢ ■ ▨
                if dot in ship.wreck:
                    d[dot.y][dot.x] = '☒'  # ⊠

        d = [[f'{i+1}' for i in range(self.size)]] + d

        for n, row in enumerate(d):
            result += f'{n:^3}' + '|'.join(row) + '|\n'

        print(result)

    def __repr__(self):
        return f'Battleships Board. Size {self.size!r}, ships: {len(self.ships)}'


class User:
    """Base class for player"""
    def __init__(self, own_board: Board, opponent_board: Board):
        self.own_board = own_board
        self.opponent_board = opponent_board
        self.last_target = None

    def ask(self):
        # what are you asking exactly?
        raise NotImplementedError

    def move(self):
        """Continuously trying to make a move
        Returns True if shot was successful, otherwise False
        """
        while True:
            try:
                target: Dot = self.ask()
                shot_result = self.opponent_board.shot(target)
            except BoardOutException:
                print('Target outside board')
                continue
            except DotAlreadyUsed:
                print('Target already used')
                continue
            else:
                self.last_target = target
                return shot_result


class Human(User):
    """Human player"""
    def ask(self):
        while True:
            # X is horizontal axis, Y is vertical
            human_input = input('Enter X Y:').split()
            if len(human_input) != 2:
                print('Please enter two numbers separated by space')
                continue

            if not all([n.isdigit() for n in human_input]):
                print('Cannot parse input')
                continue

            x, y = human_input
            x, y = int(x), int(y)
            try:
                # reduce human friendly coordinates by 1
                target = Dot(x-1, y-1)
            except ValueError:
                print('Invalid coordinates')
                continue

            return target


class Ai(User):
    """Dumb AI player"""
    def ask(self):
        target = Dot(randint(0, self.own_board.size), randint(0, self.own_board.size))
        print(f'AI turn: {target.x+1} {target.y+1}')
        return target


class Game:
    """Game controller"""
    def __init__(self):
        human_board = self.random_board()
        ai_board = self.random_board(hidden=True)

        self.human = Human(own_board=human_board, opponent_board=ai_board)
        self.ai = Ai(own_board=ai_board, opponent_board=human_board)

    @staticmethod
    def _random_board(size=10, hidden=False):
        """Actually placing ships"""
        # why static? because IDE told me so
        board = Board(size=size, hidden=hidden)
        counter = 0
        # scale number of ships according to board size
        ships_template = [4]*(size // 8) + [3]*(size // 4) + [2]*(size // 3) + [1]*((size // 2) - 1)
        for t in ships_template:
            while True:
                # count ship placement attempts
                counter += 1
                # retry if placement fails after many tries
                if counter > (size+1) ** 2:
                    return None
                ship = Ship(Dot(randint(0, board.size-1), randint(0, board.size-1)), t, randint(0, 1))
                try:
                    board.add_ship(ship)
                except BoardOutException:
                    continue
                except ShipDotsOverlap:
                    continue
                else:
                    break
        return board

    @staticmethod
    def random_board(size=10, hidden=False):
        """Method to randomly place ships on board"""
        board = None
        while board is None:
            board = Game._random_board(size=size, hidden=hidden)
        return board

    def greet(self):
        print(__doc__)
        input('Press Enter to continue...')

    def show(self):
        """Clear console then display game boards"""
        cls()
        print('_' * 80)
        print(f'Human \t(Ships: {self.human.own_board.live_ships()})\tLast shot: {self.ai.last_target}')
        self.human.own_board.display()
        print(f'AI \t(Ships: {self.ai.own_board.live_ships()})\tLast shot: {self.human.last_target}')
        self.ai.own_board.display()

    def loop(self):
        """Main loop"""
        turn = 0  # considering making this randint(0, 1), for now first turn human's
        while True:

            self.show()

            if turn % 2:
                self.ai.move()
            else:
                self.human.move()
            turn += 1

            if self.human.own_board.live_ships() == 0:
                print('AI Win')
                break

            if self.ai.own_board.live_ships() == 0:
                # yay!
                print('Human Win')
                break

    def start(self):
        self.greet()
        self.loop()


if __name__ == '__main__':
    gg = Game()
    gg.start()
