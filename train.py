#!/usr/bin/python3

import logging
import sys
import warnings
from urllib.parse import urlparse

import os
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.linear_model import ElasticNet
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split

import mlflow
import mlflow.sklearn
from mlflow.models import infer_signature

logging.basicConfig(level=logging.WARN)
logger = logging.getLogger(__name__)


def eval_metrics(actual, pred):
    rmse = np.sqrt(mean_squared_error(actual, pred))
    mae = mean_absolute_error(actual, pred)
    r2 = r2_score(actual, pred)
    return rmse, mae, r2


def get_boston_data():
    try:
        # Assuming "BostonHousing.csv" is a valid CSV file in the same directory
        boston_path = "BostonHousing.csv"
        data = pd.read_csv(boston_path)
        return data
    except Exception as e:
        logger.exception("Unable to load Boston dataset. Error: %s", e)
        raise


if __name__ == "__main__":
    warnings.filterwarnings("ignore")
    np.random.seed(42)

    # Load the Boston housing data
    data = get_boston_data()

    # Split the data into training and test sets. (0.8, 0.2) split.
    train, test = train_test_split(data, test_size=0.2, random_state=42)

    # The predicted column is "target"
    # The predicted column is "medv" instead of "target"
    train_x = train.drop(["medv"], axis=1)
    test_x = test.drop(["medv"], axis=1)
    train_y = train[["medv"]]
    test_y = test[["medv"]]

    alpha = float(sys.argv[1]) if len(sys.argv) > 1 else 0.5
    l1_ratio = float(sys.argv[2]) if len(sys.argv) > 2 else 0.5

    with mlflow.start_run():
        lr = ElasticNet(alpha=alpha, l1_ratio=l1_ratio, random_state=42)
        lr.fit(train_x, train_y)

        predicted_targets = lr.predict(test_x)

        (rmse, mae, r2) = eval_metrics(test_y, predicted_targets)

        print(f"ElasticNet model (alpha={alpha:f}, l1_ratio={l1_ratio:f}):")
        print(f"  RMSE: {rmse}")
        print(f"  MAE: {mae}")
        print(f"  R2: {r2}")

        mlflow.log_param("alpha", alpha)
        mlflow.log_param("l1_ratio", l1_ratio)
        mlflow.log_metric("rmse", rmse)
        mlflow.log_metric("r2", r2)
        mlflow.log_metric("mae", mae)

        predictions = lr.predict(train_x)
        signature = infer_signature(train_x, predictions)

        tracking_url_type_store = urlparse(mlflow.get_tracking_uri()).scheme

        # Model registry does not work with file store
        if tracking_url_type_store != "file":
            # Register the model
            mlflow.sklearn.log_model(
                lr, "model", registered_model_name="ElasticNetBostonHousingModel", signature=signature
            )
        else:
            mlflow.sklearn.log_model(lr, "model", signature=signature)
