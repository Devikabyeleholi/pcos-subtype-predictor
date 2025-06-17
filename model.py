import joblib
import numpy as np

# Load the trained model
model = joblib.load("pcos_rf_model.pkl")  # Make sure this file exists in your project root or adjust path

# Map categorical values to the encodings used during training
map_values = {
    "Yes": 1, "No": 0,
    "Mild": 0, "Severe": 1,
    "Underweight": 0, "Normal": 1, "Overweight": 2,
    "Obese PCOS": 0, "Lean PCOS": 1, "Pill-Induced PCOS": 2, "Other": 3,
    "Young Adult": 0, "Middle Age": 1,
    "Low": 0, "Medium": 1, "High": 2,
    "Elevated": 1, "Normal": 0,
    "Sedentary": 0, "Active": 1,
    "Junk/Fast food": 1, "Healthy": 0,
    "Vegetarian": 0, "Non-Vegetarian": 1,
}

# Subtype labels (adjust based on your training data labels)
label_mapping = {
    0: "Hyperandrogenic PCOS",
    1: "Insulin-Resistant PCOS",
    2: "Inflammatory PCOS",
    3: "Pill-Induced PCOS"
}

def predict_pcos_model_based(input_dict):
    """
    Predict PCOS subtype based on encoded input dictionary.

    input_dict: {
        "acne": "Yes",
        "hair_loss": "No",
        "fatigue": "Mild",
        ...
    }
    """
    # Encode input features
    input_vector = [map_values.get(value, 0) for value in input_dict.values()]

    # Make prediction
    prediction = model.predict([input_vector])[0]

    # Map numeric prediction to human-readable subtype
    return label_mapping.get(prediction, "General PCOS - Further Analysis Needed")
