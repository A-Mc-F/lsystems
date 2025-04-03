import turtle
import random
import json

lsystem = json.load(open("LSystems/Examples/4_both.lsystem"))

default_params = {
    "axiom": "F",
    "symbols": {
        "F": {"replacement": {"rule": "XY[++G][--G][G]"}},
        "G": {"replacement": {"rule": "XX[++G][--G][G]"}},
    },
    "line_length": 2,
    "line_length_variation": 0,
    "angle": 20,
    "angle_variation": 0.0,
    "tropism_angle": 90,
    "tropism_strength": 0.0,
    "colour": [0.3, 0.5, 0.2],
    "pen_size": 2,
    "start_pos": [0, -380],
    "sub_chance": 1.0,
}


def gen_rule():
    potential_characters = "abcdefghijklmnopqrstuvwxyz"
    angle_characters = "+-"
    branch_characters = "[]"
    branch_openings = 0

    rule = ""

    character = ""
    check = random.random()
    while check < 0.9:
        check = random.random()
        which = random.random()
        if which < 0.3:
            character = potential_characters[int(random.random() * 26)]
            if random.random() > 0.5:
                character = character.upper()
        elif which < 0.6:
            character = angle_characters[int(random.random() * 2)]
        else:
            character = branch_characters[int(random.random() * 2)]
            if character == "[":
                branch_openings += 1
            else:
                branch_openings -= 1

        rule += character

    closeing = ""
    if branch_openings > 0:
        closeing = "]" * branch_openings
        rule += closeing
    elif branch_openings < 0:
        closeing = "[" * -branch_openings
        rule = closeing + rule

    return rule


def load_attribute(attibute_name):
    global lsystem
    global default_params
    try:
        return lsystem[attibute_name]
    except:
        return default_params[attibute_name]


axiom = load_attribute("axiom")
string = axiom
symbols = load_attribute("symbols")

default_angle = load_attribute("angle")
default_angle_variation = load_attribute("angle_variation")
default_tropism_angle = load_attribute("tropism_angle")
default_tropism_strength = load_attribute("tropism_strength")
default_line_length = load_attribute("line_length")
default_line_length_variation = load_attribute("line_length_variation")
default_colour = load_attribute("colour")
default_pen_size = load_attribute("pen_size")
default_start_pos = load_attribute("start_pos")
default_sub_chance = load_attribute("sub_chance")


def replace(char):
    global symbols

    try:
        total_prob = sum(rule["probability"] for rule in symbols[char]["rules"])
        rand_choice = random.uniform(0, total_prob)
        cumulative_prob = 0
        for rule in symbols[char]["rules"]:
            cumulative_prob += rule["probability"]
            if rand_choice <= cumulative_prob:
                return rule["rule"]
    except:
        return char


def run_rules(axiom, iterations):

    for _ in range(iterations):
        symbols = "".join(replace(char) for char in axiom)

    return symbols


def draw_string(lindenmayer: turtle.Turtle, string):
    global symbols
    stack = []
    rotations = 0
    for char in string:
        if char == "[":
            stack.append((lindenmayer.heading(), lindenmayer.pos()))
        elif char == "]":
            (h, p) = stack.pop()
            should_hide = lindenmayer.isvisible()
            lindenmayer.hideturtle()
            lindenmayer.penup()
            lindenmayer.setheading(h)
            lindenmayer.setpos(p)
            lindenmayer.pendown()
            if should_hide:
                lindenmayer.showturtle()
        elif char == "+":
            rotations += 1
        elif char == "-":
            rotations -= 1
        else:
            try:
                colour = symbols[char]["draw"]["colour"]
            except:
                colour = default_colour
            lindenmayer.color(colour)

            try:
                pen_size = symbols[char]["draw"]["pen_size"]
            except:
                pen_size = default_pen_size
            lindenmayer.pensize(pen_size)

            if rotations != 0:
                try:
                    base_angle_increment = symbols[char]["draw"]["angle"]
                except:
                    base_angle_increment = default_angle

                new_angle_increment = rotations * base_angle_increment
            else:
                new_angle_increment = 0

            try:
                angle_variation = symbols[char]["draw"]["angle_variation"]
            except:
                angle_variation = default_angle_variation

            if angle_variation > 0:
                lindenmayer.right(random.gauss(new_angle_increment, angle_variation))
            else:
                lindenmayer.right(new_angle_increment)
            rotations = 0

            # tropism
            try:
                tropism_strength = symbols[char]["draw"]["tropism_strength"]
            except:
                tropism_strength = default_tropism_strength

            if tropism_strength > 0:

                try:
                    tropism_angle = symbols[char]["draw"]["tropism_angle"]
                except:
                    tropism_angle = default_tropism_angle

                hd = lindenmayer.heading()

                tropism_delta = hd - tropism_angle
                if tropism_delta > 180:
                    tropism_delta -= 360
                elif tropism_delta < -180:
                    tropism_delta += 360

                lindenmayer.right(tropism_delta * tropism_strength)

            try:
                line_length = symbols[char]["draw"]["line_length"]
            except:
                line_length = default_line_length

            try:
                line_length_variation = symbols[char]["draw"]["line_length_variation"]
            except:
                line_length_variation = default_line_length_variation

            if line_length_variation > 0:
                lindenmayer.forward(random.gauss(line_length, line_length_variation))
            else:
                lindenmayer.forward(line_length)


win = turtle.Screen()
win.title("L-Systems")
win.setup(800, 800)
win.bgcolor(0.9, 0.83, 0.7)

lindenmayer = turtle.Turtle()
lindenmayer.color(default_colour)
lindenmayer.pensize(default_pen_size)


def fast_mode():
    global win, lindenmayer
    print("Fast mode")
    win.tracer(0, 0)
    lindenmayer.hideturtle()
    lindenmayer.speed("fastest")


def slow_mode():
    global win, lindenmayer
    print("Slow mode")
    win.tracer(1, 25)
    lindenmayer.showturtle()
    lindenmayer.turtlesize(2)
    lindenmayer.speed("slow")


def iterate():
    global string

    lindenmayer.clear()
    lindenmayer.penup()
    lindenmayer.goto(default_start_pos)
    lindenmayer.setheading(90)
    lindenmayer.pendown()

    draw_string(lindenmayer, string)
    win.update()

    string = run_rules(string, 1)


fast_mode()

iterate()

print("ENTER to advance")
print("UP for fast mode")
print("DOWN for slow mode")

print(gen_rule())

win.onkey(iterate, "Return")
win.onkey(fast_mode, "Up")
win.onkey(slow_mode, "Down")
win.onkey(win.exitonclick, "Escape")

win.listen()
win.mainloop()
