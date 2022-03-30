import json


class Pokemon:
    def __init__(self, name: str):
        self.name = name
        self.type = POKEMONS[name]["Type"]
        self.hp = POKEMONS[name]["HP"]
        self.moves = POKEMONS[name]["Moves"]
        self.attack = POKEMONS[name]["Attack"]
        self.defense = POKEMONS[name]["Defense"]
        self.speed = POKEMONS[name]["Speed"]
        self.xp = 0
        self.level = 1

    def __repr__(self):
        return f"{self.__class__.__name__}({self.name}, {self.hp})"


with open("pokemons.json") as f:
    POKEMONS = json.load(f)

pokemon = Pokemon("Pikachu")
print(pokemon)
