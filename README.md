# Sudoku-CSP-Solver
🧩 Sudoku CSP Solver

A Python-based Sudoku solver that uses classical AI techniques from 
Constraint Satisfaction Problems (CSP) to solve puzzles of varying 
difficulty levels (Easy, Medium, Hard, Very Hard).

🔧 Techniques Used:
-> AC-3 (Arc Consistency Algorithm 3) — for initial domain pruning
-> Backtracking Search — systematic trial and error
-> MRV Heuristic (Minimum Remaining Values) — smart cell selection
-> Forward Checking — early failure detection

Input: Plain text .txt files representing 9x9 Sudoku boards
Output: Solved board + backtrack call/failure statistics
