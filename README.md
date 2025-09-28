# QR Toolkit

This project implements a QR code reader and generator in Python, following these steps:

## Reading

1. **Image Preprocessing**  
   - OpenCV is used to read the image (e.g. `qr-code.png`) in grayscale.
   - The image is converted into a binary image (using a threshold), where the pixels have the value 0 (black) or 255 (white).

2. **Detection and Extraction of the QR Pattern**  
   - **Corner Detection (finder patterns):** The function `find_coordonates` identifies the characteristic areas of the QR code.
   - **Extracting the QR Matrix:** The function `get_qr` extracts the data from the image, building a matrix (2D list) in which each element is a module (0 or 1).
   - **Aligning the QR Code:** The function `positioned_qr` rotates and translates the matrix so that the QR code is correctly oriented, based on the detected coordinates.

3. **Removing the Data Mask**  
   - QR codes have a mask applied to avoid the appearance of unwanted patterns.
   - The function `get_mask_id` extracts the mask identifier.
   - The function `remove_mask` removes the applied mask, using a reserved matrix (calculated in `get_reserved_matrix` from `utils.py`) that indicates the functional areas that should not be affected.

4. **Decoding the Bitstream**  
   - The encoding type (Numeric, Alphanumeric, Byte, Kanji) is determined by analyzing some modules from the data area.
   - The length of the message is extracted and the bitstream is traversed according to the QR specifications, using a zig-zag reading that goes from right to left and top to bottom.
   - The function `get_message` interprets the obtained bitstream and decodes the final message.

5. **Error Correction**  
   - If the error correction level is different from "L", the function `correct_bitstream` applies the Reed–Solomon algorithm (using the `reedsolo` library) to repair any errors in the bitstream.
   - The bitstream is padded with zeros so that its length is a multiple of 8, converted into codewords (groups of 8 bits), corrected, and the result is reconverted into a binary string for further decoding.

By combining these steps, the project processes the entire QR code workflow: from reading the image, preprocessing, extracting and aligning the data, removing the applied mask, performing error correction (if necessary) and finally decoding the final message.

## Generation

1. **Encoding the Message**  
    The process starts with the function `encode` from `matrix_to_hoto.py`, which receives the message as input and generates a binary string that complies with the QR specifications:
    - The mode indicator is added (for Byte mode, "0100" is used).
    - The length of the character count field is calculated, choosing 8, 16 or 24 bits depending on the length of the message.
    - Each character is assigned its binary form on 8 bits.
    - A terminator field ("0000") is added and, subsequently, zeros are added so that the length of the string is a multiple of 8.

2. **Error Correction with Reed–Solomon**  
    After the initial encoding, error correction is applied:
    - The function `encode_rs` converts the binary string into an array of bytes (each group of 8 bits becomes a byte).
    - For the total number of correction bytes (which is entered via the console), an object from the `reedsolo.RSCodec` library is instantiated.
    - The message (represented as an array of bytes) is further encoded, adding correction symbols.
    - The result is reconverted into a binary string completed with the check codes.

3. **Applying the Data Mask**  
    In other parts of the project (`mask.py`), the QR mask is managed. Here, the reserved functional areas (such as localization points and synchronization zones) are removed using a reserved matrix, defined in `utils.py`. The masks are designed to avoid the appearance of unwanted patterns in the final matrix.

4. **Building the QR Matrix**  
    After obtaining a complete binary string (with initial encoding and error correction) and after applying the mask, a 2D matrix is built. Each element represents a module (or dot), 0 for white and 1 for black. The integration of the functional areas and orientation signals is done according to the QR specifications.

5. **Generating the QR Image**  
    The final step is converting the 2D matrix into an image. This is done using the `matplotlib` library (imported at the beginning of `matrix_to_hoto.py`). The specific functions handle:
    - Rendering a visual grid, where the modules have contrasting colors (black and white).
    - Saving the final image which represents the QR code ready for scanning.

By following these steps, the project ensures the correct generation of a QR code, from encoding the initial message to creating the final image.

---

References within the project:  
- Image preprocessing and reading: `__main__.py`  
- Extraction and positioning of the QR matrix: `read.py`  
- Removing the mask: `mask.py`  
- Decoding the message: `decode.py`  
- Error correction: `correction.py`  
- Marking reserved areas: `utils.py`  
- QR Generation: `matrix_to_hoto.py`

Libraries used in this project:
- OpenCV (cv): used for image reading (`__main__.py`, `read.py`)
- Matplotlib: used for rendering and saving the QR image (`matrix_to_hoto.py`)
- Reedsolo: used for error correction with the Reed-Solomon algorithm

---

### How to Use

1. Run the file `__main__.py`
2. Enter **0** for reading the code or **1** for generating one.
3. For reading, enter the filename with the QR code image (including the extension .png/.jpg/etc)  
   For generation, enter the desired message.
4. For generation, enter the number of bytes for error correction.

---

The team that developed this project:
- Bâcă Ionut-Adelin (Group 132)
- Popa Radu-Stefan (Group 132)
- Popescu Iulia-Maria (Group 131)

### Bibliography
- https://www.nayuki.io/page/creating-a-qr-code-step-by-step
- https://www.thonky.com/qr-code-tutorial/format-version-information
- https://medium.com/@r00__/decoding-a-broken-qr-code-39fc3473a034
- https://www.thonky.com/qr-code-tutorial/data-encoding
- https://www.thonky.com/qr-code-tutorial/module-placement-matrix
- https://qr.blinry.org/
- https://www.thonky.com/qr-code-tutorial/data-analysis
- https://www.youtube.com/watch?v=pamazHwk0hg
- https://www.youtube.com/watch?v=KMsvtqQqz5g
- https://www.youtube.com/watch?v=sRgUrKWiXQs
