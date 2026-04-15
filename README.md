# Sudoku CSP Solver

A CSP-based Sudoku solver implemented in Python using **Backtracking Search**, **Forward Checking**, and **AC-3 (Arc Consistency Algorithm 3)**. Solves Sudoku puzzles of varying difficulty.

---

## Algorithms Used

- **AC-3** — Runs before and during search to reduce variable domains by enforcing arc consistency
- **Backtracking Search** — Recursively tries values and backtracks when a conflict is found
- **Forward Checking** — After each assignment, eliminates that value from all neighboring domains immediately
- **MRV Heuristic** — Always picks the variable with the fewest remaining values next (Minimum Remaining Values)

---

## How to Run

Make sure all `.txt` puzzle files are in the **same folder** as `Code.py`.

```bash
python Code.py
```

This will automatically solve all four puzzles: `easy.txt`, `medium.txt`, `hard.txt`, `veryhard.txt`.

You can also run a specific puzzle:

```bash
python Code.py easy.txt
```

---

## Input Format

Each puzzle file must have exactly 9 lines, each with exactly 9 digits (0 = empty cell).

**Example (`easy.txt`):**
```
004030050
609400000
005100489
000060930
300807002
026040000
453009600
000004705
090050200
```

---

## Results

| Board      | Backtrack() Called | Backtrack() Failures |
|------------|--------------------|----------------------|
| Easy       | 50                 | 0                    |
| Medium     | 52                 | 0                    |
| Hard       | 213                | 210                  |
| Very Hard  | 60                 | 0                    |

### Comments on Results

- **Easy & Medium** — Zero failures. AC-3 and forward checking were powerful enough to reduce domains and find the solution without any guessing.
- **Hard** — 210 failures occurred, meaning the puzzle was ambiguous enough that the solver had to genuinely backtrack and try different values multiple times.
- **Very Hard** — Surprisingly 0 failures, because AC-3 propagation alone was sufficient to narrow domains down to a single solution path.

---

## File Structure

```
├── Code.py          # Main CSP solver
├── easy.txt         # Easy Sudoku puzzle
├── medium.txt       # Medium Sudoku puzzle
├── hard.txt         # Hard Sudoku puzzle
├── veryhard.txt     # Very hard Sudoku puzzle
└── README.md        # This file
```

---

## Requirements

- Python 3.x
- No external libraries needed (uses only built-in `sys`, `copy`, `collections`)
