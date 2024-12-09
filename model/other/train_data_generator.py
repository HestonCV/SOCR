import numpy as np
import tensorflow as tf
import os
import cv2
import random
from pathlib import Path

class ObjectDetectionDataGenerator(tf.keras.utils.Sequence):
    def __init__(self, 
                 digit_images_path, 
                 background_images_path, 
                 batch_size, 
                 num_classes, 
                 image_size=(1024, 1024), 
                 min_objects=1, 
                 max_objects=10, 
                 shuffle=True, 
                 **kwargs):
        super().__init__(**kwargs)
        self.digit_images_path = digit_images_path
        self.background_images_path = background_images_path
        self.batch_size = batch_size
        self.num_classes = num_classes
        self.image_size = image_size
        self.min_objects = min_objects
        self.max_objects = max_objects
        self.shuffle = shuffle
        self.image_filenames = self._load_digit_images(digit_images_path)
        self.background_filenames = self._load_background_images(background_images_path)
        self.on_epoch_end()

    def _load_digit_images(self, path):
        # Load images from each digit folder (e.g., 0-9 folders within `digit_images_path`)
        images_by_label = {}
        for label in range(self.num_classes):
            label_dir = os.path.join(path, str(label))
            images_by_label[label] = list(Path(label_dir).glob("*.jpg"))
        return images_by_label

    def _load_background_images(self, path):
        # Load all background images
        return list(Path(path).glob("*.jpg"))

    def __len__(self):
        return int(np.ceil(len(self.background_filenames) / self.batch_size))

    def __getitem__(self, index):
        start_idx = index * self.batch_size
        end_idx = min((index + 1) * self.batch_size, len(self.background_filenames))
        batch_filenames = self.background_filenames[start_idx:end_idx]
        images, boxes, labels = self.__data_generation(batch_filenames)
        return images, {"boxes": boxes, "classes": labels}

    def on_epoch_end(self):
        if self.shuffle:
            np.random.shuffle(self.background_filenames)

    def __data_generation(self, batch_filenames):
        # Preallocate arrays
        images = np.zeros((len(batch_filenames), *self.image_size, 3), dtype=np.uint8)
        boxes = []
        labels = []
        print('testing')
        for i, bg_path in enumerate(batch_filenames):
            # Load and resize a random background image
            background = cv2.imread(str(bg_path))
            background = cv2.resize(background, self.image_size)
            canvas = background.copy()

            # Generate random objects
            num_objects = random.randint(self.min_objects, self.max_objects)
            used_locations = []  # Track placed bounding boxes for non-overlap

            img_boxes = []
            img_labels = []

            for _ in range(num_objects):
                label = random.choice(list(self.image_filenames.keys()))
                if not self.image_filenames[label]:  # Skip if no images for this label
                    print('none here:::')
                    continue

                # Select and resize a digit image
                digit_path = random.choice(self.image_filenames[label])
                digit_image = cv2.imread(str(digit_path))
                scale = random.uniform(0.2, 0.5)
                new_size = (int(digit_image.shape[1] * scale), int(digit_image.shape[0] * scale))
                digit_image = cv2.resize(digit_image, new_size)
                if digit_image is None:
                    print('digit_image is None')
                else:
                    print('digit image is not none')

                # Determine a random position on the canvas ensuring no overlap
                max_x = self.image_size[1] - new_size[0]
                max_y = self.image_size[0] - new_size[1]
                for _ in range(100):
                    x_min = random.randint(0, max_x)
                    y_min = random.randint(0, max_y)
                    x_max = x_min + new_size[0]
                    y_max = y_min + new_size[1]
                    bbox = [x_min, y_min, x_max - x_min, y_max - y_min]

                    # Check for overlap
                    if not any(
                        x_min < ux + uw and x_max > ux and y_min < uy + uh and y_max > uy
                        for ux, uy, uw, uh in used_locations
                    ):
                        used_locations.append(bbox)
                        break
                else:
                    continue  # Skip adding this image if a non-overlapping spot wasn't found

                # Place the digit image on the canvas and record the bbox and label
                canvas[y_min:y_max, x_min:x_max] = digit_image
                img_boxes.append(bbox)
                img_labels.append(label)

            images[i] = canvas
            boxes.append(np.array(img_boxes, dtype=np.float32))
            labels.append(np.array(img_labels, dtype=np.int32))

        # Format for KerasCV or compatible models
        images = images.astype("float32") / 255.0  # Normalize images
        boxes = tf.ragged.constant(boxes, dtype=tf.float32)
        labels = tf.ragged.constant(labels, dtype=tf.int32)

        return images, boxes, labels
