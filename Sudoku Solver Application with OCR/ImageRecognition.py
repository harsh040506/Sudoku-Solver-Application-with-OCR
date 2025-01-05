# import cv2
# import numpy as np
# import imutils
# from skimage.segmentation import clear_border
# import pytesseract
#
# tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
# pytesseract.pytesseract.tesseract_cmd = tesseract_cmd
#
# def preprocess_image(image_path):
#     """
#     Preprocesses the input image to isolate the Sudoku grid.
#     """
#     try:
#         image = cv2.imread(image_path)
#         if image is None:
#             print(f"Error: Could not read image at {image_path}")
#             return None, None
#         gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
#         blurred = cv2.GaussianBlur(gray, (5, 5), 0)
#         thresh = cv2.adaptiveThreshold(blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 2)
#
#         thresh = clear_border(thresh)
#
#         contours = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
#         contours = imutils.grab_contours(contours)
#         contours = sorted(contours, key=cv2.contourArea, reverse=True)
#         puzzle_contour = None
#
#         for contour in contours:
#             perimeter = cv2.arcLength(contour, True)
#             approx = cv2.approxPolyDP(contour, 0.02 * perimeter, True)
#             if len(approx) == 4:
#                 puzzle_contour = approx
#                 break
#         if puzzle_contour is None:
#             print("Error: Could not find the Sudoku grid in the image.")
#             return None, None
#
#
#         puzzle_contour = puzzle_contour.reshape(4, 2)
#         rect = np.zeros((4, 2), dtype="float32")
#
#         s = puzzle_contour.sum(axis=1)
#         rect[0] = puzzle_contour[np.argmin(s)]
#         rect[2] = puzzle_contour[np.argmax(s)]
#
#         diff = np.diff(puzzle_contour, axis=1)
#         rect[1] = puzzle_contour[np.argmin(diff)]
#         rect[3] = puzzle_contour[np.argmax(diff)]
#
#         (tl, tr, br, bl) = rect
#         width_a = np.sqrt(((br[0] - bl[0]) ** 2) + ((br[1] - bl[1]) ** 2))
#         width_b = np.sqrt(((tr[0] - tl[0]) ** 2) + ((tr[1] - tl[1]) ** 2))
#         max_width = max(int(width_a), int(width_b))
#
#         height_a = np.sqrt(((tr[0] - br[0]) ** 2) + ((tr[1] - br[1]) ** 2))
#         height_b = np.sqrt(((tl[0] - bl[0]) ** 2) + ((tl[1] - bl[1]) ** 2))
#         max_height = max(int(height_a), int(height_b))
#
#         dst = np.array([
#             [0, 0],
#             [max_width - 1, 0],
#             [max_width - 1, max_height - 1],
#             [0, max_height - 1]], dtype="float32")
#
#         transform = cv2.getPerspectiveTransform(rect, dst)
#         warped = cv2.warpPerspective(gray, transform, (max_width, max_height))
#
#         return warped, image
#
#     except Exception as e:
#         print(f"Error during preprocessing: {e}")
#         return None, None
#
# def extract_digits(warped_image):
#     """Extracts each digit/empty cell from the warped Sudoku grid
#     and returns the sudoku grid array with recognized digits."""
#     try:
#         rows = np.array_split(warped_image, 9)
#         grid_array = []
#
#         for row in rows:
#             cols = np.array_split(row, 9, axis=1)
#             row_array = []
#             for cell in cols:
#                 # Resize cell to make OCR more consistent.
#                 cell = cv2.resize(cell, (28, 28), interpolation=cv2.INTER_AREA)
#                 # Apply threshold for better OCR
#                 _, cell_thresh = cv2.threshold(cell, 128, 255, cv2.THRESH_BINARY_INV)
#
#                 # Use Tesseract OCR to recognize the digit in the cell.
#                 digit = pytesseract.image_to_string(cell_thresh, config='--psm 10 --oem 3 digits')
#
#                 digit = digit.strip()
#                 if digit.isdigit():
#                     row_array.append(int(digit))
#                 else:
#                     row_array.append(0)  # Empty cell
#
#             grid_array.append(row_array)
#         return grid_array
#     except Exception as e:
#         print(f"Error extracting digits: {e}")
#         return None
#
# if __name__ == '__main__':
#     image_path = input("Enter the path to the Sudoku image: ")
#     warped_img, original_img = preprocess_image(image_path)
#
#     if warped_img is not None:
#         sudoku_array = extract_digits(warped_img)
#         if sudoku_array is not None:
#             # print("Recognized Sudoku Grid:")
#             print("[")
#             for i, row in enumerate(sudoku_array):
#                 if i == len(sudoku_array) - 1:
#                     print(f"  {row}")  # Last row without comma
#                 else:
#                     print(f"  {row},")  # Add comma for other rows
#             print("]")
#         else:
#             print("Failed to convert image into sudoku array.")
#     else:
#         print("Failed to preprocess image.")

from flask import Flask, request, jsonify
import cv2
import numpy as np
import imutils
from skimage.segmentation import clear_border
import pytesseract
import os

app = Flask(__name__)

tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
pytesseract.pytesseract.tesseract_cmd = tesseract_cmd

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

@app.route('/upload', methods=['POST'])
def upload_image():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    file_path = os.path.join('uploads', file.filename)
    os.makedirs('uploads', exist_ok=True)
    file.save(file_path)

    warped_img, _ = preprocess_image(file_path)
    if warped_img is None:
        return jsonify({'error': 'Failed to preprocess the image'}), 400

    sudoku_array = extract_digits(warped_img)
    if sudoku_array is None:
        return jsonify({'error': 'Failed to extract Sudoku digits'}), 400

    os.remove(file_path)  # Cleanup uploaded file
    return jsonify(sudoku_array)
    # return jsonify({'sudoku_grid': sudoku_array})

if __name__ == '__main__':
    app.run(debug=True)