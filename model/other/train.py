# train.py

import tensorflow as tf
import keras_cv
from train_data_generator import ObjectDetectionDataGenerator
from val_data_generator import ValidationDataGenerator

# Paths and configuration
digit_images_path = "model/archive/data/synthetic_digits/imgs_train"
background_images_path = "background_images"
validation_images_dir = "output_dataset/val/images"
validation_annotations_file = "output_dataset/val/annotations/annotations.json"

# Model configuration
image_size = (512, 512)
num_classes = 10
batch_size = 8
epochs = 50

# Define the model using KerasCV's RetinaNet
# Corrected code
model = keras_cv.models.RetinaNet(
    backbone="resnet50",  # Backbone as the first positional argument
    num_classes=num_classes,  # num_classes as a keyword argument
    bounding_box_format="xywh",
    backbone_weights="imagenet",
    include_rescaling=True,
    input_shape=(*image_size, 3),
)



# Compile the model with appropriate loss and metrics
loss = keras_cv.losses.ObjectDetectionLoss(
    classes=num_classes,
    reduction="auto",
    bounding_box_format="xywh",
)
metrics = [
    keras_cv.metrics.BoxRecall(bounding_box_format="xywh", name="box_recall"),
    keras_cv.metrics.BoxPrecision(bounding_box_format="xywh", name="box_precision"),
    keras_cv.metrics.CategoricalAccuracy(name="class_accuracy"),
]

model.compile(
    optimizer=tf.keras.optimizers.Adam(learning_rate=1e-4),
    loss=loss,
    metrics=metrics,
)

# Initialize training data generator
train_gen = ObjectDetectionDataGenerator(
    digit_images_path=digit_images_path,
    background_images_path=background_images_path,
    batch_size=batch_size,
    num_classes=num_classes,
    image_size=image_size,
)

# Initialize validation data generator
val_gen = ValidationDataGenerator(
    images_path=validation_images_dir,
    annotations_file=validation_annotations_file,
    batch_size=batch_size,
    image_size=image_size,
)

# Define callbacks for checkpointing and early stopping
checkpoint_callback = tf.keras.callbacks.ModelCheckpoint(
    filepath="checkpoints/resnet50_digit_detection_checkpoint.keras",
    save_best_only=True,
    monitor="val_loss",
    mode="min",
    verbose=1,
)

early_stopping_callback = tf.keras.callbacks.EarlyStopping(
    monitor="val_loss",
    patience=10,
    restore_best_weights=True,
    mode="min",
    verbose=1,
)

# Train the model
history = model.fit(
    train_gen,
    validation_data=val_gen,
    epochs=epochs,
    callbacks=[checkpoint_callback, early_stopping_callback],
    verbose=1,
)
