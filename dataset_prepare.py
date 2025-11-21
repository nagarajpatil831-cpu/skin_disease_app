import pandas as pd
import os
from sklearn.model_selection import train_test_split

# Step 1: Load metadata
data = pd.read_csv(r"C:\Users\Nagaraj\OneDrive\Desktop\python\chapter 1\HAM10000\HAM10000_metadata.csv")
print("Data loaded successfully:")
print(data.head())

# Step 2: Add image path
data['path'] = data['image_id'].apply(lambda x:
    os.path.join(r"C:\Users\Nagaraj\OneDrive\Desktop\python\chapter 1\HAM10000\images", x + ".jpg"))

# Step 3: Split dataset
train_df, test_df = train_test_split(data, test_size=0.2, random_state=42, stratify=data['dx'])

print(f"\nTraining samples: {len(train_df)}")
print(f"Testing samples: {len(test_df)}")

# Optional: Save for reuse
train_df.to_csv("train_data.csv", index=False)
test_df.to_csv("test_data.csv", index=False)
print("Train/Test CSVs saved.")
