import pygame
import sys
import numpy as np
from pygame.locals import *
from dokusan import generators
from colorama import Fore, Style

# Initialize Pygame
pygame.init()

# Constants
GRID_SIZE = 540
CELL_SIZE = GRID_SIZE // 9
SCREEN_WIDTH, SCREEN_HEIGHT = 600, 700
WHITE, BLACK, GRAY, PURPLE, RED, GREEN, LIGHT_BLUE = (
    (255, 255, 255), (0, 0, 0), (200, 200, 200), (128, 0, 128),
    (255, 0, 0), (0, 255, 0), (173, 216, 230)
)
FONT = pygame.font.Font(None, 40)
TITLE_FONT = pygame.font.Font(None, 60)
BUTTON_FONT = pygame.font.Font(None, 35)

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Sudoku Solver: Enhanced GUI")


# Arc Consistency
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
    def print_sudoku_grid(self):
                for row in self.grid:
                    print(" ".join(str(num) if num != 0 else "." for num in row))

    def apply_arc_consistency(self):
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
        self.update_sudoku_grid()
        self.print_sudoku_grid()
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
# Sudoku Game Logic
class SudokuGame:
    def __init__(self):
        self.board = [0] * 81
        self.original_board = [0] * 81  # Store the original board for reference

    def get_index(self, row, col):
        return row * 9 + col

    def get_row_col(self, index):
        return index // 9, index % 9

    def is_valid_insertion(self, index, num):
        row, col = self.get_row_col(index)
        for i in range(9):
            if self.board[self.get_index(row, i)] == num or self.board[self.get_index(i, col)] == num:
                return False

        start_row, start_col = 3 * (row // 3), 3 * (col // 3)
        for r in range(start_row, start_row + 3):
            for c in range(start_col, start_col + 3):
                if self.board[self.get_index(r, c)] == num:
                    return False
        return True

    def reset_board(self):
        self.board = [0] * 81

    def load_board(self, board):
        self.board = board[:]
        self.original_board = board[:]

    def insert_number(self, index, num):
        if self.is_valid_insertion(index, num):
            self.board[index] = num
            return True
        return False

    def remove_number(self, index):
        """Remove a number from the board at the given index."""
        self.board[index] = 0


# Backtracking Solver
class BacktrackingSolver:
    def __init__(self, game):
        self.game = game

    def solve(self):
        return self._backtrack(0)

    def _backtrack(self, index):
        if index == 81:
            return True
        if self.game.board[index] != 0:
            return self._backtrack(index + 1)

        for num in range(1, 10):
            if self.game.insert_number(index, num):
                if self._backtrack(index + 1):
                    return True
                self.game.remove_number(index)
        return False

    def random_board_generator(self, difficulty="medium"):
        difficulty_map = {"easy": 50, "medium": 100, "hard": 150}
        avg_rank = difficulty_map.get(difficulty, 100)
        generated_board = np.array(list(str(generators.random_sudoku(avg_rank=avg_rank)))).astype(int)
        self.game.load_board(generated_board.tolist())

    def find_all_solutions(self):
        """Find all valid solutions for the current board."""
        self.solutions = []
        self._backtrack_all(0)
        return self.solutions

    def _backtrack_all(self, index):
        if index == 81:
            self.solutions.append(self.game.board.copy())
            return

        if self.game.board[index] != 0:
            self._backtrack_all(index + 1)
            return

        for num in range(1, 10):
            if self.game.is_valid_insertion(index, num):
                self.game.insert_number(index, num)
                self._backtrack_all(index + 1)
                self.game.remove_number(index)


# Sudoku GUI
class SudokuGUI:
    def __init__(self, game, solver):
        self.game = game
        self.solver = solver
        self.selected_cell = None
        self.invalid_cells = set()
        self.solve_button = pygame.Rect(200, 600, 200, 50)
        self.reset_button = pygame.Rect(50, 600, 100, 50)

    def draw_grid(self):
        for row in range(10):
            line_width = 3 if row % 3 == 0 else 1
            pygame.draw.line(screen, BLACK, (0, row * CELL_SIZE), (GRID_SIZE, row * CELL_SIZE), line_width)
            pygame.draw.line(screen, BLACK, (row * CELL_SIZE, 0), (row * CELL_SIZE, GRID_SIZE), line_width)

    def draw_numbers(self):
        for row in range(9):
            for col in range(9):
                index = self.game.get_index(row, col)
                num = self.game.board[index]
                if num != 0:
                    color = RED if (row, col) in self.invalid_cells else BLACK
                    text = FONT.render(str(num), True, color)
                    x = col * CELL_SIZE + CELL_SIZE // 3
                    y = row * CELL_SIZE + CELL_SIZE // 4
                    screen.blit(text, (x, y))

    def draw_buttons(self):
        pygame.draw.rect(screen, PURPLE, self.solve_button, border_radius=8)
        solve_text = BUTTON_FONT.render("Solve", True, WHITE)
        screen.blit(solve_text, (self.solve_button.x + 50, self.solve_button.y + 10))

    def highlight_selected_cell(self):
        if self.selected_cell is not None:
            row, col = self.game.get_row_col(self.selected_cell)
            pygame.draw.rect(screen, LIGHT_BLUE, (col * CELL_SIZE, row * CELL_SIZE, CELL_SIZE, CELL_SIZE), 3)

    def select_cell(self, pos):
        x, y = pos
        if x < GRID_SIZE and y < GRID_SIZE:
            row, col = y // CELL_SIZE, x // CELL_SIZE
            if 0 <= row < 9 and 0 <= col < 9:
                self.selected_cell = self.game.get_index(row, col)

    def handle_keypress(self, key):
        if self.selected_cell is not None:
            num = key - pygame.K_0
            if 1 <= num <= 9:
                index = self.selected_cell
                if self.game.is_valid_insertion(index, num):
                    self.game.board[index] = num
                    self.invalid_cells.discard(self.game.get_row_col(index))
                else:
                    self.invalid_cells.add(self.game.get_row_col(index))
            elif key == pygame.K_BACKSPACE:
                index = self.selected_cell
                self.game.board[index] = 0
                self.invalid_cells.discard(self.game.get_row_col(index))


# Interactive Mode GUI
class InteractiveSudokuGUI(SudokuGUI):
    def __init__(self, game, solver):
        super().__init__(game, solver)
        self.valid_solutions = []

    def enable_interactive_mode(self):
        """Initialize interactive mode with all possible solutions."""
        self.valid_solutions = self.solver.find_all_solutions()
        print(f"Interactive mode: {len(self.valid_solutions)} possible solutions found.")

    def validate_user_move(self, index, num):
        """Check if the user's move matches any of the valid solutions."""
        for solution in self.valid_solutions:
            if solution[index] == num:
                return True
        return False

    def handle_keypress(self, key):
        if self.selected_cell is not None:
            num = key - pygame.K_0
            index = self.selected_cell
            if 1 <= num <= 9:
                if self.validate_user_move(index, num):
                    self.game.board[index] = num
                    self.invalid_cells.discard(self.game.get_row_col(index))
                else:
                    self.invalid_cells.add(self.game.get_row_col(index))
                    print("Invalid move! This number does not lead to a valid solution.")
            elif key == pygame.K_BACKSPACE:
                self.game.board[index] = 0
                self.invalid_cells.discard(self.game.get_row_col(index))


# Gradient Background
def draw_gradient_background():
    for i in range(SCREEN_HEIGHT):
        color = (200 - i // 4, 200 - i // 4, 255)
        pygame.draw.line(screen, color, (0, i), (SCREEN_WIDTH, i))


# Menus
def main_menu():
    title = TITLE_FONT.render("Sudoku Solver", True, BLACK)
    ai_button = pygame.Rect(150, 300, 300, 50)
    manual_button = pygame.Rect(150, 400, 300, 50)
    interactive_button = pygame.Rect(150, 500, 300, 50)

    while True:
        draw_gradient_background()
        screen.blit(title, (150, 150))

        pygame.draw.rect(screen, PURPLE, ai_button, border_radius=8)
        pygame.draw.rect(screen, PURPLE, manual_button, border_radius=8)
        pygame.draw.rect(screen, PURPLE, interactive_button, border_radius=8)

        ai_text = BUTTON_FONT.render("AI Generated Board", True, WHITE)
        manual_text = BUTTON_FONT.render("Manual Input Mode", True, WHITE)
        interactive_text = BUTTON_FONT.render("Interactive Mode", True, WHITE)

        screen.blit(ai_text, (ai_button.x + 20, ai_button.y + 10))
        screen.blit(manual_text, (manual_button.x + 20, manual_button.y + 10))
        screen.blit(interactive_text, (interactive_button.x + 20, interactive_button.y + 10))

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == MOUSEBUTTONDOWN:
                if ai_button.collidepoint(event.pos):
                    return "ai"
                elif manual_button.collidepoint(event.pos):
                    return "manual"
                elif interactive_button.collidepoint(event.pos):
                    return "interactive"

        pygame.display.update()


def ai_difficulty_menu(game):
    difficulties = {"Easy": 50, "Medium": 100, "Hard": 150}
    buttons = {difficulty: pygame.Rect(150, 300 + i * 70, 300, 50) for i, difficulty in enumerate(difficulties)}

    while True:
        draw_gradient_background()
        title = FONT.render("Select Difficulty", True, BLACK)
        screen.blit(title, (200, 200))

        for difficulty, rect in buttons.items():
            pygame.draw.rect(screen, PURPLE, rect, border_radius=8)
            text = BUTTON_FONT.render(difficulty, True, WHITE)
            screen.blit(text, (rect.x + 50, rect.y + 10))

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == MOUSEBUTTONDOWN:
                for difficulty, rect in buttons.items():
                    if rect.collidepoint(event.pos):
                        board = list(map(int, str(generators.random_sudoku(avg_rank=difficulties[difficulty]))))
                        if len(board) == 81:
                            game.load_board(board)
                        return

        pygame.display.update()


# Main Function
def main():
    game = SudokuGame()
    solver = BacktrackingSolver(game)
    mode = main_menu()

    if mode == "ai":
        ai_difficulty_menu(game)
        gui = SudokuGUI(game, solver)  # Initialize GUI for AI mode
    elif mode == "interactive":
        gui = InteractiveSudokuGUI(game, solver)
        board = list(map(int, str(generators.random_sudoku(avg_rank=100))))
        game.load_board(board)
        gui.enable_interactive_mode()
    else:
        gui = SudokuGUI(game, solver)  # Initialize GUI for manual mode

    running = True
    while running:
        draw_gradient_background()
        gui.draw_grid()
        gui.draw_numbers()
        gui.highlight_selected_cell()
        gui.draw_buttons()

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == MOUSEBUTTONDOWN:
                if gui.solve_button.collidepoint(event.pos):
                    solver.solve()
                else:
                    gui.select_cell(event.pos)
            if event.type == KEYDOWN:
                gui.handle_keypress(event.key)

        pygame.display.update()


if __name__ == "__main__":
    main()