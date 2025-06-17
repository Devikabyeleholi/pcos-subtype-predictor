import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import classification_report, confusion_matrix
import joblib

# === Load the dataset ===
df = pd.read_csv("DatasetPCOS.csv")  

# === Encode all categorical features ===
le_dict = {}
encoded_df = df.copy()

for col in df.columns:
    if df[col].dtype == 'object' and col != 'Patient ID':
        le = LabelEncoder()
        encoded_df[col] = le.fit_transform(df[col])
        le_dict[col] = le  # Save encoders if you want to decode later

# === Define features and target ===
X = encoded_df.drop(columns=["Patient ID", "PCOS Confirmation"])
y = encoded_df["PCOS Confirmation"]

# === Split into training and testing sets ===
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# === Train the Random Forest Classifier ===
rf = RandomForestClassifier(n_estimators=100, random_state=42)
rf.fit(X_train, y_train)

# === Evaluate the model ===
y_pred = rf.predict(X_test)
print("\n Classification Report:\n")
print(classification_report(y_test, y_pred, target_names=le_dict["PCOS Confirmation"].classes_))

print("\n Confusion Matrix:")
print(confusion_matrix(y_test, y_pred))

# === Save the trained model ===
joblib.dump(rf, "pcos_rf_model.pkl")
print("\n Model saved as: pcos_rf_model.pkl")
