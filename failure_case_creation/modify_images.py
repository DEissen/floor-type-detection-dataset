from PIL import Image, ImageEnhance
import numpy as np

def change_brightness(image, min, max):
    
    random = np.random.uniform(min, max)
    applier = ImageEnhance.Brightness(image)
    modified_image = applier.enhance(random)
    return modified_image

def change_contrast(image, min, max):
    
    random = np.random.uniform(min, max)
    applier = ImageEnhance.Contrast(image)
    modified_image = applier.enhance(random)
    return modified_image

def change_sharpness(image, min, max):
    
    random = np.random.uniform(min, max)
    applier = ImageEnhance.Sharpness(image)
    modified_image = applier.enhance(random)
    return modified_image

if __name__ == "__main__":
    path = r"testdata\measurement_25_07__15_03\BellyCamLeft\Left_15_03_21_583.jpg"
    img = Image.open(path)

    # img.show()

    # mod1 = change_brightness(img, 1.75, 3)
    # mod1 = change_contrast(img, 2, 5)
    # mod1 = change_sharpness(img, 7, 10)
    # mod1.show()