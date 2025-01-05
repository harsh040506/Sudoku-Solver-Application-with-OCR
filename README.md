# Sudoku Solver with Pytesseract

This Python application allows users to upload an image of a Sudoku puzzle and get the solution displayed within a minute. The application runs locally, making it fully functional offline. It has been built using Python 3.10 and leverages the power of Pytesseract for OCR (Optical Character Recognition).

## Features
- Upload an image of a Sudoku puzzle.
- Automatically recognizes and solves the Sudoku puzzle.
- Displays the solution within a minute.
- Includes a sample image and its solution for testing.
- Runs locally, ensuring privacy and offline usability.

## Prerequisites
- Python 3.10
- pip (Python package manager)

## Installation
1. Clone this repository or download the source code.
   ```bash
   git clone https://github.com/harsh040506/Sudoku-Solver-Application-with-OCR
   cd sudoku_solver
   ```

2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Ensure that Tesseract OCR is installed on your system. For installation instructions, refer to [Tesseract OCR installation](https://github.com/tesseract-ocr/tesseract).

4. Verify that the `tesseract` command is accessible from your terminal or shell.

## Usage
1. Run the application:
   ```bash
   python Application.py
   ```

2. Open your browser and navigate to:
   ```
   http://localhost:5000/
   ```

3. Upload an image of a Sudoku puzzle (or use the provided sample image). The solution will be displayed within a minute.

## Sample Image
A sample image of a Sudoku puzzle is included in the package under the `sample_data` directory. You can use this image for testing:

- `sample_data/sudoku_image.png` (Input image)
- `sample_data/sudoku_solution.png` (Corresponding solution)

## How It Works
1. The user uploads an image of a Sudoku puzzle.
2. The application uses Pytesseract to extract the numbers from the puzzle.
3. A backtracking algorithm solves the puzzle.
4. The solution is displayed on the browser interface.

## Dependencies
- Python 3.10
- Flask (for the web interface)
- Pytesseract (OCR for extracting numbers from the puzzle image)
- OpenCV (for image preprocessing)
- Numpy (for handling the Sudoku grid)

## Notes
- Ensure that Tesseract OCR is correctly installed and configured for optimal performance.
- The application is designed to handle standard 9x9 Sudoku puzzles.

## License
This project is licensed under the MIT License. See the `LICENSE` file for details.

## Author
Developed by Harsh Chhajer
