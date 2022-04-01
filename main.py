import pygame
from pygame.locals import (
    K_ESCAPE,
    KEYDOWN,
    QUIT,
)
import sys
from config import SCREEN_HEIGHT, SCREEN_WIDTH
import sprites


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
        self.player_pokemon = sprites.Pokemon("Gengar", (self.all_sprites, ))
        self.cp_pokemon = sprites.Pokemon("Squirtle", (self.all_sprites, ))
        self.player_pokemon.surf = pygame.image.load(f"images/{self.player_pokemon.name.lower()}.png").convert_alpha()
        self.player_pokemon.surf = pygame.transform.scale(self.player_pokemon.surf, [150, 150])
        self.player_pokemon.rect.center = (150, 500)
        self.cp_pokemon.surf = pygame.image.load(f"images/{self.cp_pokemon.name.lower()}.png").convert_alpha()
        self.cp_pokemon.surf = pygame.transform.scale(self.cp_pokemon.surf, [150, 150])
        self.cp_pokemon.rect.center = (800, 375)
        self.messages = []
        self.current_message = None
        self.background = pygame.image.load("images/background.png").convert()
        self.background = pygame.transform.scale(self.background, [1000, 750])

        if self.player_pokemon.speed > self.cp_pokemon.speed:
            self.p_turn = True
            self.messages.append("Player goes first!")
        else:
            self.p_turn = False
            self.messages.append("Computer goes first!")

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
                           color=(255, 255, 255),
                           text_col=(0, 0, 0),
                           groups=(self.all_sprites, self.buttons, self.move_buttons),
                           float_col=(246, 213, 109),
                           press_col=(215, 0, 64),
                           func=self.player_pokemon.use_move,
                           args=(move, self.cp_pokemon)
                           )
            self.p_turn = False

    def run(self):
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
                            if button.rect.collidepoint(mouse_pos) or button.touch_box.collidepoint(mouse_pos):
                                # Checks for collision with the point of the
                                # mouse position
                                results = button.activate()
                                for result in results:
                                    self.messages.append(result)

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

            pygame.display.flip()
            self.clock.tick(60)

        pygame.quit()
        pygame.display.quit()
        sys.exit()


if __name__ == "__main__":
    Game().run()

