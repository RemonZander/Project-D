from PIL import Image
import io
import base64
import os

#Shrinks an image down to 200 x 200 pixels, the side which has a shorter dimension gets filled with a background color (white default)
def square_image(image_bytes: bytes, user_id: int, fill_color=(255, 255, 255, 0)) -> base64:
    #open image
    im = Image.open(io.BytesIO(image_bytes))
    #x, y tuple
    x, y = im.size
    max_size = max(x, y)
    #create new image with size 200 x 200 and fill it with given color
    new_im = Image.new('RGB', (max_size, max_size), fill_color)
    #paste old image into the new one, y start position is 200 - x , 200 - y
    new_im.paste(im, (int((max_size - x) / 2), int((max_size - y) / 2)))
    #resize it down to 128 x 128 pixels
    resized_img = new_im.resize((128, 128))
    #save image
    resized_img.save(str(user_id) + ".png")
    with open(f"{user_id}.png", "rb") as f:
        encoded_string = base64.b64encode(f.read())
    try: os.remove(f"{user_id}.png")
    except: pass
    return encoded_string

#sample
if __name__ == "__main__":
    new_image = square_image('img.jpg') #NOTE: When running make sure there is an image called img with extension .jpg in same folder as module
    #new_image.show()
