

#  Global counters to track backtrack calls and failures 
backtrack_calls = 0
backtrack_failures = 0


# STEP 1: Read the board from a text file

def read_board(filename):
    """
    Reads a 9x9 Sudoku board from a text file.
    Each line has 9 digits (0 = empty cell).
    Returns a 9x9 list of integers.
    """
    board = []
    with open(filename, 'r') as f:
        for line in f:
            line = line.strip()
            if line:  # skip empty lines
                row = [int(ch) for ch in line]
                board.append(row)
    return board



# Print the board in a readable 9x9 grid format
def print_board(board):
    """
    Prints the Sudoku board nicely with grid separators.
    """
    print("+-------+-------+-------+")
    for i in range(9):
        row_str = "| "
        for j in range(9):
            val = board[i][j]
            row_str += (str(val) if val != 0 else ".") + " "
            if j == 2 or j == 5:
                row_str += "| "
        row_str += "|"
        print(row_str)
        if i == 2 or i == 5:
            print("+-------+-------+-------+")
    print("+-------+-------+-------+")

#Setup domains for each cell

def setup_domains(board):
    """
    Creates a dictionary of domains for each cell (row, col).
    - If cell already has a value, domain = {that value}
    - If cell is empty (0), domain = {1, 2, ..., 9}
    """
    domains = {}
    for i in range(9):
        for j in range(9):
            if board[i][j] != 0:
                domains[(i, j)] = {board[i][j]}
            else:
                domains[(i, j)] = set(range(1, 10))
    return domains



