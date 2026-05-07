from rembg import remove
from PIL import Image
import numpy as np


def remove_background(pil_image: Image.Image) -> np.ndarray:
    rgba = remove(pil_image)
    return np.array(rgba)
