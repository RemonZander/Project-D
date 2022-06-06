"""MODULE TO VALIDATE IMAGE"""
def validate_image(uploaded_image):
    if not check_file_type(uploaded_image.filename):
        return False
    return True
    # Add functional code to process image

def check_file_type(filename, accepted_file_types = [".png", ".jpg", ".jpeg"]):
    for type in accepted_file_types:
        if filename.endswith(type):
            return True
    return False