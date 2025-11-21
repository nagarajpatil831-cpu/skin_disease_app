# ==========================
# train_model.py
# ==========================
import pandas as pd
import os
from sklearn.model_selection import train_test_split
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from keras.models import Sequential
from keras.layers import Input, Conv2D, MaxPooling2D, Flatten, Dense

# ==========================
# 1️⃣ Load the metadata CSV
# ==========================
data = pd.read_csv(r"C:\Users\Nagaraj\OneDrive\Desktop\skin_disease_app\HAM10000\HAM10000_metadata.csv")

# Add full image paths
data['path'] = data['image_id'].apply(lambda x:
    os.path.join(r"C:\Users\Nagaraj\OneDrive\Desktop\skin_disease_app\HAM10000\images", x + ".jpg"))

# ==========================
# 2️⃣ Split into train/test
# ==========================
train_df, test_df = train_test_split(data, test_size=0.2, random_state=42, stratify=data['dx'])

# ==========================
# 3️⃣ Create Image Generators
# ==========================
datagen = ImageDataGenerator(rescale=1./255, validation_split=0.2)

train_gen = datagen.flow_from_dataframe(
    dataframe=train_df,
    x_col='path',
    y_col='dx',
    target_size=(64, 64),
    batch_size=32,
    class_mode='categorical',
    subset='training'
)

val_gen = datagen.flow_from_dataframe(
    dataframe=train_df,
    x_col='path',
    y_col='dx',
    target_size=(64, 64),
    batch_size=32,
    class_mode='categorical',
    subset='validation'
)

# ✅ Number of unique disease classes
num_classes = len(train_gen.class_indices)
print(f"Detected {num_classes} disease classes:", list(train_gen.class_indices.keys()))

# ==========================
# 4️⃣ Create CNN Model
# ==========================
model = Sequential([
    Input(shape=(64, 64, 3)),                   # ✅ use Input() layer instead of input_shape
    Conv2D(16, (3,3), activation='relu'),
    MaxPooling2D(2,2),
    Flatten(),
    Dense(64, activation='relu'),
    Dense(num_classes, activation='softmax')    # ✅ dynamically uses number of classes
])

model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])

# ==========================
# 5️⃣ Train the model
# ==========================
model.fit(train_gen, validation_data=val_gen, epochs=10)

# ==========================
# 6️⃣ Save the trained model
# ==========================
model.save("skin_disease_model.h5")
print("✅ Model trained and saved successfully as skin_disease_model.h5")
