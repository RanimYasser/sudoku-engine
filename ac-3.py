
from colorama import Fore, Style

class ArcConsistency:
    def __init__(self, grid):
        self.grid = grid
        self.variables = {}
        self.arcs = []


    def represent_as_CSP(self):
        self.variables = {
            (row, col): {self.grid[row][col]} if self.grid[row][col] != 0 else set(range(1, 10))
            for row in range(9) for col in range(9)
        }

    def define_arcs(self):
        """
        @brief Define arcs for Sudoku (row, column, and box constraints).
        """
        for row in range(9):
            for col in range(9):
                print(f"\nCell: ({row}, {col})")
                print("row constraints\n")
                for i in range(9):
                    if i != col:
                        self.arcs.append(((row, col), (row, i)))  # Row constraint
                        print(f"{Fore.RED}Row Arc: {((row, col), (row, i))}{Style.RESET_ALL}")
                print("column constraints\n")
                for i in range(9):
                    if i != row:
                        self.arcs.append(((row, col), (i, col)))  # Column constraint
                        print(f"{Fore.BLUE}Column Arc: {((row, col), (i, col))}{Style.RESET_ALL}")
                print("box constraints\n")
                box_row, box_col = 3 * (row // 3), 3 * (col // 3)
                for r in range(box_row, box_row + 3):
                    for c in range(box_col, box_col + 3):
                        if (r, c) != (row, col):
                            self.arcs.append(((row, col), (r, c)))  # Box constraint
                            print(f"{Fore.GREEN}Box Arc: {((row, col), (r, c))}{Style.RESET_ALL}")
                print("\n")

    def initial_domain_reduction(self):
        for (row, col), domain in self.variables.items():
            if len(domain) == 1:
                value = next(iter(domain))
                for neighbor in self.get_neighbors(row, col):
                    self.variables[neighbor].discard(value)

    def apply_arc_consistency(self):
        self.represent_as_CSP()
        self.define_arcs()
        self.initial_domain_reduction()
        queue = self.arcs[:]
        while queue:
            (x1, x2) = queue.pop(0)
            if self.revise(x1, x2):
                if len(self.variables[x1]) == 0:
                    return False  # Inconsistent
                print(f"Domain of {x1} revised: {self.variables[x1]}")
                for neighbor in self.get_neighbors(x1[0], x1[1]):
                    if neighbor != x2:
                        queue.append((neighbor, x1))
        return True

    def revise(self, x1, x2):
        revised = False
        for value in list(self.variables[x1]):
            if all(value == val for val in self.variables[x2]):
                self.variables[x1].remove(value)
                revised = True
        return revised

    def update_sudoku_grid(self):
        for (row, col), domain in self.variables.items():
            if len(domain) == 1:
                self.grid[row][col] = next(iter(domain))

    def get_neighbors(self, row, col):
        neighbors = set()
        for i in range(9):
            if i != col:
                neighbors.add((row, i))  # Row neighbors
            if i != row:
                neighbors.add((i, col))  # Column neighbors
        box_row, box_col = 3 * (row // 3), 3 * (col // 3)
        for r in range(box_row, box_row + 3):
            for c in range(box_col, box_col + 3):
                if (r, c) != (row, col):
                    neighbors.add((r, c))  # Box neighbors
        return neighbors
    
    def print_board(self):
        for row in range(9):
            if row % 3 == 0 and row != 0:
                print("-" * 21)  # Horizontal line after every 3 rows
            for col in range(9):
                if col % 3 == 0 and col != 0:
                    print("|", end=" ")  # Vertical line after every 3 columns
                # Print cell value or a placeholder for empty cells
                print(self.grid[row][col] if self.grid[row][col] != 0 else ".", end=" ")
            print()  # Move to the next line
board = [
    [5, 3, 0, 0, 7, 0, 0, 0, 0],
    [6, 0, 0, 1, 9, 5, 0, 0, 0],
    [0, 9, 8, 0, 0, 0, 0, 6, 0],
    [8, 0, 0, 0, 6, 0, 0, 0, 3],
    [4, 0, 0, 8, 0, 3, 0, 0, 0],
    [7, 0, 0, 0, 2, 0, 0, 0, 6],
    [0, 6, 0, 0, 0, 0, 2, 0, 0],
    [0, 0, 0, 0, 1, 9, 0, 0, 0],
    [0, 0, 0, 0, 8, 0, 0, 7, 0],
]

arc_cnsistency_solver=ArcConsistency(board)
arc_cnsistency_solver.apply_arc_consistency()
print("Arc Consistency Applied\n")
for (x,y),domain in arc_cnsistency_solver.variables.items():
    print(f"Domain of ({x},{y}): {domain}")
arc_cnsistency_solver.update_sudoku_grid()
arc_cnsistency_solver.print_board()