import hashlib
import cv2
import numpy as np

def calculate_md5(image_path):
    with open(image_path, 'rb') as f:
        data = f.read()
    return hashlib.md5(data).hexdigest()

def compare_hashes(hash1, hash2):
    return hash1 == hash2

def detect_changes(original_img, test_img):
    original_gray = cv2.cvtColor(original_img, cv2.COLOR_BGR2GRAY)
    test_gray = cv2.cvtColor(test_img, cv2.COLOR_BGR2GRAY)
    diff = cv2.absdiff(original_gray, test_gray)
    _, thresh = cv2.threshold(diff, 30, 255, cv2.THRESH_BINARY)
    return thresh
