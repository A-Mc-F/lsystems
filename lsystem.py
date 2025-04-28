import random
import math
import pygame
import yaml
from enum import Enum

config = yaml.safe_load(open("config.yaml", "r"))

class LSystem:
    def __init__(self, start_pos=(0, 0)):
        self.start_pos = start_pos
        self.axiom:list[Symbol] = []
        
        layers = 3
        builders:list[LineSymbolBuilder] = []
        for _ in range(layers):
            builder = LineSymbolBuilder()
            builder.gen_rules(builders)
            builders.append(builder)
        
        init_axiom = [builders[0].build()]
        for symbol in init_axiom:
            if type(symbol) is LineSymbolBuilder:
                symbol = symbol.build()
            else:
                symbol = symbol
            self.axiom.append(symbol)

    def iterate(self):
        """Run the replacement rules"""
        if len(self.axiom) > 1000:
            return 1
        
        new_axiom = []
        finished_growing = True
        for i, symbol in enumerate(self.axiom):
            finished_growing = (symbol.growth > 0.95) and finished_growing
            before = self.axiom[i - 1] if i > 0 else None
            after = self.axiom[i + 1] if i < len(self.axiom) - 1 else None
            new_axiom.extend(symbol.replace(before, after))
        self.axiom = new_axiom

        if finished_growing:
            return 1
        else:
            return 0

    def draw(self, screen):
        """Draw the L-system on the given screen.

        Args:
            screen (pygame.Surface): The Pygame screen to draw on.
        """
        pos_stack = []
        angle_stack = []
        base_pos = self.start_pos
        current_angle = -90
        direction_multiplier = 1

        for symbol in self.axiom:
            if type(symbol) is BranchSymbol:
                if symbol.state == BranchState.OPEN:
                    # Save the current position and angle
                    pos_stack.append(base_pos)
                    angle_stack.append(current_angle)
                elif symbol.state == BranchState.CLOSE and len(pos_stack) > 0:
                    # Restore the last saved position and angle
                    direction_multiplier = 1
                    base_pos = pos_stack.pop()
                    current_angle = angle_stack.pop()

            elif type(symbol) is DirectionSymbol:
                # left is positive angle, right is negative angle
                if symbol.direction == Direction.LEFT:
                    if direction_multiplier < 0:
                        direction_multiplier = 1
                elif symbol.direction == Direction.RIGHT:
                    if direction_multiplier > 0:
                        direction_multiplier = -1

            elif type(symbol) is LineSymbol:
                symbol.grow()
                length = max(1, symbol.length * symbol.growth)  # Ensure length is at least 1
                thickness = max(1, symbol.thickness * symbol.growth)  # Ensure thickness is at least 1
                angle = symbol.angle * symbol.growth  # Scale the angle by growth
                # Scale the color tuple from [0.0, 1.0] to [0, 255]
                colour = tuple(int(c * 255) for c in symbol.colour)

                new_angle = (current_angle + angle * direction_multiplier) % 360
                tropism_delta = (symbol.tropism_angle - new_angle + 180) % 360 - 180
                current_angle = (tropism_delta * symbol.tropism_strength + new_angle) % 360

                # Calculate the new position
                angle_radians = math.radians(current_angle)
                tip_pos = (
                    base_pos[0] + length * math.cos(angle_radians),
                    base_pos[1] + length * math.sin(angle_radians),
                )

                joint_pos_factor = 0.5 + 0.4*(symbol.length/(symbol.length+symbol.thickness))
                joint_pos = (
                    base_pos[0] + length * math.cos(angle_radians)*joint_pos_factor,
                    base_pos[1] + length * math.sin(angle_radians)*joint_pos_factor
                )

                # Draw the ellipse
                ellipse_rect = pygame.Rect(0, 0, length, thickness)
                ellipse_rect.center = (
                    (base_pos[0] + tip_pos[0]) / 2,
                    (base_pos[1] + tip_pos[1]) / 2,
                )
                ellipse_angle = math.degrees(angle_radians)
                if ellipse_rect.width > 0 and ellipse_rect.height > 0:
                    rotated_surface = pygame.Surface(ellipse_rect.size, pygame.SRCALPHA)
                    pygame.draw.ellipse(rotated_surface, colour, rotated_surface.get_rect())
                    if rotated_surface.get_width() > 0 and rotated_surface.get_height() > 0:
                        rotated_surface = pygame.transform.rotate(rotated_surface, -ellipse_angle)
                        screen.blit(rotated_surface, rotated_surface.get_rect(center=ellipse_rect.center))

                # Update the current position
                base_pos = joint_pos

