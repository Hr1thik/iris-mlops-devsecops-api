import os
import mlflow
import mlflow.sklearn
from sklearn.datasets import load_iris
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split

# Allow local file store
os.environ["MLFLOW_ALLOW_FILE_STORE"] = "true"

# Explicitly use local mlruns folder
mlflow.set_tracking_uri("./mlruns")
mlflow.set_experiment("iris_classification")

data = load_iris()
X_train, X_test, y_train, y_test = train_test_split(data.data, data.target, test_size=0.2, random_state=42)

with mlflow.start_run() as run:
    model = RandomForestClassifier(n_estimators=50, max_depth=3, random_state=42)
    model.fit(X_train, y_train)
    
    accuracy = model.score(X_test, y_test)
    mlflow.log_param("n_estimators", 50)
    mlflow.log_param("max_depth", 3)
    mlflow.log_metric("accuracy", accuracy)
    
    # This registers the model directly inside ./mlruns/models
    mlflow.sklearn.log_model(model, "model", registered_model_name="IrisRandomForest")
    print(f"Model successfully saved into mlruns! Accuracy: {accuracy:.4f}")