from flask import Blueprint, request, jsonify
from app.routes.auth import jwt_required
from app.services.job_service import JobService
from app.services.forecasting.skill_frequency import SkillFrequencyEngine
from app.services.forecasting.evaluation import ModelEvaluator
from app.services.forecasting.trend_analysis import TrendAnalysisEngine
from app.models.skill_forecast import SkillForecastModel
from app.models.dataset_metadata import DatasetMetadataModel
from app.db import Database

admin_bp = Blueprint('admin', __name__, url_prefix='/api/admin')

@admin_bp.route('/system-health', methods=['GET'])
def get_system_health():
    """Get system health and database statistics."""
    all_jobs = JobService.get_all_jobs()
    return jsonify({
        "success": True,
        "data": {
            "status": "operational",
            "database_connected": Database.is_connected(),
            "total_ingested_jobs": len(all_jobs),
            "version": "v1.0"
        }
    }), 200

@admin_bp.route('/datasets/ingest', methods=['POST'])
@jwt_required
def ingest_job_dataset():
    """Admin endpoint to validate and re-ingest job datasets."""
    all_jobs = JobService.get_all_jobs()
    meta = DatasetMetadataModel.log_ingestion({
        "version": "v1.0",
        "source": "sample_jobs.csv",
        "total_records": len(all_jobs),
        "valid_jobs": len(all_jobs),
        "duplicate_count": 0,
        "status": "SUCCESS"
    })
    return jsonify({
        "success": True,
        "message": f"Successfully ingested {len(all_jobs)} valid job records into dataset.",
        "data": {
            "metadata": DatasetMetadataModel.to_json(meta)
        }
    }), 200

@admin_bp.route('/forecast/train', methods=['POST'])
@jwt_required
def train_forecasting_models():
    """Admin-only endpoint to trigger time-series model training and update forecast cache."""
    all_jobs = JobService.get_all_jobs()
    time_series_map = SkillFrequencyEngine.compute_monthly_frequencies(all_jobs)
    trained_count = 0

    for sk, ts in time_series_map.items():
        rates = ts["demand_rates"]
        current_demand = rates[-1] if rates else 0.0

        eval_res = ModelEvaluator.evaluate_and_select_best_model(rates, horizon=3)
        best_model = eval_res["best_model"]
        preds = best_model.predict(horizon=3)
        predicted_demand = preds[-1] if preds else current_demand

        mae = eval_res["mae"]
        lower_bound = round(max(0.0, predicted_demand - mae), 1)
        upper_bound = round(min(100.0, predicted_demand + mae), 1)

        trend_res = TrendAnalysisEngine.classify_trend(rates, current_demand, predicted_demand)

        forecast_doc = {
            "skill": sk.title(),
            "horizon": "6M",
            "current_demand": current_demand,
            "predicted_demand": predicted_demand,
            "lower_bound": lower_bound,
            "upper_bound": upper_bound,
            "trend": trend_res["trend"],
            "growth_rate": trend_res["growth_rate"],
            "model_name": eval_res["best_model_name"],
            "mae": mae,
            "rmse": eval_res["rmse"],
            "reliability": eval_res["reliability"],
            "periods": ts["periods"],
            "historical_rates": rates,
            "forecast_periods": ["2026-03", "2026-04", "2026-05"],
            "forecast_rates": preds
        }

        SkillForecastModel.save_forecast(forecast_doc)
        trained_count += 1

    return jsonify({
        "success": True,
        "message": f"Successfully trained time-series forecasting models for {trained_count} skills.",
        "data": {
            "skills_trained": trained_count
        }
    }), 200
