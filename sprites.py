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
SMALL_FONT = pygame.font.SysFont("Comic Sans MS", 25)


class Button(Sprite):
    def __init__(
            self,
            text: str,
            *,
            pos: tuple,
            color: tuple,
            groups: tuple,
            text_col: tuple,
            float_col: tuple | str,
            alpha: int = 255,
            func=None,
            args: tuple = None,
            image: str = "",
            image_size: tuple = ()
            ):
        super().__init__(*groups)

        # -Pygame Stuff-
        # Creates surface with text on it
        self.text = FONT.render(text, False, text_col)
        if image:
            self.surf = pygame.image.load(image).convert_alpha()
            self.img = image
            self.surf = pygame.transform.scale(self.surf, image_size)
        else:
            self.surf = Surface(self.text.get_size())
            self.surf.fill(color)
            self.img = ""
        self.surf.set_alpha(alpha)
        # Sets the surface of the actual button to the size of the text surface
        self.rect = self.surf.get_rect(center=pos)
        self.touch_box = self.rect.copy()
        self.start_y = self.rect.centery
        self.floating = False
        self.float_col = float_col
        self.color = color
        self.alpha = alpha

        # -Button Stuff-
        self.func = func
        self.args = args
        # Cooldown for getting hit and flashing press_col
        self.hit_cooldown = Cooldown(10)

    def handle_float(self, collide):
        color = self.float_col
        if collide and not self.floating:
            self.rect.centery -= 20
            self.floating = True
            if not self.img:
                self.surf.fill(self.float_col)
        elif not collide:
            self.rect.centery = self.start_y
            self.floating = False
            color = self.color
        screen = pygame.display.get_surface()
        if not self.img:
            new_rect = self.rect.inflate(20, 20)
            pygame.draw.rect(screen, color, new_rect, border_radius=10)
            pygame.draw.rect(screen, "Black", new_rect, 5, border_radius=10)

    def collide(self, point):
        return self.rect.collidepoint(point) or self.touch_box.collidepoint(point)

    def activate(self):
        if not self.hit_cooldown:
            # Starts the cooldown
            self.hit_cooldown.reset()
            try:
                # Calls the associated function if it is set
                result = self.func(*self.args)
            except TypeError:
                result = None
            for button in self.groups()[-1]:
                button.kill()
            return result

    def update(self):
        self.hit_cooldown.update()
        # Checks if cooldown is not active
        if not self.hit_cooldown and not self.floating:
            self.surf.set_alpha(self.alpha)
        elif not self.hit_cooldown and self.floating:
            self.surf.set_alpha(255)

    def get_text_pos(self):
        size_x, size_y = self.text.get_size()
        center = list(self.rect.center)
        center[0] -= size_x / 2
        center[1] -= size_y / 2
        return center

    def __repr__(self):
        return str(self.__dict__)


class SelectScreenButton(Button):
    def activate(self):
        return self.img.removeprefix("images/").removesuffix(".png")


class Message(Sprite):
    def __init__(self, text, pos, groups):
        super().__init__(*groups)
        self.seen = False
        self.surf = FONT.render(text, True, "White")
        self.rect = self.surf.get_rect(center=pos)
        self.text = text
        self.timer = 40

    def update(self, pressed):
        enter = pressed[K_RETURN]
        if enter and not self.timer:
            self.kill()
            self.seen = True
        if self.timer > 0:
            self.timer -= 1

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
        self.max_hp = self.hp
        # Creates a Move instance for each name in the pokemon["Moves"] entry
        self.moves = [Move(move_name) for move_name in pokemon["Moves"]]
        self.attack = pokemon["Attack"]
        self.defense = pokemon["Defense"]
        self.speed = pokemon["Speed"]
        self.xp = pokemon["Experience"]

        # -Pygame Stuff-
        self.surf = pygame.image.load(f"images/{self.name.lower()}.png").convert_alpha()
        self.surf = pygame.transform.scale(self.surf, [150, 150])
        self.rect = self.surf.get_rect()

        # -Health Bar-
        self.bar_len = 200
        self.hp_ratio = self.max_hp / self.bar_len
        self.timer = 0
        self.offset_y = 0

    # Method to return the level of the pokemon
    def level(self):
        return math.floor(self.xp**(1/3))

    def draw_bar(self):
        if not self.timer % 20:
            self.offset_y = random.randint(100, 106)
        self.timer += 1
        pos = (self.rect.centerx - 90, self.rect.centery - self.offset_y)
        screen = pygame.display.get_surface()

        hp_text = SMALL_FONT.render(
                f"{int(self.hp)}/{self.max_hp}", True, "White")
        screen.blit(hp_text, (self.rect.centerx - 30, pos[1] - 40))

        rect = pygame.Rect(*pos, self.hp / self.hp_ratio, 25)
        pygame.draw.rect(screen, "#af0303", rect)
        pygame.draw.rect(screen, "White", (*pos, self.bar_len, 25), 4)

    # Attack Method
    def use_move(self, move, opponent):
        messages = []
        # Code to decide whether the attack is a critical hit
        critical = 1
        type_modifier = 1
        modifier = 1
        damage = 0
        critical_calc = random.randint(0, 511)
        if critical_calc < self.speed:
            critical = 2
            messages.append("A critical hit!")
        # Code to calculate the random modifier of the attack
        rand_modifier = random.randint(85, 100) / 100
        # Code to calculate the effectiveness of the attack

        # Super effective
        for index, effective in enumerate((move.super_effective, move.not_effective)):
            for i in effective:
                if i in opponent.type and index == 0:
                    type_modifier *= 2
                    messages.append("Super effective!")
                elif i in opponent.type and index == 1:
                    type_modifier /= 2
                    messages.append("Not very effective...")

        # Calculates the modifier
        modifier = critical * rand_modifier * type_modifier
        # Calculates damage (rounding to nearest integer)
        damage = round(
            ((((((2 * self.level()) / 5) + 2) * move.power * (
                        self.attack / opponent.defense)) / 50) * modifier),
            0)
        messages.insert(0, f"{self.name} used {move.name}!")
        messages.insert(1, f"Damage dealt: {int(damage)}")
        opponent.hp -= damage
        return messages


# Class to read in information from the move dictionary
class Move:
    def __init__(self, move_name):
        self.name = move_name
        stats = MOVES_DICTIONARY[self.name]
        self.power = stats["power"]
        self.move_type = stats["type"]
        self.super_effective = stats["super effective against"]
        self.not_effective = stats["not very effective against"]