class SymbolType(Enum):
    """Enum for symbol types."""
    LINE = 1
    DIRECTION = 2
    BRANCH = 3

class Symbol:
    def __init__(self, type=SymbolType.LINE):
        self.type = type
        self.age = 0.0
        self.growth = 1.0
    
    def replace(self, before, after):
        return [self]

class BranchState(Enum):
    """Enum for branch states."""
    OPEN = "["
    CLOSE = "]"

class BranchSymbol(Symbol):
    def __init__(self, state=None):
        super().__init__(SymbolType.BRANCH)
        if state is None:
            state = random.choice([BranchState.OPEN, BranchState.CLOSE])    
        self.state = state

class Direction(Enum):
    """Enum for direction types."""
    LEFT = "+"
    RIGHT = "-"

class DirectionSymbol(Symbol):
    def __init__(self, direction=None):
        super().__init__(SymbolType.DIRECTION)
        if direction is None:
            direction = random.choice([Direction.LEFT, Direction.RIGHT])
        self.direction = direction

class LineSymbol(Symbol):
    def __init__(self):
        super().__init__(SymbolType.LINE)
        self.age = 0.01
        self.growth = 0.0
        self.angle = 0.0
        self.tropism_angle = 0.0
        self.tropism_strength = 0.0
        self.length = 10
        self.thickness = 2
        self.colour = (0.2, 0.8, 0.3)
        self.rules:list[list[Symbol],float] = []  # Rules for symbol replacement [rule, probability]

    def grow(self):
        """Grow the symbol by increasing its age."""
        self.age += 0.01
        self.growth = 1-math.exp(-2*self.age)

    def replace(self, before, after):
        """Apply replacement rules to this symbol."""

        replace = random.random() > 0.98
        if self.rules and replace and self.growth > 0.5 and self.growth < 0.8:
            rules = [rule for rule, _ in self.rules]
            probabilities = [prob for _, prob in self.rules]
            abstract_rule = random.choices(rules, probabilities, k=1)[0]

            concrete_rule = [self]
            for symbol in abstract_rule:
                if type(symbol) is LineSymbolBuilder:
                    symbol = symbol.build()
                else:
                    symbol = symbol
                concrete_rule.append(symbol)

            return concrete_rule
        else:
            return [self]

