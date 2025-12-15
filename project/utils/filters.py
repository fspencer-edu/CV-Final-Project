import cv2
import numpy as np

def _gray(img):
    return cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) if img.ndim == 3 else img

def sobel(img):
    return cv2.Sobel(_gray(img), cv2.CV_64F, 1, 1, ksize=3)

def laplace(img):
    return cv2.Laplacian(_gray(img), cv2.CV_64F)

def sharpen(img):
    K = np.array([[0,-1,0],[-1,5,-1],[0,-1,0]])
    return cv2.filter2D(img, -1, K)

def binary_threshold(img, t=128, maxv=255):
    _, b = cv2.threshold(_gray(img), t, maxv, cv2.THRESH_BINARY)
    return b
