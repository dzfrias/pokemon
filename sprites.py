import json
import pygame
from pygame import Surface
from pygame.image import load
from pygame.sprite import Sprite, Group
from helper import Cooldown

pygame.font.init()

# -Constants-
with open("characters.json") as f:
    POKEMON = json.load(f)

# Reads in the dictionaries from the json files
with open("moves.json") as json_file:
    MOVES_DICTIONARY = json.load(json_file)

FONT = pygame.font.SysFont("Comic Sans MS", 30)


class Button(Sprite):
    def __init__(
            self,
            text: str,
            *,
            pos: tuple,
            color: tuple,
            groups: tuple,
            press_col: tuple,
            text_col: tuple,
            float_col: tuple,
            func=None,
            args: tuple = None
            ):
        super().__init__(*groups)
        # Creates surface with text on it
        self.text = FONT.render(text, False, text_col)
        # Sets the surface of the actual button to the size of the text surface
        self.surf = Surface(self.text.get_size())
        self.rect = self.surf.get_rect(center=pos)
        self.surf.fill(color)
        self.press_col = press_col
        self.func = func
        self.args = args
        # Cooldown for getting hit and flashing press_col
        self.hit_cooldown = Cooldown(10)
        self.color = color
        self.touch_box = self.rect.copy()
        self.start_y = self.rect.centery
        self.floating = False
        self.float_col = float_col

    def handle_float(self, collide):
        if collide and not self.floating:
            self.rect.centery -= 20
            self.floating = True
            self.surf.fill(self.float_col)
        elif not collide:
            self.rect.centery = self.start_y
            self.floating = False

    def activate(self):
        if not self.hit_cooldown:
            self.surf.fill(self.press_col)
            # Starts the cooldown
            self.hit_cooldown.reset()
            try:
                # Calls the associated function if it is set
                self.func()
            except TypeError:
                pass

    def update(self):
        self.hit_cooldown.update()
        # Checks if cooldown is not active
        if not self.hit_cooldown and not self.floating:
            self.surf.fill(self.color)
        elif not self.hit_cooldown and self.floating:
            self.surf.fill(self.float_col)

    def get_text_pos(self):
        size_x, size_y = self.text.get_size()
        center = list(self.rect.center)
        center[0] -= size_x / 2
        center[1] -= size_y / 2
        return center


# Class to read in information from the move dictionary
class Move:
    def __init__(self, move_name):
        self.name = move_name
        stats = MOVES_DICTIONARY[self.name]
        self.power = stats["power"]
        self.type = stats["type"]
        self.super_effective = stats["super effective against"]
        self.not_effective = stats["not very effective against"]

    def __repr__(self):
        return str(self.__dict__)


class Pokemon(Sprite):
    def __init__(self, name: str, groups: tuple[Group]):
        super().__init__(*groups)

        # -Pokemon Stuff-
        pokemon = POKEMON[name]
        self.name = name
        self.type = pokemon["Type"]
        self.hp = pokemon["HP"]
        # Creates a Move instance for each name in the pokemon["Moves"] entry
        self.moves = [Move(move_name) for move_name in pokemon["Moves"]]
        self.attack = pokemon["Attack"]
        self.defense = pokemon["Defense"]
        self.speed = pokemon["Speed"]
        self.xp = pokemon["Experience"]
        self.level = 1

        # -Pygame Stuff-
        # self.surf = load(pokemon["Image"])
        self.surf = Surface((100, 100))
        self.rect = self.surf.get_rect()
        self.surf.fill((255, 255, 255))

    def update(self):
        pass

    def __repr__(self):
        return f"{self.__class__.__name__}({self.name}, {self.hp})"

