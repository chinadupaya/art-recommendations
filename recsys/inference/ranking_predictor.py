import os
import joblib
import numpy as np

import logging

class Predict(object):
    
    def __init__(self):
        self.model = joblib.load(os.environ["MODEL_FILES_PATH"] + "/ranking_model.pkl")

    def predict(self, inputs):
        
        logging.info(f"✅ Inputs: {inputs}")
        
        # Extract ranking features and artwork IDs from the inputs
        features = inputs[0].pop("ranking_features")
        artwork_ids = inputs[0].pop("artwork_ids")
        
        # Log the extracted features
        logging.info("predict -> " + str(features))
        
        # Log the extracted artwork ids
        logging.info(f'artwork IDs: {artwork_ids}')
        
        logging.info(f"🦅 Predicting...")

        # Predict probabilities for the positive class
        scores = self.model.predict_proba(features).tolist()
        
        # Get scores of positive class
        scores = np.asarray(scores)[:,1].tolist() 

        # Return the predicted scores along with the corresponding artwork IDs
        return {
            "scores": scores, 
            "artwork_ids": artwork_ids,
        }
