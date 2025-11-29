import pandas as pd
from sklearn.ensemble import RandomForestRegressor
import pickle

# Load dataset
df = pd.read_csv("backend/data/portfolio_training_data.csv")

# Features / Labels
X = df.drop("score", axis=1)
y = df["score"]

# Train model
model = RandomForestRegressor(
    n_estimators=200,
    max_depth=8,
    random_state=42
)
model.fit(X, y)

# Save model
with open("backend/models/portfolio_model.pkl", "wb") as f:
    pickle.dump(model, f)

print("Model training complete. Saved → models/portfolio_model.pkl")
