from random import *

mechanics = {"Platform Cycling":3,
             "Single Platform Cycling":6,
             "Unique Placement":8,
             "Multiple Jumps":6,
             "Dash Stacking": 7,
             "Jump + Dash":5,
             "Movement Refresh":8,
             "Crouch Extend":18,
             "Moving Platforms":5,
             "Death":7,
             "Platforming": 3,
             "Flow Mult": 10,
             "Flow Cycling":15}

level_number = 25

difficulty = int(level_number * 1.33)

ideas = []

while difficulty > 0:
    options = []
    for mechanic in list(mechanics.keys()):
        cost = mechanics[mechanic]
        if cost <= difficulty and not mechanic in ideas:
            options.append(mechanic)
    if options != []:
        option = choice(options)
        ideas.append(option)
        difficulty -= mechanics[option]
    else:
        break
    
print(ideas)