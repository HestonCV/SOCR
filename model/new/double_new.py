import easyocr
import cv2
import matplotlib.pyplot as plt

# Load the EasyOCR Reader
reader = easyocr.Reader(['en'], gpu=False)  # Use 'gpu=True' if you have a GPU available

# Load your image
image_path = 'model/data/test_image1.jpg'
image = cv2.imread(image_path)

# Perform OCR
results = reader.readtext(image_path)

# Draw bounding boxes and text on the image (only for numbers)
for (bbox, text, confidence) in results:
    # Filter: Display only numbers
    if text.isdigit():
        top_left = tuple(map(int, bbox[0]))
        bottom_right = tuple(map(int, bbox[2]))
        # Draw the rectangle
        cv2.rectangle(image, top_left, bottom_right, (0, 255, 0), 2)
        # Put the recognized number
        cv2.putText(image, text, (top_left[0], top_left[1] - 10), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

# Display the image with bounding boxes
image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)  # Convert to RGB for matplotlib
plt.imshow(image)
plt.axis('off')
plt.savefig('test_image_prediction')
