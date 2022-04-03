import json
import math
import random
import pygame
from pygame import Surface
from pygame.sprite import Sprite
from pygame.locals import K_RETURN
from helper import Cooldown
from config import SCREEN_WIDTH, SCREEN_HEIGHT
from collections import namedtuple

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
    """Clickable buttons that float when hovered over"""
    def __init__(
            self,
            text: str,
            *,
            pos: tuple,
            color: tuple,
            groups: tuple,
            text_col: tuple,
            float_col: tuple | str,
            func=None,
            args: tuple = None,
            ):
        super().__init__(*groups)

        # -Pygame Stuff-
        # Creates surface with text on it
        self.text = FONT.render(text, False, text_col)
        self.surf = Surface(self.text.get_size())
        self.surf.fill(color)
        # Sets the surface of the actual button to the size of the text surface
        self.rect = self.surf.get_rect(center=pos)
        self.touch_box = self.rect.copy()
        self.start_y = self.rect.centery
        self.floating = False
        self.float_col = float_col
        self.color = color

        # -Button Stuff-
        self.func = func
        self.args = args
        self.hit_cooldown = Cooldown(10)

    def get_text_pos(self):
        """Gets the text centered on the button"""
        size_x, size_y = self.text.get_size()
        center = list(self.rect.center)
        center[0] -= size_x / 2
        center[1] -= size_y / 2
        return center

    def update(self):
        """Update the cooldown of getting hit"""
        self.hit_cooldown.update()

    def collide(self, point):
        """Check if one of the two hitboxes are collided with"""
        return self.rect.collidepoint(point) or self.touch_box.collidepoint(point)

    def handle_float(self, collide):
        """Float if collided with"""
        color = self.float_col
        if collide and not self.floating:
            self.rect.centery -= 20
            self.floating = True
        elif not collide:
            self.rect.centery = self.start_y
            self.floating = False
            color = self.color
        screen = pygame.display.get_surface()
        new_rect = self.rect.inflate(20, 20)
        pygame.draw.rect(screen, color, new_rect, border_radius=10)
        pygame.draw.rect(screen, "Black", new_rect, 5, border_radius=10)

    def activate(self):
        """Call the assigned function with the associated arguments"""
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


class ImageButton(Button):
    """Buttons with images, which can be transparent if not hovered over"""
    def __init__(
            self,
            image: str,
            image_size: tuple,
            *,
            pos: tuple,
            groups: tuple,
            alpha: int,
            return_
            ):
        Sprite.__init__(self, *groups)

        # -Pygame Stuff-
        self.surf = pygame.image.load(image).convert_alpha()
        self.img = image
        self.surf = pygame.transform.scale(self.surf, image_size)
        self.surf.set_alpha(alpha)
        # Sets the surface of the actual button to the size of the text surface
        self.rect = self.surf.get_rect(center=pos)
        self.touch_box = self.rect.copy()
        self.start_y = self.rect.centery
        self.floating = False
        self.alpha = alpha
        self.enabled = True

        # -Button Stuff-
        self.return_val = return_
        self.hit_cooldown = Cooldown(10)

    def handle_float(self, collide):
        """Float in the air when collision is passed in"""
        if self.enabled:
            if collide and not self.floating:
                self.rect.centery -= 20
                self.floating = True
            elif not collide:
                self.rect.centery = self.start_y
                self.floating = False

    def activate(self):
        """Returns the value assigned"""
        return self.return_val

    def get_text_pos(self):
        """Not implemented for this subclass"""
        raise NotImplementedError()

    def update(self):
        """Becomes transparent if the mouse is not hovering over it"""
        self.hit_cooldown.update()
        # Checks if cooldown is not active
        if not self.hit_cooldown and not self.floating:
            self.surf.set_alpha(self.alpha)
        elif not self.hit_cooldown and self.floating:
            self.surf.set_alpha(255)

    def disable(self):
        """Disable the button from being presssed"""
        self.alpha = 255
        self.enabled = False


