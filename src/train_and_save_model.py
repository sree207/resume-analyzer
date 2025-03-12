# train_and_save_model.py
import joblib
import pandas as pd
import json
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from tensorflow import keras
from tensorflow.keras import layers
import numpy as np

# Load the dataset
with open('cleaned_combinedcourses.json', 'r') as f:
    data = json.load(f)

# Convert to DataFrame
df = pd.DataFrame(data)

# Explode the courses into separate rows
df_exploded = df.explode('courses')
df_exploded['course_name'] = df_exploded['courses'].apply(lambda x: x['course_name'])
df_exploded['course_link'] = df_exploded['courses'].apply(lambda x: x['course_link'])
df_exploded['difficulty_level'] = df_exploded['courses'].apply(lambda x: x['difficulty_level'])
df_exploded['category'] = df_exploded['courses'].apply(lambda x: x['category'])

# Keep only relevant columns
df_final = df_exploded[['job_role', 'course_name', 'course_link', 'difficulty_level', 'category']]

# Encode job roles, course names, and categories
job_role_encoder = LabelEncoder()
course_name_encoder = LabelEncoder()
category_encoder = LabelEncoder()

df_final['job_role_encoded'] = job_role_encoder.fit_transform(df_final['job_role'])
df_final['course_name_encoded'] = course_name_encoder.fit_transform(df_final['course_name'])
df_final['category_encoded'] = category_encoder.fit_transform(df_final['category'])

# Prepare input and output
X = df_final[['job_role_encoded', 'category_encoded']].values
y = df_final['course_name_encoded'].values

# Split the dataset
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Define the model
input_dim = len(job_role_encoder.classes_) + len(category_encoder.classes_)
model = keras.Sequential([
    layers.Embedding(input_dim=input_dim, output_dim=16, input_length=X_train.shape[1]),
    layers.Flatten(),
    layers.Dense(64, activation='relu'),
    layers.Dropout(0.3),
    layers.Dense(32, activation='relu'),
    layers.Dense(len(course_name_encoder.classes_), activation='softmax')
])

# Compile the model
model.compile(optimizer='adam', loss='sparse_categorical_crossentropy', metrics=['accuracy'])

# Train the model
model.fit(X_train, y_train, epochs=50, batch_size=32, validation_split=0.1)

# Save the model and encoders
model.save('course_recommendation_model.keras')  # New recommended format
joblib.dump(job_role_encoder, 'job_role_encoder.pkl')  # Save the job role encoder
joblib.dump(course_name_encoder, 'course_name_encoder.pkl')  # Save the course name encoder
joblib.dump(category_encoder, 'category_encoder.pkl')  # Save the category encoder
df_final.to_csv('df_final.csv', index=False)  # Save the final DataFrame