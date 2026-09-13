import tensorflow as tf
from tensorflow.keras.preprocessing.image import ImageDataGenerator

data_dir = "dataset/train"
val_dir = "dataset/val"

# Important: Augmentation to handle real photos like yours with hand
train_gen = ImageDataGenerator(
    rescale=1./255,
    rotation_range=20,
    zoom_range=0.2,
    horizontal_flip=True,
    brightness_range=[0.8,1.2]
)

val_gen = ImageDataGenerator(rescale=1./255)

train = train_gen.flow_from_directory(data_dir, target_size=(128,128), batch_size=32, class_mode='categorical')
val = val_gen.flow_from_directory(val_dir, target_size=(128,128), batch_size=32, class_mode='categorical')

base = tf.keras.applications.MobileNetV2(input_shape=(128,128,3), include_top=False, weights='imagenet')
base.trainable = False

model = tf.keras.Sequential([
    base,
    tf.keras.layers.GlobalAveragePooling2D(),
    tf.keras.layers.Dense(128, activation='relu'),
    tf.keras.layers.Dropout(0.3),
    tf.keras.layers.Dense(train.num_classes, activation='softmax')
])

model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])
model.fit(train, validation_data=val, epochs=10)

model.save("plant_model.h5")
print("Saved - Classes:", train.class_indices)