class Message(Sprite):
    """A message to be displayed to the player"""
    reuse = False
    # Messages that freeze the screen and need to be manually advanced
    FROZEN = ("Name your pokemon!",)

    def __init__(self, text, pos, groups):
        super().__init__(*groups)
        self.seen = False
        self.surf = FONT.render(text, True, "Black")
        self.rect = self.surf.get_rect(center=pos)
        self.text = text
        # Timer for when the message can be advanced
        self.timer = 40
        self.bar_rect = pygame.Rect(0, pos[0] + 80, 0, 50)
        self.bar_vel = 2
        self.reuse_bar = self.__class__.reuse
        # Reuses bar every after the first message. This is undone once all
        # messages in a group are seen
        self.__class__.reuse = True

    def update(self, pressed):
        """Advance the bar and sense for when return is pressed"""
        # Gets the integer value for if the enter key is pressed
        enter = pressed[K_RETURN]
        if enter and not self.timer and self.text not in self.__class__.FROZEN:
            self.kill()
            # Marks as seen so the main loop can advance
            self.seen = True
        if self.timer > 0:
            self.timer -= 1
        if self.bar_rect.w < SCREEN_WIDTH:
            self.bar_rect.w += self.bar_vel
            self.bar_vel += 2.5

    def release(self):
        """Manually advance to the next messsage, can only be done if
        the message is a special frozen message"""
        if self.text not in self.__class__.FROZEN:
            # Can only manually release a message if it is frozen
            raise NotImplementedError()
        self.kill()
        self.seen = True

    def draw_bar(self, screen):
        """Draws the bar that is animated when the messages appears"""
        if self.reuse_bar:
            self.bar_rect.w = SCREEN_WIDTH
        pygame.draw.rect(screen, (225, 225, 225), self.bar_rect)
        # Draws a thin outline around the bar
        pygame.draw.rect(screen, "Black", self.bar_rect.inflate(5, 4), 5)

    def __ne__(self, other: str):
        return self.text != other

    def __repr__(self):
        return f"{self.__class__.__name__}({self.text}, pos={self.rect.center})"


class Pokemon(Sprite):
    """The pokemon to battle with"""

    def __init__(self, name: str, groups: tuple, given_name="", xp=None):
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
        if xp is None:
            # Sets xp to the default if not specified otherwise
            self.xp = pokemon["Experience"]
        else:
            self.xp = xp
        self.given_name = given_name

        # -Pygame Stuff-
        self.surf = pygame.image.load(f"images/{self.name.lower()}.png").convert_alpha()
        self.surf = pygame.transform.scale(self.surf, [150, 150])
        self.rect = self.surf.get_rect()
        self.particles = pygame.sprite.Group()
        self.hit_timer = Cooldown(55)
        self.x_off = False

        # -Health Bar-
        self.bar_len = 200
        self.hp_ratio = self.max_hp / self.bar_len
        self.timer = 0
        self.offset_y = 0

    def update(self):
        """Handles x offsets (when getting damaged)"""
        self.hit_timer.update()
        if self.hit_timer:
            if not self.x_off and not int(self.hit_timer) % 2:
                self.rect.centerx += 5
                self.x_off = True
            elif not int(self.hit_timer) % 2:
                self.rect.centerx -= 5
                self.x_off = False

    def level(self):
        """Return the level of the pokemon"""
        return math.floor(self.xp**(1/3))

    def draw_bar(self):
        """Draws the HP bar of the pokemon"""
        if not self.timer % 20:
            # Randomly moves every third of a second
            self.offset_y = random.randint(100, 106)
        self.timer += 1
        pos = (self.rect.centerx - 90, self.rect.centery - self.offset_y)
        screen = pygame.display.get_surface()

        # Creates text with the current hp in numbers and puts it over the
        # health bar
        hp_text = SMALL_FONT.render(
                f"{int(self.hp)}/{self.max_hp}", True, "White")
        screen.blit(hp_text, (self.rect.centerx - 30, pos[1] - 40))

        # Creates a rect for the current health
        rect = pygame.Rect(*pos, self.hp / self.hp_ratio, 25)
        pygame.draw.rect(screen, "#af0303", rect)
        # Draws white border around health bar
        pygame.draw.rect(screen, "White", (*pos, self.bar_len, 25), 4)

    def take_damage(self, amount):
        """Subtracts from hp, creates a Slash particle effect, and starts
        a timer to make an x_offset of the position for some time"""
        self.hp -= amount
        Slash(self.rect.center, 300, (self.particles,))
        self.hit_timer.reset()

    def use_move(self, move, opponent):
        """Uses specified move on opponent"""
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
        name = self.given_name if self.given_name else self.name
        messages.insert(0, f"{name} used {move.name}!")
        messages.insert(1, f"Damage dealt: {int(damage)}")
        if opponent.hp - damage <= 0:
            messages.append(f"{opponent.name} fainted!")
        return damage, messages

    def choose_move(self, target):
        """Finds the most damaging move to a pokemon"""
        MoveResult = namedtuple("MoveResult", "damage messages")
        big_damage = 0
        big_messages = ""
        for move in self.moves:
            result = self.use_move(move, target)
            if result[0] > big_damage:
                big_damage = result[0]
                big_messages = result[1]
        return MoveResult(big_damage, big_messages)

    def use_and_damage(self, move, opponent):
        """Calculates the damage of a move and applies it to the target"""
        result = self.use_move(move, opponent)
        opponent.take_damage(result[0])
        return result[1]


