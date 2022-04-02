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

    def log_pokemon(self, pokemon):
        self.pokedex[pokemon.name] = pokemon.xp

    def battle(self, pokemon_name, xp=None):
        self.player_pokemon = sprites.Pokemon(pokemon_name, (self.all_sprites,), xp)
        self.cp_pokemon = sprites.Pokemon(random.choice(list(sprites.POKEMON.keys())), (self.all_sprites, ))
        self.player_pokemon.rect.center = (150, 500)
        self.cp_pokemon.rect.center = (800, 375)

        if self.player_pokemon.speed > self.cp_pokemon.speed:
            self.p_turn = True
            self.messages.append("Player goes first!")
        else:
            self.p_turn = False
            self.messages.append("Computer goes first!")

        running = True
        while running:
            mouse_pos = pygame.mouse.get_pos()

            for event in pygame.event.get():
                if event.type == KEYDOWN:
                    if event.key == K_ESCAPE:
                        running = False

                elif event.type == QUIT:
                    running = False

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        for button in self.buttons:
                            if button.collide(mouse_pos):
                                # Checks for collision with the point of the
                                # mouse position
                                results = button.activate()
                                for result in results:
                                    self.messages.append(result)
                                    if "fainted" in result:
                                        self.log_pokemon(self.cp_pokemon)
                                        print("Opponent lost")

            # -Turn Order-
            if self.current_message is None or self.current_message.seen:
                try:
                    self.current_message = sprites.Message(self.messages.pop(0), (500, 600), (self.all_sprites, self.text))
                except IndexError:
                    pass
            if self.p_turn and not self.move_buttons and self.current_message.seen:
                self.player_turn()
            elif not self.move_buttons and self.current_message.seen:
                # Computer turn
                self.messages = self.cp_pokemon.use_move(self.cp_pokemon.moves[-1], self.player_pokemon)
                self.p_turn = True
                if "fainted" in self.messages[-1]:
                    self.log_pokemon(self.player_pokemon)
                    print("Player lost!")

            pressed = pygame.key.get_pressed()
            self.buttons.update()
            self.text.update(pressed)

            self.screen.blit(self.background, (0, 0))
            for sprite in self.all_sprites:
                self.screen.blit(sprite.surf, sprite.rect)
            # Puts button text on the screen
            for button in self.buttons:
                collide = button.touch_box.collidepoint(mouse_pos)
                button.handle_float(collide)
                self.screen.blit(button.text, button.get_text_pos())
            for pokemon in (self.player_pokemon, self.cp_pokemon):
                pokemon.draw_bar()
            for pokemon in (self.player_pokemon, self.cp_pokemon):
                pokemon.particles.update()

            pygame.display.flip()
            self.clock.tick(60)

        self.log_pokemon(self.player_pokemon)
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
            for index, pokemon in enumerate(self.pokedex.keys()):
                pos_x = index * 150 + START_AMOUNT
                if index > 9:
                    pos_x = (index - 10) * 150 + START_AMOUNT
                    if index % 10 == 0:
                        pos_y += 150
                pos = (pos_x, pos_y)
                sprites.ImageButton(
                        f"images/{pokemon}.png",
                        (100, 100),
                        groups=(self.all_sprites, self.buttons),
                        pos=pos,
                        alpha=100,
                        return_=pokemon
                        )
                all_text.append(sprites.TextSurf(pokemon, (pos[0] - 45, pos[1] + 45)))
            open_text = "Choose your pokemon!"
        running = True
        text = sprites.FONT.render(open_text, True, (225, 225, 225))
        while running:
            mouse_pos = pygame.mouse.get_pos()

            for event in pygame.event.get():
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
                                pokemon = button.activate().title()
                                running = False

            self.buttons.update()

            self.screen.fill((0, 0, 0))
            for sprite in self.all_sprites:
                self.screen.blit(sprite.surf, sprite.rect)
            # Puts button text on the screen
            for button in self.buttons:
                collide = button.touch_box.collidepoint(mouse_pos)
                button.handle_float(collide)
            self.screen.blit(text, (SCREEN_WIDTH / 2 - 150, 600))
            for text_surf in all_text:
                self.screen.blit(text_surf.text, text_surf.pos)

            pygame.display.flip()
            self.clock.tick(60)

        for sprite in self.all_sprites:
            sprite.kill()
        self.battle(pokemon)


if __name__ == "__main__":
    if getsize("pokemon.json") <= 4:
        Game().opening_screen(True)
    else:
        # Pokemon select screen here
        Game().opening_screen(False)

