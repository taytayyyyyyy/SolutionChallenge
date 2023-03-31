from PIL import Image
from pytesseract import pytesseract

# Defining paths to tesseract.exe
# and the image we would be using
path_to_tesseract = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

def find_values(path : str):
    # image = Image.open("images\\test8.png")
    image = Image.open(path)
    img_gray = image.convert("L")
    img_gray.save("images\\test.png")
    image_path = r"images\\test.png"
    # r"read-text.png"
    
    # Opening the image & storing it in an image object
    img = Image.open(image_path)
    
    # Providing the tesseract executable
    # location to pytesseract library
    pytesseract.tesseract_cmd = path_to_tesseract
    
    # Passing the image object to image_to_string() function
    # This function will extract the text from the image
    text = pytesseract.image_to_string(img)
    
    # Displaying the extracted text
    # output_file = open("report.txt", "w")
    
    test = text.split("\n")
    test_values = {}
    for line in test:
        llist = list(line.split(" "))
        for entry in llist:
            if entry.isnumeric():
                # print(llist[0], entry)
                test_values[llist[0]] = entry
    return test_values
    
    
    # output_file.write(text[:-1])
    # output_file.close()

# find_values("images\\test9.png")