# Class to read in information from the move dictionary
class Move:
    """Holds information for a pokemon's move"""

    def __init__(self, move_name):
        self.name = move_name
        stats = MOVES_DICTIONARY[self.name]
        self.power = stats["power"]
        self.move_type = stats["type"]
        self.super_effective = stats["super effective against"]
        self.not_effective = stats["not very effective against"]


class Slash(Sprite):
    """An angled ellipse that looks like a slash"""

    def __init__(self, pos, angle, groups):
        super().__init__(*groups)
        self.angle = -(angle - 90)
        self.pos = list(pos)
        self.timer = 50
        self.width = 250
        self.screen = pygame.display.get_surface()

    def update(self):
        """Draws onto the screen and creates rotated surface"""
        # Creates a rectangle based on position and width
        rect = pygame.Rect(*self.pos, self.width, 20)
        rect.center = self.pos
        # Creates a surface
        surf = pygame.Surface(rect.size, pygame.SRCALPHA)
        if not self.timer % 7:
            # Turns the slash invisible every 7 frames
            if not surf.get_alpha:
                surf.set_alpha(255)
            else:
                surf.set_alpha(0)
        # Draws the ellipse on the surface
        pygame.draw.ellipse(surf, "Red", (0, 0, *rect.size))
        # Rotate the surface based on the angle
        rotate_surf = pygame.transform.rotate(surf, self.angle)
        self.screen.blit(rotate_surf, rotate_surf.get_rect(center=rect.center))
        if not self.timer:
            self.kill()
        self.timer -= 1


class TextSurf:
    """A text surface with a position"""

    def __init__(self, text, pos):
        self.text = SMALL_FONT.render(text, True, (255, 255, 255))
        self.pos = pos

    def blit(self):
        """Puts the text onto the screen"""
        screen = pygame.display.get_surface()
        screen.blit(self.text, self.pos)


class InputBox:
    """A box for the user to type into"""

    def __init__(self, pos, w, h, text="Enter name"):
        self.rect = pygame.Rect(*pos, w, h)
        self.color = "Grey"
        self.text = text
        self.txt_surface = FONT.render(text, True, self.color)
        self.usable = False
        self.typed = False

    def handle_event(self, event):
        """Handles the possibility of the user hitting a key"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                self.done = True
                return self.text
            elif event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            elif len(self.text) != 15:
                if not self.typed:
                    self.text = ""
                self.text += event.unicode
                self.typed = True
            if self.typed:
                self.color = "White"
            # Re-render the text
            self.txt_surface = FONT.render(self.text, True, self.color)
        return None

    def update(self):
        """Resizes the box if the text gets to large"""
        # Resize the box if the text is too long
        width = max(200, self.txt_surface.get_width() + 10)
        self.rect.w = width

    def draw(self, screen):
        """Puts the box onto the screen"""
        screen.blit(self.txt_surface, (self.rect.x+5, self.rect.y+5))
        pygame.draw.rect(screen, "White", self.rect, 2, 10)


class RisingBox:
    """A box that will rise until a certain height"""

    def __init__(self, height_max):
        self.rect = pygame.Rect(0, SCREEN_HEIGHT, SCREEN_WIDTH, 500)
        self.increase = 1
        self.max = height_max

    def draw(self, screen):
        """Puts the box onto the screen and increases its y position"""
        pygame.draw.rect(screen, (225, 225, 225), self.rect)
        pygame.draw.rect(screen, "Black", self.rect.inflate(20, 20), 10)
        if self.rect.top > self.max:
            self.rect.centery -= self.increase
            self.increase += 1.5

