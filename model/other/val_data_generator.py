import numpy as np
import tensorflow as tf
import os
import json
import cv2
from pathlib import Path

class ValidationDataGenerator(tf.keras.utils.Sequence):
    def __init__(self, images_path, annotations_file, batch_size, image_size=(1024, 1024), shuffle=False, **kwargs):
        super().__init__(**kwargs)
        self.images_path = images_path
        self.annotations_file = annotations_file
        self.batch_size = batch_size
        self.image_size = image_size
        self.shuffle = shuffle
        self.annotations = self._load_annotations()
        self.image_ids = list(self.annotations.keys())
        self.on_epoch_end()

    def _load_annotations(self):
        with open(self.annotations_file, 'r') as f:
            coco_data = json.load(f)

        annotations = {}
        # Build a dictionary with image IDs as keys and annotations as values
        for img_info in coco_data['images']:
            img_id = img_info['id']
            file_name = img_info['file_name']
            annotations[img_id] = {
                'file_name': file_name,
                'width': img_info['width'],
                'height': img_info['height'],
                'bboxes': [],
                'labels': []
            }

        # Assign bounding boxes and category labels to each image
        for ann in coco_data['annotations']:
            img_id = ann['image_id']
            bbox = ann['bbox']
            category_id = ann['category_id']
            annotations[img_id]['bboxes'].append(bbox)
            annotations[img_id]['labels'].append(category_id)

        return annotations

    def __len__(self):
        return int(np.ceil(len(self.image_ids) / self.batch_size))

    def __getitem__(self, index):
        start_idx = index * self.batch_size
        end_idx = min((index + 1) * self.batch_size, len(self.image_ids))
        batch_image_ids = self.image_ids[start_idx:end_idx]
        images, boxes, labels = self.__data_generation(batch_image_ids)
        return images, {"boxes": boxes, "classes": labels}

    def on_epoch_end(self):
        if self.shuffle:
            np.random.shuffle(self.image_ids)

    def __data_generation(self, batch_image_ids):
        images = np.zeros((len(batch_image_ids), *self.image_size, 3), dtype=np.float32)
        boxes = []
        labels = []
        print('testing')

        for i, img_id in enumerate(batch_image_ids):
            img_info = self.annotations[img_id]
            img_path = os.path.join(self.images_path, img_info['file_name'])

            # Load and resize image
            image = cv2.imread(img_path)
            if image is None:
                print('Error: Image is none.')
            else:
                print('image is not none')
            image = cv2.resize(image, self.image_size)
            images[i] = image / 255.0  # Normalize to [0, 1]

            # Process bounding boxes and labels
            img_boxes = np.array([self._convert_bbox(bbox) for bbox in img_info['bboxes']], dtype=np.float32)
            img_labels = np.array(img_info['labels'], dtype=np.int32)

            boxes.append(img_boxes)
            labels.append(img_labels)

        # Use RaggedTensors for variable-length boxes and labels per image
        boxes = tf.ragged.constant(boxes, dtype=tf.float32)
        labels = tf.ragged.constant(labels, dtype=tf.int32)

        return images, boxes, labels

    def _convert_bbox(self, bbox):
        # Convert COCO format [x_min, y_min, width, height] to [x_min, y_min, x_max, y_max]
        x_min, y_min, width, height = bbox
        return [x_min, y_min, x_min + width, y_min + height]
