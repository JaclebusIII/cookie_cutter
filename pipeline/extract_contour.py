import cv2
import numpy as np
from PIL import Image
from shapely.geometry import Polygon


def extract_largest_contour(
    rgba: np.ndarray,
    epsilon_factor: float = 0.002,
    alpha_threshold: int = 127,
    blur_radius: int = 5,
    close_kernel: int = 7,
) -> Polygon:
    alpha = rgba[:, :, 3]

    # blur_radius must be odd and >= 1
    r = max(1, int(blur_radius))
    if r % 2 == 0:
        r += 1
    blurred = cv2.GaussianBlur(alpha, (r, r), 0)
    _, binary = cv2.threshold(blurred, int(alpha_threshold), 255, cv2.THRESH_BINARY)

    k = max(1, int(close_kernel))
    if k % 2 == 0:
        k += 1
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (k, k))
    closed = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)

    contours, _ = cv2.findContours(closed, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)

    if not contours:
        raise ValueError("No contour found. Try an image with a clearer subject on a plain background.")

    largest_idx = max(range(len(contours)), key=lambda i: cv2.contourArea(contours[i]))

    perimeter = cv2.arcLength(contours[largest_idx], True)
    epsilon = epsilon_factor * perimeter
    approx = cv2.approxPolyDP(contours[largest_idx], epsilon, True)

    points = approx.reshape(-1, 2).tolist()
    if len(points) < 3:
        raise ValueError("Contour too simple after approximation. Try lowering the detail level.")

    return Polygon(points)


def draw_contour_preview(original: Image.Image, contour: Polygon) -> Image.Image:
    img = np.array(original.convert("RGB"))
    img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)

    # Dim the original image so the contour stands out
    img = (img * 0.4).astype(np.uint8)

    pts = np.array(list(contour.exterior.coords), dtype=np.int32).reshape((-1, 1, 2))

    # Filled teal region
    overlay = img.copy()
    cv2.fillPoly(overlay, [pts], color=(180, 160, 0))
    img = cv2.addWeighted(overlay, 0.35, img, 0.65, 0)

    # Bright outline
    cv2.polylines(img, [pts], isClosed=True, color=(0, 220, 180), thickness=3)

    # Vertex dots so it's clear how many points the simplified contour has
    for x, y in pts.reshape(-1, 2):
        cv2.circle(img, (int(x), int(y)), 4, (0, 255, 100), -1)

    return Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
