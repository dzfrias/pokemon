import random
import json


# Reads in the dictionaries from the json files
with open('moves_dictionary.json') as json_file:
    MOVES_DICTIONARY = json.load(json_file)
with open('characters.json') as json_file:
    CHARACTERS = json.load(json_file)


# Class to read in information from the move dictionary
class Move:
    def __init__(self, move_name):
        self.name = move_name
        self.power = MOVES_DICTIONARY[self.name]["power"]
        self.type = MOVES_DICTIONARY[self.name]["type"]
        self.super_effective = MOVES_DICTIONARY[self.name]["super effective against"]
        self.not_effective = MOVES_DICTIONARY[self.name]["not very effective against"]


# Attack method
def attack(speed, move, opponent_type, level, attack, defense, defender_hp):
    # Code to decide whether the attack is a critical hit
    critical = 1
    critical_calc = random.randint(0, 511)
    if critical_calc < speed:
        critical = 2
        print("A critical hit!")
    # Code to calculate the random modifier of the attack
    rand_modifier = random.randint(85, 100)/100
    # Code to calculate the effectiveness of the attack
    super_effective = move["super_effective"]
    not_effective = move["not_effective"]
    type = 1
    # Super effective
    if len(super_effective) != 0:
        if len(super_effective) > 1:
            for i in super_effective:
                if i == opponent_type:
                    type *= 2
                    print("Super effective...")
        else:
            if opponent_type in super_effective:
                type *= 2
                print("Super effective...")
    # Not very effective
    if len(not_effective) != 0:
        if len(not_effective) > 1:
            for i in not_effective:
                if i == opponent_type:
                    type /= 2
                    print("Not very effective...")
        else:
            if opponent_type in super_effective:
                type /= 2
                print("Not very effective...")
    # Calculates the modifier
    modifier = critical * rand_modifier * type
    # Finds the power of the move
    power = move["power"]
    damage = (((((2*level)/5)+2) * power * (attack / defense))/50) * modifier
    print(f"damage dealt: {damage}")
    defender_hp -= damage
    print(f"defender hp: {defender_hp}")


bite = Move("Bite")
move_info = {"name": bite.name, "power": bite.power, "type": bite.type, "super_effective": bite.super_effective,
             "not_effective": bite.not_effective}
attack(60, move_info, "Ghost", 50, 65, 60, 60)


