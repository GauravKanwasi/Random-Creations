# Define the initial Sudoku puzzle (0 represents blank cells)
puzzle = [
    [5, 3, 0, 0, 7, 0, 0, 0, 0],
    [6, 0, 0, 1, 9, 5, 0, 0, 0],
    [0, 9, 8, 0, 0, 0, 0, 6, 0],
    [8, 0, 0, 0, 6, 0, 0, 0, 3],
    [4, 0, 0, 8, 0, 3, 0, 0, 1],
    [7, 0, 0, 0, 2, 0, 0, 0, 6],
    [0, 6, 0, 0, 0, 0, 2, 8, 0],
    [0, 0, 0, 4, 1, 9, 0, 0, 5],
    [0, 0, 0, 0, 8, 0, 0, 7, 9]
]

# Define the solution to the puzzle
solution = [
    [5, 3, 4, 6, 7, 8, 9, 1, 2],
    [6, 7, 2, 1, 9, 5, 3, 4, 8],
    [1, 9, 8, 3, 4, 2, 5, 6, 7],
    [8, 5, 9, 7, 6, 1, 4, 2, 3],
    [4, 2, 6, 8, 5, 3, 7, 9, 1],
    [7, 1, 3, 9, 2, 4, 8, 5, 6],
    [9, 6, 1, 5, 3, 7, 2, 8, 4],
    [2, 8, 7, 4, 1, 9, 6, 3, 5],
    [3, 4, 5, 2, 8, 6, 1, 7, 9]
]

# Create a working copy of the puzzle for the user to modify
user_grid = [row[:] for row in puzzle]

# Function to display the Sudoku grid
def print_grid(grid):
    print("+-------+-------+-------+")
    for i in range(9):
        print("| ", end="")
        for j in range(9):
            if grid[i][j] == 0:
                print(". ", end="")
            else:
                print(f"{grid[i][j]} ", end="")
            if (j + 1) % 3 == 0:
                print("| ", end="")
        print()
        if (i + 1) % 3 == 0:
            print("+-------+-------+-------+")

# Main game loop
print("Welcome to Sudoku!")
print("Enter 'row col num' (e.g., '1 1 3') to place a number.")
print("Enter 'check' to verify your solution, or 'quit' to exit.")

while True:
    print_grid(user_grid)
    command = input("Enter command: ").strip()

    if command == "quit":
        print("Thanks for playing!")
        break
    elif command == "check":
        if user_grid == solution:
            print("Congratulations! You've solved the puzzle!")
            print_grid(user_grid)
            break
        else:
            print("Not correct yet. Keep trying.")
    else:
        try:
            # Parse input as row, column, number
            row, col, num = map(int, command.split())
            row -= 1  # Adjust to 0-based indexing
            col -= 1

            # Validate input ranges
            if row < 0 or row > 8 or col < 0 or col > 8:
                print("Row and column must be between 1 and 9.")
            elif num < 1 or num > 9:
                print("Number must be between 1 and 9.")
            elif puzzle[row][col] != 0:
                print("This cell is fixed and cannot be changed.")
            else:
                # Update the grid with the user's number
                user_grid[row][col] = num
        except ValueError:
            print("Invalid input. Enter three integers (e.g., '1 1 3'), 'check', or 'quit'.")
