from random import *

mechanics = {"Pogo":4,
             "Unique Placement":5,
             "Multiple Jumps":6,
             "Dash Stacking": 7,
             "Movement Refresh":8,
             "Moving Platforms":5,
             "Death":7,
             "Flow Mult": 10}

level_number = 19

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