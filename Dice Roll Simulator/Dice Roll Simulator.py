import random

def roll_dice(sides=6):
    return random.randint(1, sides)

num_rolls = int(input("How many dice to roll? "))
results = [roll_dice() for _ in range(num_rolls)]
print(f"Results: {results} | Total: {sum(results)}")
