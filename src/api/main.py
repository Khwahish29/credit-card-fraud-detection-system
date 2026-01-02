"""FastAPI application for credit card fraud detection."""

from typing import Dict, List, Optional

import pandas as pd
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from src.config import APIConfig
from src.models.loader import load_model
from src.utils import setup_logger

logger = setup_logger(__name__)

# Initialize FastAPI app
config = APIConfig()
app = FastAPI(
    title=config.API_TITLE,
    version=config.API_VERSION,
    description=config.API_DESCRIPTION,
)

# Global variables for model and preprocessor
model = None
preprocessor = None


class TransactionFeatures(BaseModel):
    """Transaction features model."""
    
    # Note: In a real scenario, you would define all feature columns here.
    # For flexibility, we'll accept a dictionary of features.
    features: Dict[str, float] = Field(
        ...,
        description="Dictionary of feature names and values",
    )
    
    class Config:
        """Pydantic config."""
        schema_extra = {
            "example": {
                "features": {
                    "V1": -1.359807134,
                    "V2": -0.072781173,
                    "V3": 2.536346738,
                    # ... other features
                }
            }
        }


class PredictionRequest(BaseModel):
    """Request model for prediction endpoint."""
    
    transaction_id: str = Field(..., description="Unique transaction identifier")
    features: Dict[str, float] = Field(
        ...,
        description="Dictionary of feature names and values",
    )
    
    class Config:
        """Pydantic config."""
        schema_extra = {
            "example": {
                "transaction_id": "txn_12345",
                "features": {
                    "V1": -1.359807134,
                    "V2": -0.072781173,
                    "V3": 2.536346738,
                }
            }
        }


class PredictionResponse(BaseModel):
    """Response model for prediction endpoint."""
    
    transaction_id: str
    fraud_probability: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Probability of fraud (0.0 to 1.0)",
    )
    is_fraud: bool = Field(..., description="Fraud prediction (threshold: 0.5)")
    threshold: float = Field(default=0.5, description="Threshold used for classification")


@app.on_event("startup")
async def startup_event() -> None:
    """
    Load model and preprocessor on application startup.
    """
    global model, preprocessor
    
    logger.info("Starting up FastAPI application...")
    
    try:
        model, preprocessor = load_model(
            model_path=config.MODEL_PATH,
            preprocessor_path=config.PREPROCESSOR_PATH,
        )
        logger.info("Model and preprocessor loaded successfully")
    except FileNotFoundError as e:
        logger.error(f"Failed to load model/preprocessor: {str(e)}")
        logger.error(
            "Please train the model first using: python -m src.models.train"
        )
        raise
    except Exception as e:
        logger.error(f"Error loading model/preprocessor: {str(e)}")
        raise


@app.get("/")
async def root() -> Dict[str, str]:
    """
    Root endpoint.
    
    Returns:
        Welcome message and API information.
    """
    return {
        "message": "Credit Card Fraud Detection API",
        "version": config.API_VERSION,
        "status": "running",
    }


@app.get("/health")
async def health() -> Dict[str, str]:
    """
    Health check endpoint.
    
    Returns:
        Health status of the API.
    """
    is_ready = model is not None and preprocessor is not None
    
    return {
        "status": "healthy" if is_ready else "unhealthy",
        "model_loaded": model is not None,
        "preprocessor_loaded": preprocessor is not None,
    }


@app.post("/predict", response_model=PredictionResponse)
async def predict(request: PredictionRequest) -> PredictionResponse:
    """
    Predict fraud probability for a transaction.
    
    Args:
        request: Prediction request containing transaction_id and features.
    
    Returns:
        Prediction response with fraud probability and classification.
    
    Raises:
        HTTPException: If prediction fails.
    """
    if model is None or preprocessor is None:
        raise HTTPException(
            status_code=503,
            detail="Model or preprocessor not loaded",
        )
    
    try:
        logger.info(
            f"Processing prediction request for transaction: "
            f"{request.transaction_id}"
        )
        
        # Convert features to DataFrame
        features_df = pd.DataFrame([request.features])
        
        # Validate that all required features are present
        expected_features = preprocessor.feature_columns
        if expected_features:
            missing_features = set(expected_features) - set(features_df.columns)
            if missing_features:
                raise HTTPException(
                    status_code=400,
                    detail=f"Missing required features: {list(missing_features)}",
                )
        
        # Transform features
        features_transformed = preprocessor.transform(features_df)
        
        # Predict
        fraud_probability = float(model.predict_proba(features_transformed)[0, 1])
        threshold = 0.5
        is_fraud = fraud_probability >= threshold
        
        logger.info(
            f"Prediction for {request.transaction_id}: "
            f"probability={fraud_probability:.4f}, is_fraud={is_fraud}"
        )
        
        return PredictionResponse(
            transaction_id=request.transaction_id,
            fraud_probability=fraud_probability,
            is_fraud=is_fraud,
            threshold=threshold,
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error during prediction: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Prediction failed: {str(e)}",
        )


@app.post("/predict/batch")
async def predict_batch(
    requests: List[PredictionRequest],
) -> List[PredictionResponse]:
    """
    Predict fraud probability for multiple transactions (batch processing).
    
    Args:
        requests: List of prediction requests.
    
    Returns:
        List of prediction responses.
    
    Raises:
        HTTPException: If prediction fails.
    """
    if model is None or preprocessor is None:
        raise HTTPException(
            status_code=503,
            detail="Model or preprocessor not loaded",
        )
    
    try:
        logger.info(f"Processing batch prediction for {len(requests)} transactions")
        
        # Prepare features DataFrame
        features_list = [req.features for req in requests]
        features_df = pd.DataFrame(features_list)
        
        # Validate features
        expected_features = preprocessor.feature_columns
        if expected_features:
            missing_features = set(expected_features) - set(features_df.columns)
            if missing_features:
                raise HTTPException(
                    status_code=400,
                    detail=f"Missing required features: {list(missing_features)}",
                )
        
        # Transform features
        features_transformed = preprocessor.transform(features_df)
        
        # Predict
        fraud_probabilities = model.predict_proba(features_transformed)[:, 1]
        threshold = 0.5
        
        # Build responses
        responses = []
        for i, request in enumerate(requests):
            fraud_prob = float(fraud_probabilities[i])
            is_fraud = fraud_prob >= threshold
            
            responses.append(
                PredictionResponse(
                    transaction_id=request.transaction_id,
                    fraud_probability=fraud_prob,
                    is_fraud=is_fraud,
                    threshold=threshold,
                )
            )
        
        logger.info(f"Batch prediction completed for {len(responses)} transactions")
        
        return responses
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error during batch prediction: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Batch prediction failed: {str(e)}",
        )


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "src.api.main:app",
        host=config.HOST,
        port=config.PORT,
        reload=False,
    )

