"""
Sudoku CSP Solver

Uses:
  - Backtracking Search
  - Forward Checking (domain reduction after each assignment)
  - AC-3 (Arc Consistency Algorithm 3) for initial + ongoing propagation

Usage:
  python Code.py easy.txt
  python Code.py medium.txt
  python Code.py hard.txt
  python Code.py veryhard.txt

Input format:
  9 lines, each with 9 digits (0 = empty cell)
"""

import sys
import copy
from collections import deque


# Global counters for reporting

backtrack_calls = 0
backtrack_failures = 0


# 1. READING THE BOARD

def read_board(filename):
    """Read a 9x9 Sudoku board from a text file. Returns a list of 81 ints."""
    with open(filename) as f:
        lines = f.read().splitlines()
    board = []
    for line in lines:
        for ch in line.strip():
            board.append(int(ch))
    return board


def print_board(board):
    """Pretty-print the 9x9 board."""
    for r in range(9):
        if r % 3 == 0 and r != 0:
            print("------+-------+------")
        row = []
        for c in range(9):
            if c % 3 == 0 and c != 0:
                row.append("|")
            row.append(str(board[r * 9 + c]) if board[r * 9 + c] != 0 else ".")
        print(" ".join(row))


# 2. CSP SETUP

def get_peers(cell):
    """
    Return the set of all cells that share a row, column, or 3x3 box
    with 'cell'. These are the variables that cannot have the same value.
    """
    row, col = divmod(cell, 9)
    peers = set()

    # Same row
    for c in range(9):
        peers.add(row * 9 + c)

    # Same column
    for r in range(9):
        peers.add(r * 9 + col)

    # Same 3x3 box
    box_r, box_c = (row // 3) * 3, (col // 3) * 3
    for r in range(box_r, box_r + 3):
        for c in range(box_c, box_c + 3):
            peers.add(r * 9 + c)

    peers.discard(cell)   # A cell is not its own peer
    return peers


# Build peer lookup once (reused across calls)
PEERS = [get_peers(i) for i in range(81)]


def build_domains(board):
    """
    Create initial domains for all 81 cells.
    - Fixed cells get domain = {given_value}
    - Empty cells get domain = {1..9} minus values already in peers
    """
    domains = []
    for i, val in enumerate(board):
        if val != 0:
            domains.append({val})
        else:
            # Start with all digits and remove those used by peers
            used = {board[p] for p in PEERS[i] if board[p] != 0}
            domains.append(set(range(1, 10)) - used)
    return domains


# 3. AC-3 (ARC CONSISTENCY)

def ac3(domains):
    """
    Run AC-3 to enforce arc consistency across all cells.
    Returns False if any domain becomes empty (unsolvable state).
    Modifies domains in-place.
    """
    # Queue of arcs (Xi, Xj) — all pairs of peers
    queue = deque()
    for i in range(81):
        for j in PEERS[i]:
            queue.append((i, j))

    while queue:
        xi, xj = queue.popleft()

        if revise(domains, xi, xj):
            if len(domains[xi]) == 0:
                return False   # Domain wiped out → inconsistency

            # xi's domain changed → re-check all arcs (xk, xi)
            for xk in PEERS[xi]:
                if xk != xj:
                    queue.append((xk, xi))

    return True


def revise(domains, xi, xj):
    """
    Remove values from domains[xi] that have no support in domains[xj].
    In Sudoku, xi ≠ xj always, so remove any value v from xi's domain
    if xj's domain = {v} (xj is forced to v, so xi can't use v).
    Returns True if any value was removed.
    """
    revised = False
    if len(domains[xj]) == 1:
        # xj is forced to a single value
        forced = next(iter(domains[xj]))
        if forced in domains[xi]:
            domains[xi].discard(forced)
            revised = True
    return revised


# 4. FORWARD CHECKING

def forward_check(domains, cell, value):
    """
    After assigning 'value' to 'cell', remove 'value' from the domains
    of all peers. Return False if any peer's domain becomes empty.
    Returns a list of (peer, removed_value) for easy undo on backtrack.
    """
    pruned = []
    for peer in PEERS[cell]:
        if value in domains[peer]:
            domains[peer].discard(value)
            pruned.append((peer, value))
            if len(domains[peer]) == 0:
                return None   # Failure: a peer has no valid values left
    return pruned


def undo_pruning(domains, pruned):
    """Restore domains that were pruned during forward checking."""
    for (peer, value) in pruned:
        domains[peer].add(value)


# 5. VARIABLE & VALUE ORDERING

def select_unassigned_variable(domains, assigned):
    """
    MRV (Minimum Remaining Values) heuristic:
    Pick the unassigned cell with the smallest domain.
    Ties broken by cell index (top-left first).
    """
    best = None
    best_size = float('inf')
    for i in range(81):
        if i not in assigned:
            size = len(domains[i])
            if size < best_size:
                best_size = size
                best = i
    return best


def order_domain_values(domains, cell):
    """Return domain values in sorted order (simple, predictable)."""
    return sorted(domains[cell])



# 6. BACKTRACKING SEARCH

def backtrack(domains, assigned):
    """
    Recursive backtracking search with forward checking.
    Returns a completed assignment dict {cell: value} or None on failure.
    """
    global backtrack_calls, backtrack_failures
    backtrack_calls += 1

    # Base case: all 81 cells assigned → solution found
    if len(assigned) == 81:
        return assigned

    # Choose next variable using MRV
    cell = select_unassigned_variable(domains, assigned)
    if cell is None:
        return assigned

    for value in order_domain_values(domains, cell):
        # Try assigning value to cell
        assigned[cell] = value
        saved_domain = set(domains[cell])
        domains[cell] = {value}

        # Forward checking: propagate to peers
        pruned = forward_check(domains, cell, value)

        if pruned is not None:
            # Optionally run AC-3 after assignment for stronger propagation
            domains_copy = [set(d) for d in domains]
            if ac3(domains_copy):
                result = backtrack(domains_copy, dict(assigned))
                if result is not None:
                    return result

        # Undo this assignment (backtrack)
        backtrack_failures += 1
        del assigned[cell]
        domains[cell] = saved_domain
        if pruned is not None:
            undo_pruning(domains, pruned)

    return None   # All values tried, none worked


# 7. MAIN SOLVE FUNCTION

def solve(filename):
    global backtrack_calls, backtrack_failures
    backtrack_calls = 0
    backtrack_failures = 0

    # print(f"\n{'='*40}")
    print()
    print(f"Solving: {filename}")
    print('='*30)

    board = read_board(filename)

    print("\nInitial board:")
    print_board(board)

    # Build CSP domains
    domains = build_domains(board)

    # Run AC-3 first to reduce domains before search
    if not ac3(domains):
        print("No solution exists (AC-3 detected inconsistency).")
        return

    # Build initial assignment from fixed cells
    assigned = {i: board[i] for i in range(81) if board[i] != 0}

    # Run backtracking search
    result = backtrack(domains, assigned)

    if result is None:
        print("No solution found.")
    else:
        # Reconstruct solved board
        solved_board = [result[i] for i in range(81)]
        print("\nSolved board:")
        print_board(solved_board)

    print(f"\nBacktrack() called:          {backtrack_calls}")
    print(f"Backtrack() returned failure: {backtrack_failures}")



# 8. ENTRY POINT

if __name__ == "__main__":
    # If no command-line arguments given (e.g. running from VS Code),
    # automatically solve all four puzzle files in the same folder.
    if len(sys.argv) < 2:
        default_files = ["easy.txt", "medium.txt", "hard.txt", "veryhard.txt"]

        for fname in default_files:
            solve(fname)
    else:
        # Or pass specific files: python sudoku_csp.py easy.txt
        for fname in sys.argv[1:]:
            solve(fname)