# Get all neighbors  of a cell
def get_neighbors(row, col):
    """
    Returns a list of all cells that share a row, column,
    or 3x3 box with cell (row, col).
    These are the cells that CANNOT have the same value.
    """
    neighbors = set()

   
    for j in range(9):
        if j != col:
            neighbors.add((row, j))

  
    for i in range(9):
        if i != row:
            neighbors.add((i, col))

   
    box_row = (row // 3) * 3  # top-left row of the box
    box_col = (col // 3) * 3  # top-left col of the box
    for i in range(box_row, box_row + 3):
        for j in range(box_col, box_col + 3):
            if (i, j) != (row, col):
                neighbors.add((i, j))

    return list(neighbors)



#  Arc Consistency Algorithm 
def ac3(domains):
    """
    AC-3 reduces domains by removing values that can never
    satisfy the constraints (no two peers can have same value).

    It keeps a queue of arcs (pairs of cells that are neighbors).
    For each arc (Xi, Xj): remove values from Xi's domain that
    have no valid match in Xj's domain.

    Returns False if any domain becomes empty (unsolvable).
    Returns True if all arcs are consistent.
    """

    queue = []
    for i in range(9):
        for j in range(9):
            for neighbor in get_neighbors(i, j):
                queue.append(((i, j), neighbor))

    # Process the queue
    while queue:
        (xi, xj) = queue.pop(0)  # take first arc
        if revise(domains, xi, xj):
            # If domain became empty, puzzle is unsolvable
            if len(domains[xi]) == 0:
                return False
            # Add all neighbors of xi back to queue (re-check them)
            for neighbor in get_neighbors(xi[0], xi[1]):
                if neighbor != xj:
                    queue.append((neighbor, xi))

    return True


def revise(domains, xi, xj):
    """
    Removes values from domains[xi] that have no valid
    support in domains[xj].

    A value 'v' in Xi is invalid if every value in Xj equals 'v'
    (meaning Xi=v would conflict with all options of Xj).

    Returns True if any value was removed.
    """
    revised = False
    to_remove = set()

    for v in domains[xi]:
        # Check if there's at least one value in xj != v
        # If xj's entire domain is just {v}, then v is not valid for xi
        if domains[xj] == {v}:
            to_remove.add(v)
            revised = True

    domains[xi] -= to_remove
    return revised



#  Select next unassigned cell (MRV Heuristic)

def select_unassigned_cell(domains, board):
    """
    Picks the empty cell with the SMALLEST domain (fewest choices).
    This is called MRV (Minimum Remaining Values) heuristic.
    It helps find failures faster and reduces backtracking.
    """
    min_size = 10  # larger than max possible domain size
    best_cell = None

    for i in range(9):
        for j in range(9):
            if board[i][j] == 0:  # only consider empty cells
                size = len(domains[(i, j)])
                if size < min_size:
                    min_size = size
                    best_cell = (i, j)

    return best_cell

# STEP 7: Forward Checking
def forward_check(domains, row, col, value):
    """
    After assigning 'value' to cell (row, col),
    remove 'value' from all neighbors' domains.

    Returns False if any neighbor's domain becomes empty.
    Also returns the list of changes made (for undo later).
    """
    changes = []  

    for (ni, nj) in get_neighbors(row, col):
        if value in domains[(ni, nj)]:
            domains[(ni, nj)].remove(value)
            changes.append((ni, nj, value))

    
            if len(domains[(ni, nj)]) == 0:
                return False, changes

    return True, changes


def undo_forward_check(domains, changes):
    """
    Undoes the changes made during forward checking.
    This is called when we backtrack.
    """
    for (ni, nj, value) in changes:
        domains[(ni, nj)].add(value)


# STEP 8: Backtracking Search
def backtrack(board, domains):
    """
    Main backtracking function.
    - Picks an unassigned cell
    - Tries each value in its domain
    - Uses forward checking after each assignment
    - Recurses; if stuck, backtracks and tries next value
    """
    global backtrack_calls, backtrack_failures
    backtrack_calls += 1

    cell = select_unassigned_cell(domains, board)

    if cell is None:
        return True

    row, col = cell

    
    for value in sorted(domains[(row, col)]):  

       
        old_domain = domains[(row, col)].copy()

        # Assign the value
        board[row][col] = value
        domains[(row, col)] = {value}

        ok, changes = forward_check(domains, row, col, value)

        if ok:
            result = backtrack(board, domains)
            if result:
                return True  # Solution found!
            
        board[row][col] = 0
        domains[(row, col)] = old_domain
        undo_forward_check(domains, changes)

    # No value worked → failure
    backtrack_failures += 1
    return False


# Main solver function

def solve_sudoku(filename):
    """
    Full pipeline:
    1. Read board from file
    2. Setup domains
    3. Run AC-3 for initial pruning
    4. Run backtracking with forward checking
    5. Print results
    """
    global backtrack_calls, backtrack_failures

    # Reset counters for each puzzle
    backtrack_calls = 0
    backtrack_failures = 0

    print(f"\n{'='*50}")
    print(f"  Solving: {filename}")
    print(f"{'='*50}")

    # Read the board
    board = read_board(filename)

    print("\nInitial Board:")
    print_board(board)

    # Setup domains i.e possible values for each cell
    domains = setup_domains(board)

    # Run AC-3 to reduce domains before backtracking
    print("\nRunning AC-3 for initial constraint propagation...")
    ac3_result = ac3(domains)

    if not ac3_result:
        print("AC-3 determined this puzzle is UNSOLVABLE!")
        return

    # Run backtracking search
    print("Running Backtracking with Forward Checking...")
    solved = backtrack(board, domains)

    if solved:
        print("\nSolved Board:")
        print_board(board)
    else:
        print("\nNo solution found for this puzzle.")

    # Print statistics
    print(f"\n--- Statistics for {filename} ---")
    print(f"  BACKTRACK calls    : {backtrack_calls}")
    print(f"  BACKTRACK failures : {backtrack_failures}")

    return board



#  Run all four boards
if __name__ == "__main__":

    print("\n" + "#"*50)
    print("#     SUDOKU CSP SOLVER                          #")
    print("#     Using: AC-3 + Backtracking + Forward Check #")
    print("#"*50)

    # List of all four puzzle files
    puzzle_files = [
        "easy.txt",
        "medium.txt",
        "hard.txt",
        "veryhard.txt"
    ]

    # Solve each puzzle one by one
    for puzzle in puzzle_files:
        solve_sudoku(puzzle)

    print("\n" + "#"*50)
    print("#     All puzzles solved!                        #")
    print("#"*50)
