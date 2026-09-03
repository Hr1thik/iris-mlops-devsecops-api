from fastapi import FastAPI
import mlflow.sklearn
import pandas as pd
from pydantic import BaseModel

app = FastAPI()

# Load the MLflow model directly from the copied directory
MODEL_URI = "iris_model"
model = mlflow.sklearn.load_model(MODEL_URI)

class IrisInput(BaseModel):
    sepal_length: float
    sepal_width: float
    petal_length: float
    petal_width: float

@app.post("/predict")
def predict(features: IrisInput):
    data_df = pd.DataFrame([list(features.model_dump().values())], columns=[
        "sepal length (cm)", "sepal width (cm)", "petal length (cm)", "petal width (cm)"
    ])
    prediction = model.predict(data_df)
    return {"class_id": int(prediction[0])}