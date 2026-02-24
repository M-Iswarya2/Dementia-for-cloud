import pandas as pd
from sklearn.ensemble import RandomForestClassifier
import pickle

# Load dataset
df = pd.read_csv("dataset/fusion_dataset.csv")

# Features and label
X = df[['memory_score', 'voice_score', 'questionnaire_score']]
y = df['risk_label']

# Train RandomForest
clf = RandomForestClassifier(n_estimators=100, random_state=42)
clf.fit(X, y)

# Save model to backend models folder
pickle.dump(clf, open("models/final_evaluator.pkl", "wb"))

print("RandomForest trained and saved as final_evaluator.pkl")
