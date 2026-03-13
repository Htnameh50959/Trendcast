import pandas as pd
import numpy as np
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from statsmodels.tsa.statespace.sarimax import SARIMAX
from datetime import datetime, timezone
from api.firebase_admin_init import get_db, verify_token

router = APIRouter()


class ForecastRequest(BaseModel):
    column: str = "Weekly_Sales"
    horizon: int = 30
    model: str = "sarima"
    group_by: str | None = None


def get_user_id_from_request(request: Request) -> str:
    token = getattr(request.state, "token", None)
    if not token:
        raise HTTPException(status_code=401, detail="No authentication token provided")
    try:
        return verify_token(token)
    except Exception:
        raise HTTPException(status_code=401, detail="Unauthorized")


def get_latest_sales_doc(user_id: str):
    db = get_db()
    docs = (
        db.collection("sales_data")
        .where("user_id", "==", user_id)
        .order_by("created_at", direction="DESCENDING")
        .limit(1)
        .stream()
    )
    results = list(docs)
    return results[0].to_dict() if results else None


@router.post("/generateforecast")
async def generate_forecast(req: ForecastRequest, request: Request):
    try:
        user_id = "anonymous"
        try:
            user_id = get_user_id_from_request(request)
        except Exception:
            pass

        dataset = get_latest_sales_doc(user_id) if user_id != "anonymous" else None

        if not dataset:
            raise HTTPException(status_code=400, detail="No data available. Please upload sales data first.")

        column = req.column
        horizon = req.horizon

        df = pd.DataFrame(dataset.get("data", []))

        if df.empty or "Date" not in df.columns or column not in df.columns:
            raise HTTPException(status_code=400, detail="Insufficient data for forecasting")

        df["Date"] = pd.to_datetime(df["Date"], dayfirst=True, errors="coerce")
        df = df.dropna(subset=["Date", column])

        if df.empty:
            raise HTTPException(status_code=400, detail="No valid data found in selected column")

        df = df.sort_values("Date").reset_index(drop=True)

        series = (
            df.groupby("Date")[column]
            .sum()
            .resample("D")
            .sum()
            .fillna(0)
        )

        if len(series) < 2:
            raise HTTPException(status_code=400, detail="Not enough data points for forecasting")

        def forecast_series(series_obj, horizon_val):
            try:
                if len(series_obj) > 14:
                    model = SARIMAX(
                        series_obj,
                        order=(1, 1, 1),
                        seasonal_order=(1, 1, 1, 7),
                        enforce_stationarity=False,
                        enforce_invertibility=False,
                    )
                else:
                    model = SARIMAX(
                        series_obj,
                        order=(1, 1, 1),
                        enforce_stationarity=False,
                        enforce_invertibility=False,
                    )
                model_fit = model.fit(disp=False)
                forecast = model_fit.get_forecast(steps=horizon_val).predicted_mean
                fitted = model_fit.fittedvalues
            except Exception:
                from statsmodels.tsa.holtwinters import ExponentialSmoothing
                model = ExponentialSmoothing(
                    series_obj,
                    trend="add",
                    seasonal="add",
                    seasonal_periods=7,
                )
                model_fit = model.fit()
                forecast = model_fit.forecast(horizon_val)
                fitted = model_fit.fittedvalues
            return forecast, fitted

        def compute_metrics(actual, predicted):
            mae = mean_absolute_error(actual, predicted)
            mse = mean_squared_error(actual, predicted)
            r2 = r2_score(actual, predicted)
            return {
                "mae": float(mae),
                "mse": float(mse),
                "r2": float(r2),
                "rmse": float(np.sqrt(mse)),
                "accuracy": float(max(0, min(100, r2 * 100))),
            }

        forecast_values, historical_pred = forecast_series(series, horizon)
        metrics = compute_metrics(series, historical_pred)

        response_payload = {
            "forecast": [max(0, float(v)) for v in forecast_values.tolist()],
            "dates": [
                d.strftime("%Y-%m-%d")
                for d in pd.date_range(
                    start=series.index[-1] + pd.Timedelta(days=1),
                    periods=horizon,
                    freq="D",
                )
            ],
            "historical": {
                "dates": series.index.strftime("%Y-%m-%d").tolist(),
                "values": series.values.tolist(),
                "trend": historical_pred.tolist(),
            },
            "metrics": metrics,
            "is_grouped": False,
        }

        if req.group_by and req.group_by in df.columns:
            groups_dict = {}
            for group_value, group_df in df.groupby(req.group_by):
                group_df = group_df.dropna(subset=["Date", column])
                if group_df.empty:
                    continue
                sub_series = (
                    group_df.groupby("Date")[column]
                    .sum()
                    .resample("D")
                    .sum()
                    .fillna(0)
                )
                if len(sub_series) < 2:
                    continue
                group_forecast, group_pred = forecast_series(sub_series, horizon)
                groups_dict[str(group_value)] = {
                    "historical": sub_series.values.tolist(),
                    "forecast": [max(0, float(v)) for v in group_forecast.tolist()],
                    "dates": sub_series.index.strftime("%Y-%m-%d").tolist(),
                }
            response_payload["is_grouped"] = True
            response_payload["groups"] = groups_dict

        try:
            db = get_db()
            db.collection("forecasts").add({
                "column": column,
                "horizon": horizon,
                "model": req.model,
                "forecast_data": response_payload,
                "user_id": user_id,
                "created_at": datetime.now(timezone.utc).isoformat(),
            })
        except Exception as db_err:
            print(f"Warning: Could not save forecast to database: {db_err}")

        return response_payload

    except Exception as e:
        import traceback
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/forecasts")
async def get_user_forecasts(request: Request):
    try:
        user_id = get_user_id_from_request(request)
        db = get_db()
        docs = (
            db.collection("forecasts")
            .where("user_id", "==", user_id)
            .order_by("created_at", direction="DESCENDING")
            .stream()
        )
        return {"forecasts": [d.to_dict() for d in docs]}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/forecasts/{forecast_id}")
async def get_forecast(forecast_id: str, request: Request):
    try:
        db = get_db()
        doc = db.collection("forecasts").document(forecast_id).get()
        if not doc.exists:
            raise HTTPException(status_code=404, detail="Forecast not found")
        return {"forecast": doc.to_dict()}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/forecasts/{forecast_id}")
async def delete_forecast(forecast_id: str, request: Request):
    try:
        db = get_db()
        db.collection("forecasts").document(forecast_id).delete()
        return {"message": "Forecast deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
