// Sudoku game logic
const grid = document.getElementById('grid');
const newGameBtn = document.getElementById('new-game');
const solveBtn = document.getElementById('solve');
const hintBtn = document.getElementById('hint');
const checkBtn = document.getElementById('check');
const status = document.getElementById('status');
const timerElement = document.querySelector('.timer');
const difficultyBtns = document.querySelectorAll('.difficulty button');
const numberBtns = document.querySelectorAll('.number-btn');

let selectedCell = null;
let puzzle = [];
let solution = [];
let currentPuzzle = [];
let difficulty = 'easy';
let timerInterval;
let seconds = 0;
let gameActive = false;

// Initialize the empty grid
initializeGrid();

// Set up event listeners
newGameBtn.addEventListener('click', startNewGame);
solveBtn.addEventListener('click', solveGame);
hintBtn.addEventListener('click', giveHint);
checkBtn.addEventListener('click', checkSolution);

difficultyBtns.forEach(btn => {
    btn.addEventListener('click', () => {
        difficultyBtns.forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        difficulty = btn.id;
    });
});

numberBtns.forEach(btn => {
    btn.addEventListener('click', () => {
        if (selectedCell && gameActive) {
            const row = parseInt(selectedCell.dataset.row);
            const col = parseInt(selectedCell.dataset.col);

            // Don't allow changing initial numbers
            if (selectedCell.classList.contains('initial')) {
                return;
            }

            if (btn.classList.contains('clear')) {
                selectedCell.textContent = '';
                currentPuzzle[row][col] = 0;
            } else {
                const num = parseInt(btn.textContent);
                selectedCell.textContent = num;
                currentPuzzle[row][col] = num;
            }

            // Check if this causes any errors
            validateBoard();

            // Check if puzzle is solved
            if (isPuzzleSolved()) {
                endGame(true);
            }
        }
    });
});

function initializeGrid() {
    grid.innerHTML = '';
    for (let i = 0; i < 9; i++) {
        for (let j = 0; j < 9; j++) {
            const cell = document.createElement('div');
            cell.classList.add('cell');
            cell.dataset.row = i;
            cell.dataset.col = j;
            cell.addEventListener('click', () => {
                if (!gameActive) return;

                // Remove selected class from previously selected cell
                if (selectedCell) {
                    selectedCell.classList.remove('selected');
                }

                // Set new selected cell
                selectedCell = cell;
                cell.classList.add('selected');
            });
            grid.appendChild(cell);
        }
    }
}

function startNewGame() {
    // Reset game state
    clearInterval(timerInterval);
    seconds = 0;
    updateTimer();
    status.textContent = 'Game started. Good luck!';
    gameActive = true;

    // Generate a new puzzle based on difficulty
    generatePuzzle();

    // Start the timer
    timerInterval = setInterval(updateTimer, 1000);
}

