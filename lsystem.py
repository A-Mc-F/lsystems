import random

potential_characters = "abcdefghijklmnopqrstuvwxyz"
potential_characters = "abcdefghijk"
angle_characters = "+-"
branch_characters = "[]"

class LSystem:
    def __init__(self, start_pos:tuple = (0,0)):
        self.start_pos = start_pos
        self.axiom = ""
        self.symbols: dict[str,Symbol] = {}
        da = Symbol()
        da.randomise_attributes()
        self.default_attrbutes:Symbol = da

    def replace(self, char:str):
        if char in angle_characters or char in branch_characters:
            return char
        
        try:
            replacements = [*self.symbols[char].rules.keys()]
            probs = [*self.symbols[char].rules.values()]

            return random.choices(replacements, probs, k=1)[0]
        except:
            return char

    def run_rules(self, iterations):
        for _ in range(iterations):
            self.axiom = "".join(self.replace(char) for char in self.axiom)

def gen_rule(used_chars:list):
        branch_openings = 0

        num_of_chars = int(random.triangular(1, 9, 4))

        branch_chance = random.uniform(0.0,0.4)
        angle_chance = branch_chance + random.uniform(0.0,0.4)

        rule = ""

        last_char_type = ""
        for i in range(num_of_chars):
            character = ""
            which = random.random()

            if which < branch_chance and (num_of_chars - i) > 2:
                if last_char_type in ["open",""]:
                    character = "["
                    last_char_type = "open"
                    branch_openings += 1
                else:
                    leaning = 0.3 # open
                    if branch_openings > 0:
                        leaning = 0.7 # close
                    character = branch_characters[round(random.triangular(0,1,leaning))]
                    if character == "[":
                        last_char_type = "open"
                        branch_openings += 1
                    elif character == "]":
                        if branch_openings <= 0:
                            rule = "[" + rule
                            character = ""
                            branch_openings += 1
                        elif last_char_type in ["angle+","angle-"]:
                            character = ""
                        else:
                            branch_openings -= 1
                            last_char_type = "close"

            elif which < angle_chance and (num_of_chars - i) > 1:
                if last_char_type == "angle-":
                    character = "-"
                elif last_char_type == "angle+":
                    character = "+"
                else:
                    character = random.choice(angle_characters)
                    if character == "+":
                        last_char_type = "angle+"
                    elif character == "-":
                        last_char_type = "angle-"

            else:
                if random.random() < 0.9 and len(used_chars) > 0:
                    character = used_chars[int(random.random() * len(used_chars))]
                else:
                    character = potential_characters[int(random.random() * len(potential_characters))]
                    if random.random() > 0.5:
                        character = character.upper()
                    used_chars.append(character)
                last_char_type = "char"
                

            rule += character

        if branch_openings > 0:
            closeing = "]" * branch_openings
            if last_char_type == "open":
                if random.random() < 0.9 and len(used_chars) > 0:
                    character = used_chars[int(random.random() * len(used_chars))]
                else:
                    character = potential_characters[int(random.random() * len(potential_characters))]
                    if random.random() > 0.5:
                        character = character.upper()
                    used_chars.append(character)
                rule += character + closeing
            else:
                rule += closeing
        elif branch_openings < 0:
            closeing = "[" * -branch_openings
            rule = closeing + rule

        return rule, random.randint(1, 10)
    
class Symbol:
    def __init__(self):
        self.angle = 20.0
        self.angle_variation = 2.0
        self.tropism_angle = 10.0
        self.tropism_strength = 0.05
        self.line_length = 5.0
        self.line_length_variation = 1.0
        self.colour = [74,124,89]
        self.thickness = 2.0
        self.rules:dict = {}

    def randomise_attributes(self):
        self.angle = random.gauss(0.0, 50.0)
        self.angle_variation = random.uniform(0.0, 10.0)
        self.tropism_angle = random.uniform(0.0, 360.0)
        self.tropism_strength = random.gauss(0.0, 0.03)
        self.line_length = random.uniform(1.0, 10.0)
        self.line_length_variation = random.uniform(0.0, self.line_length / 2)
        self.colour = [random.triangular(0, 1, 0.2),
                       random.triangular(0, 1, 0.8),
                       random.triangular(0, 1, 0.3)]
        self.thickness = random.uniform(2, self.line_length *0.8)


    def to_string(self):
        return str(self.__dict__)
    

if __name__ == "__main__":
    lsystem = LSystem()
    lsystem.axiom = "F"
    characters = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J"]
    lsystem.symbols = {char: Symbol() for char in characters}
    for symbol in lsystem.symbols.items():
        char = symbol[0]
        symb = symbol[1]
        symb.randomise_attributes()
        symb.rules = {gen_rule(characters)}
        print(f"{char} {symb.to_string()}")
