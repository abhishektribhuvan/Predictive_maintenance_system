import pandas as pd
from sklearn.ensemble import IsolationForest
import joblib
import numpy as np

df = pd.read_csv("training_data.csv")
healthy_means =  df["mean"]
healthy_variances = df["var"]
X_train = np.column_stack((healthy_means, healthy_variances))

print("Training Isolation Forest...")
model = IsolationForest(n_estimators=100, contamination=0.01, random_state=42)
model.fit(X_train)

print("Saving the trained model...")
joblib.dump(model, "vibration_model.pkl")
print("Model saved as vibration_model.pkl! Ready for production.")