from flask import Flask, request, jsonify

app = Flask(__name__)

class SudokuSolver:
    def is_safe(self, board, row, col, num):

        # Check if the number is already present in the current row
        if any(board[row][c] == num for c in range(9)):
            return False

        # Check if the number is already present in the current column
        if any(board[r][col] == num for r in range(9)):
            return False

        # Check if the number is already present in the current 3x3 subgrid
        box_row_start, box_col_start = 3 * (row // 3), 3 * (col // 3)
        for r in range(box_row_start, box_row_start + 3):
            for c in range(box_col_start, box_col_start + 3):
                if board[r][c] == num:
                    return False

        # If not in row, column, or subgrid, it's safe
        return True

    def solve_sudoku(self, board):
        for row in range(9):
            for col in range(9):
                if board[row][col] == 0:  # Find an empty cell
                    for num in range(1, 10):  # Try numbers 1-9
                        if self.is_safe(board, row, col, num):
                            board[row][col] = num
                            if self.solve_sudoku(board):  # Recursive call
                                return True
                            board[row][col] = 0  # Backtrack
                    return False  # No number can be placed
        return True  # All cells are filled; solved

solver = SudokuSolver()

@app.route('/Api/solve', methods=['POST'])
def solve_sudoku():
    input_board = request.json  # Get input board from request body
    board = [[0 if value is None else value for value in row] for row in input_board]

    if solver.solve_sudoku(board):
        solved_board = [[board[i][j] for j in range(9)] for i in range(9)]
        return jsonify(solved_board)
    else:
        return jsonify(None), 400

if __name__ == '__main__':
    app.run(debug=True)