function updateTimer() {
    seconds++;
    const minutes = Math.floor(seconds / 60);
    const secs = seconds % 60;
    timerElement.textContent = `Time: ${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
}

function generatePuzzle() {
    // First, generate a solved puzzle
    solution = generateSolvedPuzzle();

    // Then remove numbers based on difficulty
    let cellsToRemove;
    switch (difficulty) {
        case 'easy':
            cellsToRemove = 30; // Leave ~51 numbers
            break;
        case 'medium':
            cellsToRemove = 45; // Leave ~36 numbers
            break;
        case 'hard':
            cellsToRemove = 55; // Leave ~26 numbers
            break;
        default:
            cellsToRemove = 30;
    }

    // Deep copy the solution
    puzzle = JSON.parse(JSON.stringify(solution));

    // Randomly remove cells
    for (let i = 0; i < cellsToRemove; i++) {
        let row, col;
        do {
            row = Math.floor(Math.random() * 9);
            col = Math.floor(Math.random() * 9);
        } while (puzzle[row][col] === 0);
        puzzle[row][col] = 0;
    }

    // Deep copy puzzle for current state
    currentPuzzle = JSON.parse(JSON.stringify(puzzle));

    // Render the puzzle
    renderPuzzle();
}

function renderPuzzle() {
    const cells = document.querySelectorAll('.cell');
    cells.forEach(cell => {
        cell.textContent = '';
        cell.classList.remove('initial', 'error', 'hint', 'selected');
    });

    for (let i = 0; i < 9; i++) {
        for (let j = 0; j < 9; j++) {
            const cellIndex = i * 9 + j;
            const cell = cells[cellIndex];
            if (puzzle[i][j] !== 0) {
                cell.textContent = puzzle[i][j];
                cell.classList.add('initial');
            }
        }
    }

    selectedCell = null;
}

function generateSolvedPuzzle() {
    // Create an empty 9x9 grid
    const grid = Array(9).fill().map(() => Array(9).fill(0));

    // Solve the empty grid
    if (solveSudoku(grid)) {
        return grid;
    }

    // Fallback to a hardcoded valid puzzle if solver fails
    return [
        [5, 3, 4, 6, 7, 8, 9, 1, 2],
        [6, 7, 2, 1, 9, 5, 3, 4, 8],
        [1, 9, 8, 3, 4, 2, 5, 6, 7],
        [8, 5, 9, 7, 6, 1, 4, 2, 3],
        [4, 2, 6, 8, 5, 3, 7, 9, 1],
        [7, 1, 3, 9, 2, 4, 8, 5, 6],
        [9, 6, 1, 5, 3, 7, 2, 8, 4],
        [2, 8, 7, 4, 1, 9, 6, 3, 5],
        [3, 4, 5, 2, 8, 6, 1, 7, 9]
    ];
}

function solveSudoku(board) {
    // Find an empty cell
    const emptyCell = findEmptyCell(board);

    // If no empty cell is found, puzzle is solved
    if (!emptyCell) {
        return true;
    }

    const [row, col] = emptyCell;

    // Try each number 1-9
    for (let num = 1; num <= 9; num++) {
        if (isValid(board, row, col, num)) {
            // Place number if valid
            board[row][col] = num;

            // Recursively solve the rest of the puzzle
            if (solveSudoku(board)) {
                return true;
            }

            // If we get here, this number didn't work
            // Backtrack and try another number
            board[row][col] = 0;
        }
    }

    // No solution found with current configuration
    return false;
}

function findEmptyCell(board) {
    for (let i = 0; i < 9; i++) {
        for (let j = 0; j < 9; j++) {
            if (board[i][j] === 0) {
                return [i, j];
            }
        }
    }

    return null;
}

function isValid(board, row, col, num) {
    // Check row
    for (let i = 0; i < 9; i++) {
        if (board[row][i] === num) {
            return false;
        }
    }

    // Check column
    for (let i = 0; i < 9; i++) {
        if (board[i][col] === num) {
            return false;
        }
    }

    // Check 3x3 box
    const boxRow = Math.floor(row / 3) * 3;
    const boxCol = Math.floor(col / 3) * 3;

    for (let i = 0; i < 3; i++) {
        for (let j = 0; j < 3; j++) {
            if (board[boxRow + i][boxCol + j] === num) {
                return false;
            }
        }
    }

    return true;
}

function solveGame() {
    if (!gameActive) return;

    // Display the solution
    const cells = document.querySelectorAll('.cell');
    for (let i = 0; i < 9; i++) {
        for (let j = 0; j < 9; j++) {
            const cellIndex = i * 9 + j;
            const cell = cells[cellIndex];
            cell.textContent = solution[i][j];
            if (!cell.classList.contains('initial')) {
                cell.classList.add('hint');
            }
        }
    }

    endGame(false);
    status.textContent = 'Puzzle solved. Game over.';
}

function giveHint() {
    if (!gameActive) return;

    // Find a random empty or incorrect cell
    const emptyCells = [];
    for (let i = 0; i < 9; i++) {
        for (let j = 0; j < 9; j++) {
            if (currentPuzzle[i][j] !== solution[i][j]) {
                emptyCells.push([i, j]);
            }
        }
    }

    if (emptyCells.length === 0) {
        status.textContent = 'Puzzle is already solved!';
        return;
    }

    // Select a random empty cell
    const randomIndex = Math.floor(Math.random() * emptyCells.length);
    const [row, col] = emptyCells[randomIndex];

    // Update the cell with the correct number
    const cellIndex = row * 9 + col;
    const cell = document.querySelectorAll('.cell')[cellIndex];
    cell.textContent = solution[row][col];
    currentPuzzle[row][col] = solution[row][col];
    cell.classList.add('hint');

    status.textContent = 'Hint provided!';

    // Check if puzzle is solved after hint
    if (isPuzzleSolved()) {
        endGame(true);
    }
}

function checkSolution() {
    if (!gameActive) return;

    let errors = 0;
    const cells = document.querySelectorAll('.cell');

    // Clear all error markings
    cells.forEach(cell => cell.classList.remove('error'));

    // Check for errors in rows, columns, and boxes
    for (let i = 0; i < 9; i++) {
        const rowNums = new Set();
        const colNums = new Set();
        const boxNums = new Set();
        const rowCells = [];
        const colCells = [];
        const boxCells = [];

        for (let j = 0; j < 9; j++) {
            // Process row
            if (currentPuzzle[i][j] !== 0) {
                if (rowNums.has(currentPuzzle[i][j])) {
                    // Duplicate in row
                    const cell = cells[i * 9 + j];
                    cell.classList.add('error');
                } else {
                    rowNums.add(currentPuzzle[i][j]);
                }
                rowCells.push(i * 9 + j);
            }

            // Process column
            if (currentPuzzle[j][i] !== 0) {
                if (colNums.has(currentPuzzle[j][i])) {
                    // Duplicate in column
                    const cell = cells[j * 9 + i];
                    cell.classList.add('error');
                } else {
                    colNums.add(currentPuzzle[j][i]);
                }
                colCells.push(j * 9 + i);
            }

            // Process 3x3 box
            const boxRow = Math.floor(i / 3) * 3 + Math.floor(j / 3);
            const boxCol = (i % 3) * 3 + (j % 3);
            if (currentPuzzle[boxRow][boxCol] !== 0) {
                if (boxNums.has(currentPuzzle[boxRow][boxCol])) {
                    // Duplicate in box
                    const cell = cells[boxRow * 9 + boxCol];
                    cell.classList.add('error');
                } else {
                    boxNums.add(currentPuzzle[boxRow][boxCol]);
                }
                boxCells.push(boxRow * 9 + boxCol);
            }
        }
    }

    if (errors === 0) {
        status.textContent = 'No errors found. Keep going!';
    } else {
        status.textContent = `Found ${errors} error${errors > 1 ? 's' : ''}!`;
    }
}

function validateBoard() {
    const cells = document.querySelectorAll('.cell');

    // Clear all error markings
    cells.forEach(cell => cell.classList.remove('error'));

    // Check for errors in rows, columns, and boxes
    for (let i = 0; i < 9; i++) {
        const rowNums = new Set();
        const colNums = new Set();
        const boxNums = new Set();
        const rowCells = [];
        const colCells = [];
        const boxCells = [];

        for (let j = 0; j < 9; j++) {
            // Process row
            if (currentPuzzle[i][j] !== 0) {
                if (rowNums.has(currentPuzzle[i][j])) {
                    // Duplicate in row
                    const cell = cells[i * 9 + j];
                    cell.classList.add('error');
                } else {
                    rowNums.add(currentPuzzle[i][j]);
                }
                rowCells.push(i * 9 + j);
            }

            // Process column
            if (currentPuzzle[j][i] !== 0) {
                if (colNums.has(currentPuzzle[j][i])) {
                    // Duplicate in column
                    const cell = cells[j * 9 + i];
                    cell.classList.add('error');
                } else {
                    colNums.add(currentPuzzle[j][i]);
                }
                colCells.push(j * 9 + i);
            }

            // Process 3x3 box
            const boxRow = Math.floor(i / 3) * 3 + Math.floor(j / 3);
            const boxCol = (i % 3) * 3 + (j % 3);
            if (currentPuzzle[boxRow][boxCol] !== 0) {
                if (boxNums.has(currentPuzzle[boxRow][boxCol])) {
                    // Duplicate in box
                    const cell = cells[boxRow * 9 + boxCol];
                    cell.classList.add('error');
                } else {
                    boxNums.add(currentPuzzle[boxRow][boxCol]);
                }
                boxCells.push(boxRow * 9 + boxCol);
            }
        }
    }
}

function isPuzzleSolved() {
    // Check if all cells are filled correctly
    for (let i = 0; i < 9; i++) {
        for (let j = 0; j < 9; j++) {
            if (currentPuzzle[i][j] !== solution[i][j]) {
                return false;
            }
        }
    }

    return true;
}

function endGame(won) {
    gameActive = false;
    clearInterval(timerInterval);

    if (won) {
        const minutes = Math.floor(seconds / 60);
        const secs = seconds % 60;
        status.textContent = `Congratulations! You solved the puzzle in ${minutes}:${secs.toString().padStart(2, '0')}!`;
    }
}
