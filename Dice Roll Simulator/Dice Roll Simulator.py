import random
import time

def roll_dice(sides=6):
    """Roll a single die with the specified number of sides."""
    return random.randint(1, sides)

def animate_roll(sides=6):
    """Create a simple animation effect for dice rolling."""
    for _ in range(3):
        print(f"Rolling{'.' * (_ + 1)}", end="\r")
        time.sleep(0.3)
    return roll_dice(sides)

def main():
    print("🎲 DICE ROLL SIMULATOR 🎲")
    print("------------------------")
    
    while True:
        try:
            # Get number of dice
            num_dice = int(input("\nHow many dice would you like to roll? "))
            if num_dice <= 0:
                print("Please enter a positive number.")
                continue
                
            # Get number of sides
            sides = int(input("How many sides on each die? "))
            if sides <= 1:
                print("A die must have at least 2 sides.")
                continue
            
            # Roll the dice with animation
            results = []
            print("\nRolling dice...")
            for i in range(num_dice):
                result = animate_roll(sides)
                results.append(result)
                print(f"Die {i+1}: {result}")
            
            # Display results
            print("\n📊 RESULTS 📊")
            print(f"Individual rolls: {results}")
            print(f"Total: {sum(results)}")
            print(f"Average: {sum(results)/len(results):.2f}")
            
            if sides == 6:
                # For standard 6-sided dice
                if num_dice == 2 and sum(results) == 7:
                    print("Lucky 7!")
                elif num_dice == 2 and results[0] == results[1]:
                    print("Doubles!")
            
            # Ask to roll again
            play_again = input("\nWould you like to roll again? (y/n): ").lower()
            if play_again != 'y' and play_again != 'yes':
                print("Thanks for playing!")
                break
                
        except ValueError:
            print("Please enter a valid number.")

if __name__ == "__main__":
    main()