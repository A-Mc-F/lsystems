import turtle
import random
import json
from lsystem import LSystem, gen_rule, Symbol

def draw_string(lindenmayer_turtle: turtle.Turtle, lsystem:LSystem):
    stack = []
    rotations = 0
    for char in lsystem.axiom:
        if char == "[":
            stack.append((lindenmayer_turtle.heading(), lindenmayer_turtle.pos()))
            if rotations != 0:
                base_angle_increment = lsystem.default_attrbutes.angle

                new_angle_increment = rotations * base_angle_increment

                angle_variation = lsystem.default_attrbutes.angle_variation

                if angle_variation > 0:
                    lindenmayer_turtle.right(random.gauss(new_angle_increment, angle_variation))
                else:
                    lindenmayer_turtle.right(new_angle_increment)
                    
                rotations = 0
        elif char == "]":
            (h, p) = stack.pop()
            should_hide = lindenmayer_turtle.isvisible()
            lindenmayer_turtle.hideturtle()
            lindenmayer_turtle.penup()
            lindenmayer_turtle.setheading(h)
            lindenmayer_turtle.setpos(p)
            lindenmayer_turtle.pendown()
            if should_hide:
                lindenmayer_turtle.showturtle()
        elif char == "+":
            rotations += 1
        elif char == "-":
            rotations -= 1
        else:
            try:
                colour = lsystem.symbols[char].colour
            except:
                colour = lsystem.default_attrbutes.colour
            lindenmayer_turtle.color(colour)

            try:
                pen_size = lsystem.symbols[char].thickness
            except:
                pen_size = lsystem.default_attrbutes.thickness
            lindenmayer_turtle.pensize(pen_size)

            if rotations != 0:
                try:
                    base_angle_increment = lsystem.symbols[char].angle
                except:
                    base_angle_increment = lsystem.default_attrbutes.angle

                new_angle_increment = rotations * base_angle_increment
            else:
                new_angle_increment = 0

            try:
                angle_variation = lsystem.symbols[char].angle_variation
            except:
                angle_variation = lsystem.default_attrbutes.angle_variation

            if angle_variation > 0:
                lindenmayer_turtle.right(random.gauss(new_angle_increment, angle_variation))
            else:
                lindenmayer_turtle.right(new_angle_increment)
            rotations = 0


            # tropism
            try:
                tropism_strength = lsystem.symbols[char].tropism_strength
            except:
                tropism_strength = lsystem.default_attrbutes.tropism_strength

            # 0 is up
            try:
                tropism_angle = lsystem.symbols[char].tropism_angle
            except:
                tropism_angle = lsystem.default_attrbutes.tropism_angle

            # 0 is to the right, 90 is up; taking off 90 degrees to correct angle
            hd = lindenmayer_turtle.heading() - 90

            tropism_delta = hd - tropism_angle
            if tropism_delta > 180:
                tropism_delta -= 360
            elif tropism_delta < -180:
                tropism_delta += 360

            lindenmayer_turtle.right(tropism_delta * tropism_strength)

            # Line length
            try:
                line_length = lsystem.symbols[char].line_length
            except:
                line_length = lsystem.default_attrbutes.line_length

            try:
                line_length_variation = lsystem.symbols[char].line_length_variation
            except:
                line_length_variation = lsystem.default_attrbutes.line_length_variation

            if line_length_variation > 0:
                lindenmayer_turtle.forward(random.gauss(line_length, line_length_variation))
            else:
                lindenmayer_turtle.forward(line_length)

win = turtle.Screen()
win.title("L-Systems")
win.setup(800, 800)
win.bgcolor(0.9, 0.83, 0.7)

lindenmayer = turtle.Turtle()

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

def redraw(lsystem:LSystem):
    lindenmayer.penup()
    lindenmayer.goto(lsystem.start_pos[0], lsystem.start_pos[1])
    lindenmayer.setheading(90)
    lindenmayer.pendown()

    draw_string(lindenmayer, lsystem)
    win.update()


def iterate():
    global lsystems
    
    lindenmayer.clear()

    for ls in lsystems:
        ls.run_rules(1)
        print(ls.axiom)
        redraw(ls)

    


fast_mode()

l_system1 = LSystem()
l_system1.start_pos = (100, -300)
characters = ["A", "B", "C"]
l_system1.axiom = gen_rule(characters)[0]
print(l_system1.axiom)
l_system1.symbols = {char: Symbol() for char in characters}
for symbol in l_system1.symbols.items():
    char = symbol[0]
    symb = symbol[1]
    symb.randomise_attributes()
    for i in range(random.randint(1, 3)):
        rule, prob = gen_rule(characters)
        
        symb.rules[rule] = prob
    print(f"{char} {symb.to_string()}")

l_system2 = LSystem()
l_system2.start_pos = (-100, -300)
characters = ["A", "B", "C"]
l_system2.axiom = gen_rule(characters)[0]
print(l_system2.axiom)
l_system2.symbols = {char: Symbol() for char in characters}
for symbol in l_system2.symbols.items():
    char = symbol[0]
    symb = symbol[1]
    symb.randomise_attributes()
    for i in range(random.randint(1, 3)):
        rule, prob = gen_rule(characters)
        
        symb.rules[rule] = prob
    print(f"{char} {symb.to_string()}")


lsystems = [l_system1, l_system2]

print("ENTER to advance")
print("UP for fast mode")
print("DOWN for slow mode")

win.onkey(iterate, "Return")
win.onkey(fast_mode, "Up")
win.onkey(slow_mode, "Down")
win.onkey(win.exitonclick, "Escape")
win.onkeypress(redraw, "space")

win.listen()
win.mainloop()
