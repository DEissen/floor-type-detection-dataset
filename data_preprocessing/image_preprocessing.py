from PIL import ImageFile, Image
# allow truncated images for PIL to process
ImageFile.LOAD_TRUNCATED_IMAGES = True

def image_crop(image, config_dict):
    """
        Method to crop all images in data_dict according to the config from config_dict.

        Parameters:
            - image (PIL.Image): Image to crop
            - config_dict (dict): Dict containing configuration for cropping

        Returns:
            - image (PIL.Image): Image after cropping is applied.
    """
    # transform only needed for cameras, other data shall stay unchanged
    # get values for new top, ... for cropping
    new_top = int(config_dict["crop_top"])
    new_bottom = int(
        config_dict["crop_bottom"])
    new_left = int(config_dict["crop_left"])
    new_right = int(
        config_dict["crop_right"])

    # replace image in sample dict with cropped image
    image = image.crop(
        (new_left, new_top, new_right, new_bottom))

    return image

def image_rescale(image, config_dict):
    """
        Method to rescale all images in data_dict according to the config from config_dict.

        Parameters:
            - image (PIL.Image): Image to rescale
            - config_dict (dict): Dict containing configuration for rescaling

        Returns:
            - image (PIL.Image): Image after rescaling is applied.
    """
    # get new target heigth and width from config dict
    new_h = int(config_dict["final_height"])
    new_w = int(config_dict["final_width"])

    # replace image in sample dict with resized image
    image = image.resize((new_w, new_h))

    return image