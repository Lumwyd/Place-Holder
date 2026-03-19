a = {3:"b", 5:"D"}
b = a = {3:"b", 5:"D"}

temp_dict = {}
to_remove = []
for thing in list(a.keys()):
    to_remove.append(thing)
    number = a[thing]
    thing += 1
    temp_dict[thing] = number
    
for thing in to_remove:
    a.pop(thing)

for thing in temp_dict:
    a[thing] = temp_dict[thing]
    
print(a)