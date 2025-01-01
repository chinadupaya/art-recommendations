from datetime import datetime

import hopsworks
import numpy as np

import nest_asyncio
nest_asyncio.apply()
import pandas as pd

class Transformer(object):
    def __init__(self) -> None:
        # Connect to the Hopsworks
        project = hopsworks.login()
        ms = project.get_model_serving()

        # Retrieve the 'users' feature view
        fs = project.get_feature_store()
        self.user_fv = fs.get_feature_view(
            name="users",
            version=1,
        )

        # Retrieve  the "ranking" feature view and initialize the batch scoring server.
        self.ranking_fv = fs.get_feature_view(name="ranking", version=1)
        self.ranking_fv.init_batch_scoring(1)

        # Retrieve the ranking deployment
        self.ranking_server = ms.get_deployment("ranking")

    def preprocess(self, inputs):
        # Check if the input data contains a key named "instances"
        # and extract the actual data if present
        inputs = inputs["instances"] if "instances" in inputs else inputs
        inputs = inputs[0]

        # Extract user_id and transaction_date from the inputs
        user_id = inputs["user_id"]
        # transaction_date = inputs["transaction_date"]

        # Extract month from the transaction_date
        # month_of_purchase = datetime.fromisoformat(inputs.pop("transaction_date"))

        # Get user features
        user_features = self.user_fv.get_feature_vector(
            {"user_id": user_id},
            return_type="pandas",
        )

        # Enrich inputs with user age
        inputs["age"] = user_features.age.values[0]

        # Calculate the sine and cosine of the month_of_purchase
        # month_of_purchase = datetime.strptime(
        #     transaction_date, "%Y-%m-%dT%H:%M:%S.%f"
        # ).month

        # Calculate the sine and cosine components for the month_of_purchase using on-demand transformation present in "ranking" feature view.
        # feature_vector = self.ranking_fv._batch_scoring_server.compute_on_demand_features(
        #     feature_vectors=pd.DataFrame([inputs]), request_parameters={"month": month_of_purchase}
        # ).to_dict(orient="records")[0]

        # inputs["month_sin"] = feature_vector["month_sin"]
        # inputs["month_cos"] = feature_vector["month_cos"]

        return {"instances": [inputs]}

    def postprocess(self, outputs):
        # Return ordered ranking predictions
        return self.ranking_server.predict(inputs=outputs)
