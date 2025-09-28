import cv2

from read import *
from mask import *
from decode import *
from matrix_to_photo import *

action_id = int(input("Enter the action id(0 for reading | 1 for generating): "))

if action_id == 0:
    img_name = input("Enter the image file name(must be in currect path): ")

    img = cv2.imread(img_name, cv2.IMREAD_GRAYSCALE)
    height, width = img.shape # dimensions of the image

    _, binary_img = cv2.threshold(img, 127, 255, cv2.THRESH_BINARY)
    # Now binary_img is either 0 (black) or 255 (white)

    finder_patterns_coords = find_coordonates(binary_img, height, width)

    qr = positioned_qr(get_qr(binary_img, height, width), binary_img, height, width)
    mask_id = get_mask_id(qr)
    unmasked_qr = remove_mask(qr, mask_id)
    
    encoding_type = get_encoding_type(unmasked_qr)
    correction_level = get_correction_level(unmasked_qr)
    message = get_message(unmasked_qr, encoding_type, correction_level)

    print(message)
elif action_id == 1:
    message=input("Message: ") #The input that will be made a QR code
    make_matrix_before_mask(message)

