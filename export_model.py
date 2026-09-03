import mlflow.sklearn

mlflow.set_tracking_uri("sqlite:///mlflow.db")
model = mlflow.sklearn.load_model("models:/IrisRandomForest/latest")
mlflow.sklearn.save_model(model, "iris_model")
print("Model exported successfully to ./iris_model")