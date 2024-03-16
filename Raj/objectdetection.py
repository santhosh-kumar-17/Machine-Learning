import tensorflow as tf
import cv2
import numpy as np
import requests
from io import BytesIO

# Download the model locally
model_url = 'https://tfhub.dev/tensorflow/ssd_mobilenet_v2/coco/4'
model_path = tf.keras.utils.get_file('ssd_mobilenet_v2_coco', model_url + '?tf-hub-format=compressed')

# Load the COCO pre-trained MobileNetV2 model
model = tf.saved_model.load(model_path)

def detect_objects(image_path):
    # Read the image
    image = cv2.imread(image_path)
    image_np = np.expand_dims(image, axis=0)

    # Convert image to tensor
    input_tensor = tf.convert_to_tensor(image_np, dtype=tf.uint8)

    # Perform inference
    detections = model(input_tensor)

    # Extract information about detected objects
    boxes = detections['detection_boxes'].numpy()
    classes = detections['detection_classes'].numpy()
    scores = detections['detection_scores'].numpy()

    # Display the results (customize based on your needs)
    for i in range(len(boxes)):
        if scores[i] > 0.5:  # Adjust the confidence threshold as needed
            class_id = int(classes[i])
            class_name = f"Class {class_id}"
            box = boxes[i]

            print(f"Object: {class_name}, Confidence: {scores[i]}, Box: {box}")

# Replace 'path/to/your/image.jpg' with the path to your image file
image_path = '2d21d3ca-144b-4364-be92-4bfc2f80ee94.jpg'
detect_objects(image_path)
