import pygame
from pygame.locals import (
    K_ESCAPE,
    KEYDOWN,
    QUIT,
)
import sys
from config import SCREEN_HEIGHT, SCREEN_WIDTH
import sprites
import random
import json
from os.path import getsize

GOD_MODE = False


class Game:
    """Manages the event loops of the game"""

    def __init__(self):
        # -General setup-
        pygame.init()
        self.screen = pygame.display.set_mode([SCREEN_WIDTH, SCREEN_HEIGHT])
        self.clock = pygame.time.Clock()
        pygame.display.set_caption("Pokémon Duels")

        # -Groups-
        self.all_sprites = pygame.sprite.Group()
        self.buttons = pygame.sprite.Group()
        self.move_buttons = pygame.sprite.Group()
        self.text = pygame.sprite.Group()
        self.pokemon = pygame.sprite.Group()

        # -Game stuff-
        self.player_pokemon = None
        self.cp_pokemon = None
        self.messages = []
        self.current_message = None
        self.background = pygame.image.load("images/background.png").convert()
        self.background = pygame.transform.scale(self.background, [1000, 750])
        with open("pokemon.json") as f:
            self.pokedex = json.load(f)
        self.button_background = None
        self.pokeball_image = pygame.image.load("images/pokeball.png").convert_alpha()
        self.pokeball_image = pygame.transform.scale(self.pokeball_image, (350, 350))

        with open("type_colors.json") as f:
            self.TYPE_COLORS = json.load(f)

    def player_turn(self):
        """Creates the player UI when taking their turn"""
        # Get the appropriate button spread depending on the amount of moves
        move_len = len(self.player_pokemon.moves)
        if move_len == 5:
            spread = 200
            start = 100
        elif move_len == 4:
            spread = 200
            start = 150
        else:
            spread = 300
            start = 200
        for index, move in enumerate(self.player_pokemon.moves):
            # Spreads the buttons out evenly across the screen
            pos = (index * spread + start, 650)
            # Creates a button to damage the pokemon with the corresponding
            # move when pressed
            sprites.Button(move.name,
                           pos=pos,
                           color=(198, 192, 198),
                           text_col=(0, 0, 0),
                           groups=(
                               self.all_sprites,
                               self.buttons,
                               self.move_buttons),
                           float_col=self.TYPE_COLORS[move.move_type],
                           func=self.player_pokemon.use_and_damage,
                           args=(move, self.cp_pokemon)
                           )
            self.p_turn = False
        self.button_background = sprites.RisingBox(600)

    def draw_capture(self, text_box):
        """Draws the UI for when the player beats the opponent"""
        pokeball_pos = (SCREEN_WIDTH / 2 - 175, SCREEN_HEIGHT / 2 - 175)
        self.screen.blit(self.pokeball_image, pokeball_pos)
        # Tests if that message is already on screen
        if self.current_message != "Name your pokemon!":
            # Prompts to name the pokemon
            self.current_message = sprites.Message(
                    "Name your pokemon!",
                    (500, 600),
                    (self.all_sprites, self.text)) 
        text_box.draw(self.screen)

    def log_pokemon(self, name, pokemon):
        """Log pokemon into pokedex"""
        self.pokedex[name] = {"xp": pokemon.xp, "type": pokemon.name}

    def battle(self, pokemon_info):
        """The battle screen between the player and the opponent"""
        self.player_pokemon = sprites.Pokemon(
                pokemon_info[1]["type"],
                (self.all_sprites, self.pokemon),
                pokemon_info[0],
                pokemon_info[1]["xp"]
                )
        if GOD_MODE:
            self.player_pokemon.xp = 100000000000000
        # Randomly chooses a pokemon for the computer
        self.cp_pokemon = sprites.Pokemon(
                random.choice(list(sprites.POKEMON.keys())),
                (self.all_sprites, self.pokemon)
                )
        # Puts both pokemon into set positions
        self.player_pokemon.rect.center = (150, 500)
        self.cp_pokemon.rect.center = (800, 375)

        if self.player_pokemon.speed > self.cp_pokemon.speed:
            self.p_turn = True
            self.messages.append(
                    f"{self.player_pokemon.given_name} goes first!")
        else:
            self.p_turn = False
            self.messages.append(f"{self.cp_pokemon.name} goes first!")

        # The input box for this screen, inactive by default
        text_box = sprites.InputBox((400, 290), 200, 50)

        running = True
        while running:
            mouse_pos = pygame.mouse.get_pos()

            for event in pygame.event.get():
                if text_box.usable:
                    inp = text_box.handle_event(event)
                    if inp is not None and inp not in self.pokedex and inp:
                        text_box.usable = False
                        self.log_pokemon(inp, self.cp_pokemon)
                        # Releases the suspended message 
                        self.current_message.release()

                if event.type == KEYDOWN:
                    if event.key == K_ESCAPE:
                        running = False

                elif event.type == QUIT:
                    running = False

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    # Checks if left click is used
                    if event.button != 1:
                        continue
                    for button in self.buttons:
                        if button.collide(mouse_pos) and not text_box.usable:
                            # Checks for collision with the point of the
                            # mouse position
                            results = button.activate()
                            for result in results:
                                self.messages.append(result)
                                if "fainted" in result:
                                    # Gives prompt to name pokemon, as a
                                    # defeated pokemon is a captured one
                                    text_box.usable = True

            # -Turn Order-
            if (self.current_message is None or self.current_message.seen) and not text_box.usable:
                try:
                    # Turns sets the current message
                    self.current_message = sprites.Message(
                            self.messages.pop(0),
                            (500, 600),
                            (self.all_sprites, self.text))
                except IndexError:
                    # Excepts when there are no messages
                    sprites.Message.reuse = False
            if self.p_turn and not self.move_buttons and self.current_message.seen:
                # Only starts a new player turn when the current message is seen
                self.player_turn()
            elif (not self.move_buttons and self.current_message.seen) and not text_box.usable:
                # Computer turn
                move_result = self.cp_pokemon.choose_move(self.player_pokemon)
                self.messages = move_result.messages
                self.player_pokemon.take_damage(move_result.damage)
                self.p_turn = True
                if "fainted" in self.messages[-1]:
                    self.log_pokemon(self.player_pokemon.given_name, self.player_pokemon)
                    print("Player lost!")

            pressed = pygame.key.get_pressed()
            self.buttons.update()
            # Messages need the enter key to be pressed in order to be seen
            self.text.update(pressed)
            self.pokemon.update()
            if text_box.usable:
                text_box.update()

            self.screen.blit(self.background, (0, 0))
            if self.move_buttons:
                self.button_background.draw(self.screen)
            if self.current_message is not None and not self.current_message.seen:
                self.current_message.draw_bar(self.screen)
            for sprite in self.all_sprites:
                self.screen.blit(sprite.surf, sprite.rect)
            # Puts button text on the screen
            for button in self.buttons:
                collide = button.touch_box.collidepoint(mouse_pos)
                if not text_box.usable:
                    button.handle_float(collide)
                self.screen.blit(button.text, button.get_text_pos())
            for pokemon in self.pokemon:
                pokemon.draw_bar()
                pokemon.particles.update()
            if text_box.usable:
                self.draw_capture(text_box)

            pygame.display.flip()
            self.clock.tick(60)

        self.log_pokemon(self.player_pokemon.given_name, self.player_pokemon)
        with open("pokemon.json", "w") as f:
            json.dump(self.pokedex, f, indent=4)
        pygame.quit()
        pygame.display.quit()
        sys.exit()

    def opening_screen(self, first_time):
        """The screen for when the player plays for the first time or open
        the game"""
        all_text = []
        if first_time:
            for index, pokemon in enumerate(
                    ("bulbasaur", "charmander", "squirtle")):
                pos = (index * 400 + 100, 300)
                # Creates button to return the corresponding pokemon name
                # when pressed
                sprites.ImageButton(
                        f"images/{pokemon}.png",
                        (225, 225),
                        groups=(self.all_sprites, self.buttons),
                        pos=pos,
                        alpha=100,
                        return_=pokemon
                        )
            open_text = "Choose and name your starter!"
        else:
            pos_y = 100
            START_AMOUNT = 80
            for index, (name, pokemon) in enumerate(self.pokedex.items()):
                pos_x = index * 150 + START_AMOUNT
                if index > 5:
                    # Wraps every 6 pokemon
                    pos_x = (index - 6) * 150 + START_AMOUNT
                    if index % 6 == 0:
                        # Increases y position to create a wrap effect
                        pos_y += 150
                pos = (pos_x, pos_y)
                # Creates button to return the name of the pokemon and the
                # pokemon info when pressed
                sprites.ImageButton(
                        f"images/{pokemon['type']}.png",
                        (100, 100),
                        groups=(self.all_sprites, self.buttons),
                        pos=pos,
                        alpha=100,
                        return_=(name, pokemon)
                        )
                # Centers the text a little more to the image
                all_text.append(sprites.TextSurf(name, (pos[0] - 45, pos[1] + 45)))
            open_text = "Choose your pokemon!"

        # Textbox is only usable in this screen when first_time is true
        text_box = sprites.InputBox((400, 500), 200, 60)

        text = sprites.FONT.render(open_text, True, (225, 225, 225))
        running = True
        while running:
            mouse_pos = pygame.mouse.get_pos()

            for event in pygame.event.get():
                if text_box.usable:
                    inp = text_box.handle_event(event)
                    if inp is not None and inp:
                        # Tests if the user enters their text
                        text_box.usable = False
                        running = False

                if event.type == KEYDOWN:
                    if event.key == K_ESCAPE:
                        pygame.quit()
                        pygame.display.quit()
                        sys.exit()

                elif event.type == QUIT:
                    pygame.quit()
                    pygame.display.quit()
                    sys.exit()

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        for button in self.buttons:
                            if button.collide(mouse_pos):
                                # Gets the selected pokemon the ImageButton
                                pokemon = button.activate()
                                try:
                                    # If first time is true, the button
                                    # will only return the pokemon's type
                                    # which needs to be capitalized
                                    pokemon = pokemon.title()
                                except AttributeError:
                                    pass
                                if first_time:
                                    # Opens prompt to name the pokemon
                                    text_box.usable = True
                                    button.disable()
                                    for button2 in self.buttons:
                                        if button2 is not button:
                                            button2.kill()
                                else:
                                    # Otherwise, quits the loop
                                    running = False

            if text_box.usable:
                text_box.update()
            self.buttons.update()

            self.screen.fill((0, 0, 0))
            for sprite in self.all_sprites:
                self.screen.blit(sprite.surf, sprite.rect)
            # Puts button text on the screen
            for button in self.buttons:
                # touch_box extends the rect of the button a bit downwards
                # so hitting the button is easy when it floats upwards
                collide = button.touch_box.collidepoint(mouse_pos)
                button.handle_float(collide)
            text_offset = text.get_width() / 2
            self.screen.blit(text, (SCREEN_WIDTH / 2 - text_offset, 600))
            for text_surf in all_text:
                self.screen.blit(text_surf.text, text_surf.pos)
            if text_box.usable:
                text_box.draw(self.screen)

            pygame.display.flip()
            self.clock.tick(60)

        for sprite in self.all_sprites:
            sprite.kill()
        if isinstance(pokemon, str):
            # If the pokemon just has it's type filled out because first_time
            # is true, the rest of the pokemon will be filled out for battle()
            pokemon = (inp, {"xp": None, "type": pokemon})
        self.battle(pokemon)


if __name__ == "__main__":
    if getsize("pokemon.json") <= 4:
        # When the user has no pokemon yet
        Game().opening_screen(True)
    else:
        # Pokemon select screen here
        Game().opening_screen(False)

