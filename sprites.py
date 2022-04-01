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
            func=None,
            args: tuple = None
            ):
        super().__init__(*groups)
        self.text = FONT.render(text, False, text_col)
        self.surf = Surface(self.text.get_size())
        self.rect = self.surf.get_rect(center=pos)
        self.surf.fill(color)
        self.press_col = press_col
        self.func = func
        self.args = args
        self.hit_cooldown = Cooldown(10)
        self.color = color

    def activate(self):
        self.surf.fill(self.press_col)
        self.hit_cooldown.reset()
        if self.func is not None:
            self.func()

    def update(self):
        self.hit_cooldown.update()
        if not self.hit_cooldown:
            self.surf.fill(self.color)

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

