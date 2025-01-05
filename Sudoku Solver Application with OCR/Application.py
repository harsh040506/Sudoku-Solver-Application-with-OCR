from flask import Flask, request, jsonify, render_template_string
import cv2
import numpy as np
import imutils
from skimage.segmentation import clear_border
import pytesseract
import os

app = Flask(__name__)

# Configure Tesseract
tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
pytesseract.pytesseract.tesseract_cmd = tesseract_cmd

# Sudoku Solver Class
class SudokuSolver:
    def is_safe(self, board, row, col, num):
        if any(board[row][c] == num for c in range(9)):
            return False
        if any(board[r][col] == num for r in range(9)):
            return False
        box_row_start, box_col_start = 3 * (row // 3), 3 * (col // 3)
        for r in range(box_row_start, box_row_start + 3):
            for c in range(box_col_start, box_col_start + 3):
                if board[r][c] == num:
                    return False
        return True

    def solve_sudoku(self, board):
        for row in range(9):
            for col in range(9):
                if board[row][col] == 0:
                    for num in range(1, 10):
                        if self.is_safe(board, row, col, num):
                            board[row][col] = num
                            if self.solve_sudoku(board):
                                return True
                            board[row][col] = 0
                    return False
        return True

solver = SudokuSolver()

# Image Preprocessing
def preprocess_image(image_path):
    try:
        image = cv2.imread(image_path)
        if image is None:
            return None, None
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        thresh = cv2.adaptiveThreshold(blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 2)
        thresh = clear_border(thresh)
        contours = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        contours = imutils.grab_contours(contours)
        contours = sorted(contours, key=cv2.contourArea, reverse=True)
        puzzle_contour = None
        for contour in contours:
            perimeter = cv2.arcLength(contour, True)
            approx = cv2.approxPolyDP(contour, 0.02 * perimeter, True)
            if len(approx) == 4:
                puzzle_contour = approx
                break
        if puzzle_contour is None:
            return None, None
        puzzle_contour = puzzle_contour.reshape(4, 2)
        rect = np.zeros((4, 2), dtype="float32")
        s = puzzle_contour.sum(axis=1)
        rect[0] = puzzle_contour[np.argmin(s)]
        rect[2] = puzzle_contour[np.argmax(s)]
        diff = np.diff(puzzle_contour, axis=1)
        rect[1] = puzzle_contour[np.argmin(diff)]
        rect[3] = puzzle_contour[np.argmax(diff)]
        (tl, tr, br, bl) = rect
        width_a = np.sqrt(((br[0] - bl[0]) ** 2) + ((br[1] - bl[1]) ** 2))
        width_b = np.sqrt(((tr[0] - tl[0]) ** 2) + ((tr[1] - tl[1]) ** 2))
        max_width = max(int(width_a), int(width_b))
        height_a = np.sqrt(((tr[0] - br[0]) ** 2) + ((tr[1] - br[1]) ** 2))
        height_b = np.sqrt(((tl[0] - bl[0]) ** 2) + ((tl[1] - bl[1]) ** 2))
        max_height = max(int(height_a), int(height_b))
        dst = np.array([
            [0, 0],
            [max_width - 1, 0],
            [max_width - 1, max_height - 1],
            [0, max_height - 1]], dtype="float32")
        transform = cv2.getPerspectiveTransform(rect, dst)
        warped = cv2.warpPerspective(gray, transform, (max_width, max_height))
        return warped, image
    except Exception as e:
        return None, None

def extract_digits(warped_image):
    try:
        rows = np.array_split(warped_image, 9)
        grid_array = []
        for row in rows:
            cols = np.array_split(row, 9, axis=1)
            row_array = []
            for cell in cols:
                cell = cv2.resize(cell, (28, 28), interpolation=cv2.INTER_AREA)
                _, cell_thresh = cv2.threshold(cell, 128, 255, cv2.THRESH_BINARY_INV)
                digit = pytesseract.image_to_string(cell_thresh, config='--psm 10 --oem 3 digits')
                digit = digit.strip()
                if digit.isdigit():
                    row_array.append(int(digit))
                else:
                    row_array.append(0)
            grid_array.append(row_array)
        return grid_array
    except Exception as e:
        return None

@app.route('/')
def index():
    template = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
      <meta charset="UTF-8">
      <meta name="viewport" content="width=device-width, initial-scale=1.0">
      <title>Sudoku Solver</title>
      <link href="https://fonts.googleapis.com/css2?family=Urbanist:wght@400;500;700&display=swap" rel="stylesheet">
      <style>
        body {
          font-family: 'Urbanist', sans-serif;
          display: flex;
          justify-content: center;
          align-items: center;
          height: 100vh;
          margin: 0;
          background-color: #f4f4f9;
          overflow: auto;
        }

        .container {
          text-align: center;
          padding: 20px;
          border: 2px solid #ddd;
          border-radius: 10px;
          background-color: white;
          width: 100%;
          max-width: 450px;
          box-shadow: 0 0 15px rgba(0, 0, 0, 0.2);
        }

        h1 {
          font-size: 2.5em;
          margin-bottom: 20px;
          color: #333;
        }

        table {
          margin: 0 auto 20px;
          border-collapse: collapse;
          width: 100%;
          max-width: 360px;
        }

        td {
          padding: 0;
          border: 1px solid #ddd;
          text-align: center;
          width: 40px;
          height: 40px;
          position: relative;
        }

        td:nth-child(3), td:nth-child(6) {
          border-right: 3px solid #000;
        }

        tr:nth-child(3) td, tr:nth-child(6) td {
          border-bottom: 3px solid #000;
        }

        table#solved-sudoku-board {
            border: 3px solid #000; /* Outer border is already specified */
        }

        /* Additional style to make the outer border bolder */
        #solved-sudoku-board {
            border-width: 3px;
            border-color: black; /* Ensure outer border color is black */
        }

        input[type="text"] {
          width: calc(100% - 8px);
          height: calc(100% - 8px);
          text-align: center;
          font-size: 18px;
          font-weight: bold;
          color: #333;
          border: none;
          outline: none;
          background: none;
          position: absolute;
          top: 0;
          left: 0;
        }

        input[type="text"]:focus {
          border: 3px solid #4CAF50;
          border-radius: 3px;
          background-color: #e8f5e9;
        }

        button {
          padding: 12px 25px;
          font-size: 18px;
          cursor: pointer;
          margin-top: 20px;
          background-color: #4CAF50;
          color: white;
          border: none;
          border-radius: 5px;
          box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
          transition: background-color 0.3s, box-shadow 0.3s;
        }

        button:hover {
          background-color: #45a049;
          box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
        }

        .error-message {
          color: red;
          margin-top: 20px;
          font-size: 16px;
        }

        /* Style for Choose file button */
        input[type="file"] {
          font-family: 'Urbanist', sans-serif;
          font-size: 16px;
          padding: 10px;
          cursor: pointer;
          border: 2px solid #ddd;
          border-radius: 5px;
          background-color: #f4f4f9;
          color: #333;
          transition: background-color 0.3s;
        }

        input[type="file"]:hover {
          background-color: #e8f5e9;
        }
      </style>
    </head>
    <body>
    <div class="container">
      <h1>Sudoku Solver</h1>
      <form id="sudoku-form" enctype="multipart/form-data">
        <input type="file" id="image-file" accept="image/*" required>
        <button type="button" id="solve-button">Solve Sudoku</button>
      </form>
      <div id="solved-board" style="display: none;">
        <h2>Solved Sudoku:</h2>
        <table id="solved-sudoku-board">
          <tbody>
            <!-- Solved Sudoku grid will be inserted here -->
          </tbody>
        </table>
      </div>
      <p class="error-message" id="error-message"></p>
    </div>
    <script>
      document.getElementById("solve-button").addEventListener("click", async () => {
        const fileInput = document.getElementById("image-file");
        const errorMessage = document.getElementById("error-message");
        const solvedBoard = document.getElementById("solved-board");
        const solvedTable = document.getElementById("solved-sudoku-board").querySelector("tbody");
        errorMessage.textContent = "";
        solvedBoard.style.display = "none";

        if (!fileInput.files[0]) {
          errorMessage.textContent = "Please select an image file.";
          return;
        }

        const formData = new FormData();
        formData.append("file", fileInput.files[0]);

        try {
          const response = await fetch("/solve", {
            method: "POST",
            body: formData
          });

          if (response.ok) {
            const data = await response.json();
            if (data.error) {
              errorMessage.textContent = data.error;
            } else {
              solvedBoard.style.display = "block";
              solvedTable.innerHTML = "";
              data.board.forEach((row) => {
                const tr = document.createElement("tr");
                row.forEach((cell) => {
                  const td = document.createElement("td");
                  const input = document.createElement("input");
                  input.type = "text";
                  input.value = cell || "";
                  td.appendChild(input);
                  tr.appendChild(td);
                });
                solvedTable.appendChild(tr);
              });
            }
          } else {
            errorMessage.textContent = "An error occurred while solving the Sudoku.";
          }
        } catch (error) {
          errorMessage.textContent = "An error occurred while processing the image.";
        }
      });
    </script>
    </body>
    </html>
    """
    return render_template_string(template)

@app.route('/solve', methods=['POST'])
def solve():
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400

    file = request.files['file']
    file_path = os.path.join('uploads', file.filename)
    os.makedirs('uploads', exist_ok=True)
    file.save(file_path)

    warped, _ = preprocess_image(file_path)
    if warped is None:
        return jsonify({'error': 'Unable to process image for Sudoku board'}), 400

    grid = extract_digits(warped)
    if grid is None:
        return jsonify({'error': 'Unable to extract digits from the image'}), 400

    if not solver.solve_sudoku(grid):
        return jsonify({'error': 'No solution found for the Sudoku'}), 400
    return jsonify({'board': grid})

if __name__ == '__main__':
    app.run(debug=True)