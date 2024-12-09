import cv2
import pytesseract

# Load the image
image_path = 'test_image.jpg'
image = cv2.imread(image_path)

# Configure Tesseract to recognize only digits
custom_config = r'--oem 3 --psm 6 -c tessedit_char_whitelist=0123456789'
detected_text = pytesseract.image_to_string(image, config=custom_config)

print("Detected Numbers:", detected_text)

# Optional: Draw bounding boxes
data = pytesseract.image_to_data(image, config=custom_config, output_type=pytesseract.Output.DICT)
for i in range(len(data['text'])):
    if data['text'][i].strip().isdigit():
        x, y, w, h = data['left'][i], data['top'][i], data['width'][i], data['height'][i]
        cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)
cv2.imshow('Detected Numbers', image)
cv2.waitKey(0)
