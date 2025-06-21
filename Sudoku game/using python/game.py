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

# Function to check if a move is valid
def is_valid_move(grid, row, col, num):
    # Check row, excluding current cell
    for j in range(9):
        if j != col and grid[row][j] == num:
            return False
    # Check column, excluding current cell
    for i in range(9):
        if i != row and grid[i][col] == num:
            return False
    # Check 3x3 subgrid, excluding current cell
    sub_row = (row // 3) * 3
    sub_col = (col // 3) * 3
    for i in range(sub_row, sub_row + 3):
        for j in range(sub_col, sub_col + 3):
            if (i != row or j != col) and grid[i][j] == num:
                return False
    return True

# Main game loop
print("Welcome to Sudoku!")
print("Commands:")
print("- 'row col num' to place a number (1-9) in row and column (1-9).")
print("- 'erase row col' to erase the number in row and column.")
print("- 'check' to verify if the puzzle is solved.")
print("- 'quit' to exit the game.")
print("- 'help' to show this message.")

while True:
    print_grid(user_grid)
    command = input("Enter command: ").strip().split()
    if not command:
        continue
    cmd = command[0].lower()

    if cmd == "quit":
        print("Thanks for playing!")
        break
    elif cmd == "check":
        if user_grid == solution:
            print("Congratulations! You've solved the puzzle!")
            print_grid(user_grid)
            break
        else:
            print("Not correct yet. Keep trying!")
    elif cmd == "erase":
        if len(command) != 3:
            print("Invalid erase command. Use 'erase row col'.")
            continue
        try:
            row, col = map(int, command[1:])
            row -= 1  # Adjust to 0-based indexing
            col -= 1
            if row < 0 or row > 8 or col < 0 or col > 8:
                print("Row and column must be between 1 and 9.")
            elif puzzle[row][col] != 0:
                print("This cell is fixed and cannot be erased.")
            elif user_grid[row][col] == 0:
                print(f"The cell ({row+1}, {col+1}) is already empty.")
            else:
                user_grid[row][col] = 0
                print(f"Erased cell ({row+1}, {col+1}).")
        except ValueError:
            print("Invalid input for erase. Enter two integers after 'erase'.")
    elif cmd == "help":
        print("Commands:")
        print("- 'row col num' to place a number (1-9) in row and column (1-9).")
        print("- 'erase row col' to erase the number in row and column.")
        print("- 'check' to verify if the puzzle is solved.")
        print("- 'quit' to exit the game.")
        print("- 'help' to show this message.")
    else:
        if len(command) != 3:
            print("Invalid input. Use 'row col num' (e.g., '1 1 3'), 'erase row col', 'check', 'quit', or 'help'.")
            continue
        try:
            row, col, num = map(int, command)
            row -= 1  # Adjust to 0-based indexing
            col -= 1
            if row < 0 or row > 8 or col < 0 or col > 8:
                print("Row and column must be between 1 and 9.")
            elif num < 1 or num > 9:
                print("Number must be between 1 and 9.")
            elif puzzle[row][col] != 0:
                print("This cell is fixed and cannot be changed.")
            elif not is_valid_move(user_grid, row, col, num):
                print("Invalid move: This number conflicts with existing numbers in the row, column, or subgrid.")
            elif user_grid[row][col] == num:
                print(f"The cell ({row+1}, {col+1}) already has the number {num}.")
            else:
                user_grid[row][col] = num
                print(f"Placed {num} in cell ({row+1}, {col+1}).")
        except ValueError:
            print("Invalid input. Use 'row col num' (e.g., '1 1 3'), 'erase row col', 'check', 'quit', or 'help'.")
