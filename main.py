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

        # -Game stuff-
        self.player_pokemon = sprites.Pokemon("Pikachu", (self.all_sprites, ))
        self.cp_pokemon = sprites.Pokemon("Bulbasaur", (self.all_sprites, ))
        self.player_pokemon.rect.center = (150, 600)
        self.cp_pokemon.rect.center = (800, 150)
        sprites.Button("Hello", (100, 100),
                       pos=(100, 100),
                       color=(255, 255, 255),
                       groups=(self.all_sprites, self.buttons),
                       press_col=(255, 0, 0)
                       )

    def player_turn(self):
        pass

    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == KEYDOWN:
                    if event.key == K_ESCAPE:
                        running = False

                elif event.type == QUIT:
                    running = False

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        mouse_pos = pygame.mouse.get_pos()
                        for button in self.buttons:
                            if button.rect.collidepoint(mouse_pos):
                                button.activate()

            self.screen.fill((0, 0, 0))

            self.buttons.update()

            for sprite in self.all_sprites:
                self.screen.blit(sprite.surf, sprite.rect)
            for button in self.buttons:
                self.screen.blit(button.text, button.get_text_pos())

            pygame.display.flip()
            self.clock.tick(60)

        pygame.quit()
        pygame.display.quit()
        sys.exit()


if __name__ == "__main__":
    Game().run()

