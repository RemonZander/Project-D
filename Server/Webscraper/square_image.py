from PIL import Image

#Shrinks an image down to 200 x 200 pixels, the side which has a shorter dimension gets filled with a background color (white default)
def square_image(image_path_name, fill_color=(255, 255, 255, 0)):
    #open image
    im = Image.open(open(image_path_name, "rb"))
    #x, y tuple
    x, y = im.size
    max_size = max(x, y)
    #create new image with size 200 x 200 and fill it with given color
    new_im = Image.new('RGB', (max_size, max_size), fill_color)
    #paste old image into the new one, y start position is 200 - x , 200 - y
    new_im.paste(im, (int((max_size - x) / 2), int((max_size - y) / 2)))
    #resize it down to 200 x 200 pixels
    resized_img = new_im.resize((200, 200))
    #save image
    resized_img.save(image_path_name, "jpeg")
    #return resized_img
    return new_im

#sample
if __name__ == "__main__":
    new_image = square_image('img.jpg') #NOTE: When running make sure there is an image called img with extension .jpg in same folder as module
    #new_image.show()