class LineSymbolBuilder:
    def __init__(self):
        self.angle_tri = []
        self.tropism_angle = 0.0
        self.tropism_angle_SD = 0.0
        self.tropism_strength_tri = 0.0
        self.length_tri = []
        self.thickness_tri = []
        self.colour_red_tri = []
        self.colour_green_tri = []
        self.colour_blue_tri = []
        self.rules = []  # Initialize rules

        def _tri_range(low_lim, up_lim, max_range, preference=None):
            midpoint = random.triangular(low_lim, up_lim, preference)
            range = random.uniform(0, max_range)
            low = max(low_lim, midpoint - range)
            high = min(up_lim, midpoint + range)
            mid = random.triangular(low, high, midpoint)
            return [low, mid, high]

        # Randomize attributes
        min_angle = -90
        max_angle = 90
        max_angle_range = 45
        angle_preference = 0.0
        self.angle_tri = _tri_range(min_angle, max_angle, max_angle_range, angle_preference)

        self.tropism_angle = random.triangular(270-180, 270+180, 270)
        self.tropism_angle_SD = random.uniform(0.0, 10.0)

        self.tropism_strength_tri = _tri_range(0.0, 0.3, 0.1, 0.1)
        tropism_sign_chance = 0.8
        self.tropism_sign = random.choices([-1, 1],[1 - tropism_sign_chance, tropism_sign_chance],k=1)[0]

        min_length = 5.0
        max_length = 100.0
        self.length_tri = _tri_range(min_length, max_length, 5.0)

        min_thickness = 2.0
        max_thickness = self.length_tri[2] * 0.6
        self.thickness_tri = _tri_range(min_thickness, max_thickness, max_thickness * 0.2)

        min_colour = 0.0
        max_colour = 1.0
        colour_preference_red = 0.5
        colour_preference_green = 0.8
        colour_preference_blue = 0.5
        self.colour_red_tri = _tri_range(min_colour, max_colour,0.1, colour_preference_red)
        self.colour_green_tri = _tri_range(min_colour, max_colour,0.1, colour_preference_green)
        self.colour_blue_tri = _tri_range(min_colour, max_colour,0.1, colour_preference_blue)

    def gen_rules(self, other_builders:list[LineSymbolBuilder]):
        for _ in range(math.floor(random.triangular(1, 5, 1))):
            rule_and_prob = [gen_rule(other_builders.copy(), self), random.randint(1, 10)]
            self.rules.append(rule_and_prob)

    def build(self):
        """Create a concrete Symbol by randomizing attributes."""
        symbol = LineSymbol()

        symbol.type = SymbolType.LINE

        symbol.angle = random.triangular(self.angle_tri[0], self.angle_tri[2], self.angle_tri[1])
        symbol.tropism_angle = random.gauss(self.tropism_angle, self.tropism_angle_SD)
        
        symbol.tropism_strength = self.tropism_sign * random.triangular(self.tropism_strength_tri[0], self.tropism_strength_tri[2], self.tropism_strength_tri[1])
        
        symbol.length = random.triangular(self.length_tri[0], self.length_tri[2], self.length_tri[1])
        symbol.thickness = random.triangular(self.thickness_tri[0], self.thickness_tri[2], self.thickness_tri[1])
        symbol.colour = (
            random.triangular(self.colour_red_tri[0], self.colour_red_tri[2], self.colour_red_tri[1]),
            random.triangular(self.colour_green_tri[0], self.colour_green_tri[2], self.colour_green_tri[1]),
            random.triangular(self.colour_blue_tri[0], self.colour_blue_tri[2], self.colour_blue_tri[1])
        )

        symbol.rules = self.rules.copy()
        symbol.rules.append([[self], random.randint(1, 10)])
        symbol.rules.append([[BranchSymbol(BranchState.OPEN), DirectionSymbol(), self, BranchSymbol(BranchState.CLOSE)], random.randint(1, 10)])

        return symbol
    

