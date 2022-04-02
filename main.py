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


class Game:
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

        # -Game stuff-
        self.player_pokemon = None
        self.cp_pokemon = None
        self.messages = []
        self.current_message = None
        self.background = pygame.image.load("images/background.png").convert()
        self.background = pygame.transform.scale(self.background, [1000, 750])
        with open("pokemon.json") as f:
            self.pokedex = json.load(f)

    def player_turn(self):
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
            sprites.Button(move.name,
                           pos=pos,
                           color=(208, 202, 208),
                           text_col=(0, 0, 0),
                           groups=(self.all_sprites, self.buttons, self.move_buttons),
                           float_col="#ffd700",
                           func=self.player_pokemon.use_move,
                           args=(move, self.cp_pokemon)
                           )
            self.p_turn = False

    def log_pokemon(self, name, pokemon):
        """Log pokemon into pokedex"""
        self.pokedex[name] = {"xp": pokemon.xp, "type": pokemon.name}

    def battle(self, pokemon_info):
        self.player_pokemon = sprites.Pokemon(pokemon_info[1]["type"], (self.all_sprites,), pokemon_info[0], pokemon_info[1]["xp"])
        # Randomly chooses a pokemon for the computer
        self.cp_pokemon = sprites.Pokemon(random.choice(list(sprites.POKEMON.keys())), (self.all_sprites, ))
        # Puts both pokemon into set positions
        self.player_pokemon.rect.center = (150, 500)
        self.cp_pokemon.rect.center = (800, 375)

        if self.player_pokemon.speed > self.cp_pokemon.speed:
            self.p_turn = True
            self.messages.append("Player goes first!")
        else:
            self.p_turn = False
            self.messages.append("Computer goes first!")

        text_box = sprites.InputBox((400, 300), 200, 50)

        running = True
        while running:
            mouse_pos = pygame.mouse.get_pos()

            for event in pygame.event.get():
                if text_box.usable:
                    inp = text_box.handle_event(event)
                    if inp is not None and inp not in self.pokedex:
                        text_box.usable = False
                        self.log_pokemon(inp, self.cp_pokemon)

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
                                    text_box.usable = True

            # -Turn Order-
            if (self.current_message is None or self.current_message.seen) and not text_box.usable:
                try:
                    # Turns sets the current message
                    self.current_message = sprites.Message(self.messages.pop(0), (500, 600), (self.all_sprites, self.text))
                except IndexError:
                    # Excepts when there are no messages
                    pass
            if self.p_turn and not self.move_buttons and self.current_message.seen:
                # Only starts a new player turn when the current message is seen
                self.player_turn()
            elif (not self.move_buttons and self.current_message.seen) and not text_box.usable:
                # Computer turn
                self.messages = self.cp_pokemon.use_move(self.cp_pokemon.moves[-1], self.player_pokemon)
                self.p_turn = True
                if "fainted" in self.messages[-1]:
                    self.log_pokemon(self.player_pokemon.given_name, self.player_pokemon)
                    print("Player lost!")

            pressed = pygame.key.get_pressed()
            self.buttons.update()
            # Messages need the enter key to be pressed in order to be seen
            self.text.update(pressed)
            if text_box.usable:
                text_box.update()

            self.screen.blit(self.background, (0, 0))
            for sprite in self.all_sprites:
                self.screen.blit(sprite.surf, sprite.rect)
            # Puts button text on the screen
            for button in self.buttons:
                collide = button.touch_box.collidepoint(mouse_pos)
                if not text_box.usable:
                    button.handle_float(collide)
                self.screen.blit(button.text, button.get_text_pos())
            for pokemon in (self.player_pokemon, self.cp_pokemon):
                pokemon.draw_bar()
            for pokemon in (self.player_pokemon, self.cp_pokemon):
                pokemon.particles.update()
            if text_box.usable:
                pygame.draw.circle(self.screen, (30, 30, 30), (SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2), 150)
                capture_text = sprites.SMALL_FONT.render("Name your pokemon!", True, "White")
                self.screen.blit(capture_text, (380, 400))
                text_box.draw(self.screen)

            pygame.display.flip()
            self.clock.tick(60)

        self.log_pokemon(self.player_pokemon.given_name, self.player_pokemon)
        with open("pokemon.json", "w") as f:
            json.dump(self.pokedex, f, indent=4)
        pygame.quit()
        pygame.display.quit()
        sys.exit()

    def opening_screen(self, first_time):
        all_text = []
        if first_time:
            for index, pokemon in enumerate(("bulbasaur", "charmander", "squirtle")):
                pos = (index * 400 + 100, 300)
                sprites.ImageButton(
                        f"images/{pokemon}.png",
                        (225, 225),
                        groups=(self.all_sprites, self.buttons),
                        pos=pos,
                        alpha=100,
                        return_=pokemon
                        )
            open_text = "Choose your starter!"
        else:
            pos_y = 100
            START_AMOUNT = 80
            for index, (name, pokemon) in enumerate(self.pokedex.items()):
                pos_x = index * 150 + START_AMOUNT
                if index > 5:
                    pos_x = (index - 6) * 150 + START_AMOUNT
                    if index % 6 == 0:
                        # Increases y position to create a wrap effect
                        pos_y += 150
                pos = (pos_x, pos_y)
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
        text_box = sprites.InputBox((500, 500), 200, 60)

        text = sprites.FONT.render(open_text, True, (225, 225, 225))
        running = True
        while running:
            mouse_pos = pygame.mouse.get_pos()

            for event in pygame.event.get():
                if text_box.usable:
                    inp = text_box.handle_event(event)
                    if inp is not None:
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
            self.screen.blit(text, (SCREEN_WIDTH / 2 - 150, 600))
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

