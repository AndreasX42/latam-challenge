from typing import Literal

import pandas as pd
from fastapi import FastAPI, Depends
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from pydantic import BaseModel

from challenge.model import DelayModel

app = FastAPI(
    title="FastAPI",
    version="0.01",
    description="""API for LATAM Challenge""",
    root_path="/api",
)

model_instance: DelayModel = None


@app.get("/health", status_code=200)
async def get_health() -> dict:
    return {"status": "OK"}


# Using pydantic for request validation
class SingleFlightPredictionRequest(BaseModel):
    """Model for a single flight request"""

    TIPOVUELO: Literal["N", "I"]
    MES: Literal[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
    OPERA: Literal[
        "Grupo LATAM",
        "Sky Airline",
        "Aerolineas Argentinas",
        "Copa Air",
        "Latin American Wings",
        "Avianca",
        "JetSmart SPA",
        "Gol Trans",
        "American Airlines",
        "Air Canada",
        "Iberia",
        "Delta Air",
        "Air France",
        "Aeromexico",
        "United Airlines",
        "Oceanair Linhas Aereas",
        "Alitalia",
        "K.L.M.",
        "British Airways",
        "Qantas Airways",
        "Lacsa",
        "Austral",
        "Plus Ultra Lineas Aereas",
    ]


class ExpectedPredictionRequest(BaseModel):
    """Overall model for an '/predict' endpoint call"""

    flights: list[SingleFlightPredictionRequest]


def get_model():
    """Train the model and store it into 'model_instance' if not yet set."""
    global model_instance

    if not model_instance:
        data = pd.read_csv("./data/data.csv")
        model_instance = DelayModel()
        x_train, y_train = model_instance.preprocess(data, "delay")
        model_instance.fit(x_train, y_train)
    return model_instance


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    """Return 400 code instead of 422  for pydantic validation error to pass test."""
    return JSONResponse(
        status_code=400,
        content={"detail": exc.errors(), "body": exc.body},
    )


@app.on_event("startup")
async def on_startup():
    """On FastAPI startup we get the model ready for serving."""
    get_model()


@app.post("/predict", status_code=200)
async def post_predict(
    request: ExpectedPredictionRequest, model: DelayModel = Depends(get_model)
) -> dict:
    # transform request data to dataframe
    input_df = pd.DataFrame([dict(item) for item in request.flights])

    # preprocess input
    preprocessed_input = model.preprocess(input_df)

    # get predictions
    predictions = model.predict(preprocessed_input)

    # return list of predictions
    return {"predict": predictions}
