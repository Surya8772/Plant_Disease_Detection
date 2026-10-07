import tensorflow as tf
from tensorflow.keras.preprocessing.image import ImageDataGenerator

data_dir = "dataset/train"
val_dir = "dataset/val"

# Aggressive augmentation to handle real-world photos
train_gen = ImageDataGenerator(
    rescale=1./255,
    rotation_range=40,
    width_shift_range=0.2,
    height_shift_range=0.2,
    shear_range=0.2,
    zoom_range=0.3,
    horizontal_flip=True,
    vertical_flip=True,
    brightness_range=[0.6,1.4],
    fill_mode='nearest'
)

val_gen = ImageDataGenerator(rescale=1./255)

train = train_gen.flow_from_directory(data_dir, target_size=(128,128), batch_size=32, class_mode='categorical')
val = val_gen.flow_from_directory(val_dir, target_size=(128,128), batch_size=32, class_mode='categorical')

base = tf.keras.applications.MobileNetV2(input_shape=(128,128,3), include_top=False, weights='imagenet')

# Fine-tune: unfreeze last 30 layers
base.trainable = True
for layer in base.layers[:-30]:
    layer.trainable = False

model = tf.keras.Sequential([
    base,
    tf.keras.layers.GlobalAveragePooling2D(),
    tf.keras.layers.Dense(256, activation='relu'),
    tf.keras.layers.BatchNormalization(),
    tf.keras.layers.Dropout(0.5),
    tf.keras.layers.Dense(128, activation='relu'),
    tf.keras.layers.Dropout(0.3),
    tf.keras.layers.Dense(train.num_classes, activation='softmax')
])

model.compile(optimizer=tf.keras.optimizers.Adam(learning_rate=1e-4),
              loss='categorical_crossentropy',
              metrics=['accuracy'])
model.fit(train, validation_data=val, epochs=15)

model.save("plant_model.h5")
print("Saved - Classes:", train.class_indices)