"""
function for DALLE Jina Backend: https://github.com/jina-ai/dalle-flow
"""
from docarray import Document
import datetime
from PIL import Image
import base64
from io import BytesIO
import os
from dotenv import load_dotenv

load_dotenv()
DALLE_URL = os.environ["DALLE_URL"]

# Image to base64 string
def img_to_base64(image):
    buffered = BytesIO()
    image.save(buffered, format="JPEG")
    img_str = base64.b64encode(buffered.getvalue())
    return img_str


def base64_to_img(img_str):
    img_data = base64.b64decode(img_str)
    img = Image.open(BytesIO(img_data))
    return img


def get_images_from_dalle(prompt, num_images=1):
    now = datetime.datetime.now()
    da = (
        Document(text=prompt)
        .post(DALLE_URL, parameters={"num_images": num_images})
        .matches
    )

    # print elapsed time in sec
    print(
        "{} response in {}".format(da, (datetime.datetime.now() - now).total_seconds())
    )
    img_list = []

    for _d in da:
        _d.load_uri_to_image_tensor()
        _img = Image.fromarray(_d.tensor)
        # Return the first one
        return _img

    return None
