# app/utils/image_utils.py
import base64


def image_file_limit(base64_image: str, limit: int) -> bool:
    """
    Limit the image file size to a certain limit
    :param base64_image: base64 image string
    :param limit: limit in bytes
    :return: boolean is the image size is within the limit
    """
    image = base64.b64decode(base64_image)
    if len(image) > limit:
        return False
    return True
