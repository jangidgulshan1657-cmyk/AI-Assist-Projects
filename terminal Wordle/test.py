guess = [
    "crane", "slate", "pilot", "brave", "ghost", "money", "laugh", "trick",
    "flame", "stone", "plant", "shirt", "mouse", "dream", "light", "sound",
    "river", "table", "chair", "water", "happy", "smile", "night", "tiger"
    ]

answer = ['a','b','c']
for i, p in zip(guess,answer):# zip the two list in tuple with the order 
    print(f"{i}")# stops where the shortest list stop 
    print(f"{p}")


for i in range(6):# starts at o end before the number which is passed in range
    print(f"{i}")
    