def gen_rule(outsourced_builders:list=[], line_symbol:LineSymbol=None) -> list[Symbol]:

    internal_builders = []

    branch_openings:int = 0
    direction:int = 0

    num_of_symbols = int(random.triangular(1, 10, 1))

    branch_chance = random.uniform(0.3,0.6)
    angle_chance = branch_chance + random.uniform(0.2,0.3)

    rule = []

    last_symbol:Symbol = None

    charaters:int = 0
    while charaters < num_of_symbols:
        which = random.random()

        if which < branch_chance and (num_of_symbols - i) > 2 and last_symbol != None:
            # Branching
            branch_chance -= 0.1
            angle_chance += 0.1
            if type(last_symbol) in [BranchSymbol, DirectionSymbol]:
                last_symbol = BranchSymbol(BranchState.OPEN)
                rule.append(last_symbol)
                branch_openings += 1

            elif type(last_symbol) is LineSymbol:
                leaning = 0.7 if branch_openings > 0 else 0.3
                state = [BranchState.OPEN,BranchState.CLOSE][round(random.triangular(0,1,leaning))]
                if state == BranchState.OPEN:
                    last_symbol = BranchSymbol(state)
                    rule.append(last_symbol)
                    branch_openings += 1
                elif state == BranchState.CLOSE:
                    last_symbol = BranchSymbol(state)
                    rule.append(last_symbol)
                    branch_openings -= 1

        elif which < angle_chance and (num_of_symbols - i) > 2:
            angle_chance -= 0.1
            branch_chance -= 0.1
            # Direction
            if type(last_symbol) is DirectionSymbol:
                if last_symbol.direction == Direction.LEFT:
                    last_symbol = DirectionSymbol(Direction.LEFT)
                elif last_symbol.direction == Direction.RIGHT:
                    last_symbol = DirectionSymbol(Direction.RIGHT)
            else:
                leaning = 0.4
                if direction > 0:
                    leaning = 0.6
                state = [Direction.RIGHT,Direction.LEFT][round(random.triangular(0,1,leaning))]
                if state == Direction.RIGHT:
                    last_symbol = DirectionSymbol(state)
                    direction += 1
                elif state == Direction.LEFT:
                    last_symbol = DirectionSymbol(state)
                    direction -= 1
            rule.append(last_symbol)

        else:
            # Line
            branch_chance += 0.1
            charaters += 1
            chance = random.random()
            if chance < 0.2 and line_symbol is not None:
                rule.append(line_symbol)
            elif chance < 0.6 and len(internal_builders) > 0:
                builder = random.choice(internal_builders)
                rule.append(builder)
            elif chance < 0.9 and len(outsourced_builders) > 0:
                builder = random.choice(outsourced_builders)
                rule.append(builder)
            else:
                new_builder = LineSymbolBuilder()
                internal_builders.append(new_builder)
                rule.append(new_builder)

    # Close off any open branches
    if branch_openings > 0:
        if type(last_symbol) is BranchSymbol:
            if last_symbol.state == BranchState.OPEN:
                if len(outsourced_builders) > 0:
                    last_symbol = random.choice(outsourced_builders)
                else:
                    last_symbol = LineSymbolBuilder()
                rule.append(last_symbol)
        close_off = [BranchSymbol(BranchState.CLOSE)] * branch_openings
        rule.extend(close_off)

    elif branch_openings < 0:
        close_off = [BranchSymbol(BranchState.OPEN)] * abs(branch_openings)
        close_off.extend(rule)

    return rule

        
if __name__ == "__main__":
    import pygame

    # Pygame setup
    pygame.init()
    window_width = 1000
    window_height = 700
    screen = pygame.display.set_mode((window_width, window_height))
    pygame.display.set_caption("Multiple L-Systems in Pygame")
    clock = pygame.time.Clock()

    # Main loop
    running = True
    i = 0
    done = 0
    
    poss = [0.25,0.5, 0.75]
    start_positions= [(window_width*pos, window_height*0.8) for pos in poss]
    base_lsystem = LSystem(start_positions[0])
    lsystems = [LSystem(start_pos) for start_pos in start_positions]
    for lsystem in lsystems:
        lsystem.axiom = base_lsystem.axiom.copy()

    timer = 0
    time_up = False

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Clear the screen
        screen.fill((255, 255, 255))
        
        # Grow and draw all L-Systems
        still_growing = False
        for lsystem in lsystems:
            lsystem.draw(screen)
            if lsystem.iterate() != 1:
                still_growing = True

        if not still_growing or time_up:
            base_lsystem = LSystem(start_positions[0])
            lsystems = [LSystem(start_pos) for start_pos in start_positions]
            for lsystem in lsystems:
                lsystem.axiom = base_lsystem.axiom.copy()
            done = 0

        timer+=1
        if timer > 1000:
            timer = 0
            time_up = True
        else:
            time_up = False

        # Update the display
        pygame.display.flip()

        # Cap the frame rate
        clock.tick(30)

    pygame.quit()

