import json
from pygame import Surface
from pygame.image import load
from pygame.sprite import Sprite, Group


class Pokemon(Sprite):
    def __init__(self, name: str, groups: tuple[Group]):
        super().__init__(*groups)
        pokemon = POKEMONS[name]
        self.name = name
        self.type = pokemon["Type"]
        self.hp = pokemon["HP"]
        self.moves = pokemon["Moves"]
        self.attack = pokemon["Attack"]
        self.defense = pokemon["Defense"]
        self.speed = pokemon["Speed"]
        self.xp = 0
        self.level = 1
        # self.surf = load(pokemon["Image"])
        self.surf = Surface((50, 50))
        self.rect = self.surf.get_rect()
        self.surf.fill((255, 255, 255))

    def __repr__(self):
        return f"{self.__class__.__name__}({self.name}, {self.hp})"


with open("pokemons.json") as f:
    POKEMONS = json.load(f)

pokemon = Pokemon("Pikachu", (Group(),))
print(pokemon)
