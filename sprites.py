import json
import math

import pygame
from pygame import Surface
from pygame.image import load
from pygame.sprite import Sprite, Group
from helper import Cooldown
from pygame.locals import K_RETURN
import random

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

        # -Pygame Stuff-
        # Creates surface with text on it
        self.text = FONT.render(text, False, text_col)
        # Sets the surface of the actual button to the size of the text surface
        self.surf = Surface(self.text.get_size())
        self.rect = self.surf.get_rect(center=pos)
        self.surf.fill(color)
        self.press_col = press_col
        self.touch_box = self.rect.copy()
        self.start_y = self.rect.centery
        self.floating = False
        self.float_col = float_col
        self.color = color

        # -Button Stuff-
        self.func = func
        self.args = args
        # Cooldown for getting hit and flashing press_col
        self.hit_cooldown = Cooldown(10)

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
                self.func(*self.args)
            except TypeError:
                pass
            for button in self.groups()[-1]:
                button.kill()

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

        def __repr__(self):
            return str(self.__dict__)

class Message(Sprite):
    def __init__(self, text, pos, groups):
        super().__init__(*groups)
        self.seen = False
        self.surf = FONT.render(text, True, "White")
        self.rect = self.surf.get_rect(center=pos)
        self.text = text

    def update(self, pressed):
        enter = pressed[K_RETURN]
        if enter:
            self.kill()
            self.seen = True

    def __repr__(self):
        return f"{self.__class__.__name__}({self.text}, pos={self.rect.center})"


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

        # -Pygame Stuff-
        # self.surf = load(pokemon["Image"])
        self.surf = Surface((100, 100))
        self.rect = self.surf.get_rect()
        self.surf.fill((255, 255, 255))

    # Method to return the level of the pokemon
    def level(self):
        return math.floor(self.xp**(1/3))

    # Attack Method
    def use_move(self, move, opponent):
        # Code to decide whether the attack is a critical hit
        critical = 1
        type_modifier = 1
        modifier = 1
        damage = 0
        critical_calc = random.randint(0, 511)
        if critical_calc < self.speed:
            critical = 2
            print("A critical hit!")
        # Code to calculate the random modifier of the attack
        rand_modifier = random.randint(85, 100) / 100
        # Code to calculate the effectiveness of the attack

        # Super effective
        for index, effective in enumerate((move.super_effective, move.not_effective)):
            for i in effective:
                if i in opponent.type and index == 0:
                    type_modifier *= 2
                    print("Super effective...")
                elif i in opponent.type and index == 1:
                    type_modifier /= 2
                    print("Not very effective...")

        # Calculates the modifier
        modifier = critical * rand_modifier * type_modifier
        # Calculates damage (rounding to nearest integer)
        damage = round(
            ((((((2 * self.level()) / 5) + 2) * move.power * (
                        self.attack / opponent.defense)) / 50) * modifier),
            0)
        print(f"{self.name} used {move.name}!")
        print(f"Damage dealt: {int(damage)}")
        opponent.hp -= damage
        print(f"Defender hp: {int(opponent.hp)}")


# Class to read in information from the move dictionary
class Move:
    def __init__(self, move_name):
        self.name = move_name
        stats = MOVES_DICTIONARY[self.name]
        self.power = stats["power"]
        self.move_type = stats["type"]
        self.super_effective = stats["super effective against"]
        self.not_effective = stats["not very effective against"]

    def update(self):
        pass


