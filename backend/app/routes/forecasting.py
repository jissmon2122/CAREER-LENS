from flask import Blueprint, request, jsonify
from app.routes.auth import jwt_required
from app.services.job_service import JobService
from app.services.forecasting.skill_frequency import SkillFrequencyEngine
from app.services.forecasting.evaluation import ModelEvaluator
from app.services.forecasting.trend_analysis import TrendAnalysisEngine
from app.services.forecasting.recommendations import ForecastingRecommendationEngine
from app.services.forecasting.preprocessing import PreprocessingService
from app.services.forecasting.skill_taxonomy import SkillTaxonomy
from app.services.forecasting.skill_registry import SkillRegistry
from app.services.skill_gap import SkillGapEngine
from app.models.resume import ResumeModel
from app.models.resume_analysis import ResumeAnalysisModel
from app.models.user import UserModel
from app.models.skill_forecast import SkillForecastModel

import time
import logging

logger = logging.getLogger(__name__)

forecasting_bp = Blueprint('forecasting', __name__, url_prefix='/api/forecasting')

# In-memory forecast cache (1 hour TTL)
_ALL_FORECASTS_CACHE = {"timestamp": 0, "data": None}
_FORECASTS_TTL_SECONDS = 3600
_USER_FORECAST_REC_CACHE = {}

TOTAL_FORECAST_HORIZON_MONTHS = 36

def _generate_all_forecasts(force_refresh=False):
    """
    Generate and return continuous time-series forecasts across all dataset skills.
    Uses real 2023-2026 historical observations and forecasts the next 36 months (2026-12 to 2029-11).
    Evaluates all 4 algorithms (Naive, Moving Average, Linear Regression, Exponential Smoothing).
    """
    global _ALL_FORECASTS_CACHE
    now_ts = time.time()

    # 1. In-memory cache hit
    if not force_refresh and _ALL_FORECASTS_CACHE["data"] and (now_ts - _ALL_FORECASTS_CACHE["timestamp"] < _FORECASTS_TTL_SECONDS):
        return _ALL_FORECASTS_CACHE["data"]

    # 2. Check MongoDB collection for existing fresh forecasts
    if not force_refresh:
        try:
            existing_docs = SkillForecastModel.get_all_forecasts()
            # Only use if documents have the new 36M horizon and non-zero counts
            if existing_docs and len(existing_docs) >= 20:
                has_36m = any(len(d.get("forecast_periods", [])) >= 36 for d in existing_docs)
                has_data = sum(1 for d in existing_docs if d.get("current_demand", 0) > 0) >= 15
                if has_36m and has_data:
                    forecasts = {}
                    for d in existing_docs:
                        sk = str(d.get("skill", "")).lower().strip()
                        if sk:
                            forecasts[sk] = d
                    _ALL_FORECASTS_CACHE = {"timestamp": now_ts, "data": forecasts}
                    logger.info(f"Loaded {len(forecasts)} verified 36M forecasts from database cache.")
                    return forecasts
        except Exception as e:
            logger.warning(f"Could not load forecasts from database cache: {e}")

    # 3. Compute forecasts from real job vacancies in MongoDB Atlas
    logger.info("Computing time-series forecasting models across dataset skills (2023-2026 -> 36M future)...")
    coll = None
    try:
        from app.models.job import JobModel
        coll = JobModel.get_collection()
    except Exception:
        pass

    if coll is not None:
        raw_jobs = list(coll.find({}, {
            "posted_at": 1, "posted_date": 1, "first_seen_at": 1,
            "required_skills": 1, "preferred_skills": 1, "skills": 1,
            "title": 1, "clean_description": 1
        }))
    else:
        raw_jobs = JobService.get_all_jobs()

    time_series_map = SkillFrequencyEngine.compute_monthly_frequencies(raw_jobs)
    forecasts = {}
    docs_to_save = []

    last_historical_period = SkillFrequencyEngine.MAX_HISTORICAL_PERIOD  # "2026-11"
    future_periods = PreprocessingService.generate_forecast_periods(last_historical_period, horizon=TOTAL_FORECAST_HORIZON_MONTHS)

    for sk, ts in time_series_map.items():
        rates = ts["demand_rates"]
        current_demand = rates[-1] if rates else 0.0

        # Run model evaluation across all 4 algorithms on historical split
        eval_res = ModelEvaluator.evaluate_and_select_best_model(rates, horizon=TOTAL_FORECAST_HORIZON_MONTHS)
        best_model = eval_res["best_model"]

        # Generate 36-month predictions & prediction intervals
        preds, lower_bounds, upper_bounds = best_model.predict_with_intervals(horizon=TOTAL_FORECAST_HORIZON_MONTHS)
        predicted_36m = preds[-1] if preds else current_demand

        # Get individual forecasts for all 4 models
        all_model_preds = ModelEvaluator.fit_and_predict_all_models(rates, horizon=TOTAL_FORECAST_HORIZON_MONTHS)

        mae = eval_res["mae"]
        rmse = eval_res["rmse"]
        mape = eval_res["mape"]
        reliability = eval_res["reliability"]

        if not ts.get("has_sufficient_data") or reliability == "INSUFFICIENT_HISTORICAL_DATA":
            confidence_label = "Confidence bounds wide (insufficient historical data)"
        else:
            confidence_label = f"[{lower_bounds[5]}% – {upper_bounds[5]}%] (6M) / [{lower_bounds[-1]}% – {upper_bounds[-1]}%] (36M)"

        trend_res = TrendAnalysisEngine.classify_trend(rates, current_demand, predicted_36m)

        forecast_doc = {
            "skill": sk.lower(),
            "skill_display": sk.title(),
            "category": ts["category"],
            "sub_categories": ts.get("sub_categories", []),
            "horizon": f"{TOTAL_FORECAST_HORIZON_MONTHS}M",
            "current_demand": current_demand,
            "predicted_demand": predicted_36m,
            "lower_bound": lower_bounds[-1] if lower_bounds else current_demand,
            "upper_bound": upper_bounds[-1] if upper_bounds else current_demand,
            "confidence_label": confidence_label,
            "trend": trend_res["trend"],
            "trend_label": trend_res["trend_label"],
            "growth_rate": trend_res["growth_rate"],
            "relative_growth": trend_res["relative_growth"],
            "growth_diff": trend_res["growth_diff"],
            "reason": trend_res["reason"],
            "model_name": eval_res["best_model_name"],
            "mae": mae,
            "rmse": rmse,
            "mape": mape,
            "reliability": reliability,
            "periods": ts["periods"],
            "historical_rates": rates,
            "forecast_periods": future_periods,
            "forecast_rates": preds,
            "forecast_lower_bounds": lower_bounds,
            "forecast_upper_bounds": upper_bounds,
            "model_comparisons": eval_res["model_comparisons"],
            "all_model_predictions": all_model_preds,
            "has_sufficient_data": ts.get("has_sufficient_data", True),
            "total_occurrences": ts.get("total_occurrences", 0)
        }

        docs_to_save.append(forecast_doc)
        forecasts[sk] = forecast_doc

    # Batch save into database
    try:
        SkillForecastModel.save_forecasts_batch(docs_to_save)
        logger.info(f"Saved {len(docs_to_save)} forecast documents into MongoDB.")
    except Exception as e:
        logger.warning(f"Batch forecast save warning: {e}")

    _ALL_FORECASTS_CACHE = {"timestamp": now_ts, "data": forecasts}
    return forecasts

@forecasting_bp.route('/categories', methods=['GET', 'OPTIONS'])
def get_categories():
    """Return available skill categories and skill counts per category."""
    if request.method == 'OPTIONS':
        return ('', 204)

    forecasts = _generate_all_forecasts()
    categories_dict = {}

    for cat in SkillTaxonomy.CATEGORIES:
        categories_dict[cat] = 0

    for f in forecasts.values():
        c = f.get("category", "General Technical")
        if c in categories_dict:
            categories_dict[c] += 1
        else:
            categories_dict[c] = 1

    return jsonify({
        "success": True,
        "data": {
            "categories": SkillTaxonomy.CATEGORIES,
            "category_counts": categories_dict
        }
    }), 200

@forecasting_bp.route('/top-skills', methods=['GET', 'OPTIONS'])
def get_top_skills():
    """
    Get top rising, stable, declining, and emerging skills.
    Supports ?category=... and ?limit=... query parameters.
    """
    if request.method == 'OPTIONS':
        return ('', 204)

    category = request.args.get('category', '').strip()
    limit = int(request.args.get('limit', 8))

    forecasts = _generate_all_forecasts()
    all_list = list(forecasts.values())

    if category and category.lower() != "all categories":
        all_list = [f for f in all_list if f.get("category", "").lower() == category.lower()]

    rising = [f for f in all_list if f["trend"] == "RISING"]
    stable = [f for f in all_list if f["trend"] == "STABLE"]
    declining = [f for f in all_list if f["trend"] == "DECLINING"]
    emerging = [f for f in all_list if f["trend"] == "EMERGING"]

    # Sort rising by growth_diff descending
    rising.sort(key=lambda x: x.get("growth_diff", 0.0), reverse=True)
    # Sort stable by current_demand descending
    stable.sort(key=lambda x: x.get("current_demand", 0.0), reverse=True)
    # Sort emerging by relative growth
    emerging.sort(key=lambda x: float(str(x.get("relative_growth", "0")).replace("%", "").replace("+", "") or 0), reverse=True)
    # Sort declining by growth_diff ascending (most negative first)
    declining.sort(key=lambda x: x.get("growth_diff", 0.0))

    return jsonify({
        "success": True,
        "data": {
            "category": category or "All Categories",
            "rising_skills": rising[:limit],
            "stable_skills": stable[:limit],
            "declining_skills": declining[:limit],
            "emerging_skills": emerging[:limit]
        }
    }), 200

@forecasting_bp.route('/skill/<skill_name>', methods=['GET', 'OPTIONS'])
def get_skill_forecast(skill_name):
    """
    Get detailed historical time series (2023-2026) and 36-month forecast for a specific skill.
    Strictly validates skill against SkillRegistry before accessing historical data or executing models.
    Supports ?horizon=6|12|24|36 and ?model=auto|naive|moving_average|linear_regression|exponential_smoothing|all.
    """
    if request.method == 'OPTIONS':
        return ('', 204)

    # 1. STRICT SKILL VALIDATION AGAINST TRUSTED REGISTRY
    validation = SkillRegistry.validate_skill(skill_name)
    if not validation["is_valid"]:
        return jsonify({
            "success": False,
            "error": "INVALID_SKILL",
            "message": validation.get("message") or f"The entered term '{skill_name}' is not a recognized technical skill.",
            "suggestions": validation.get("suggestions", ["Python", "Java", "JavaScript"])
        }), 400

    canonical_key = validation["canonical_key"]
    canonical_display = validation["display_name"]
    category = validation["category"]
    sub_categories = validation["sub_categories"]

    requested_horizon = int(request.args.get('horizon', 36))
    if requested_horizon not in (3, 6, 12, 24, 36):
        requested_horizon = 36

    requested_model = request.args.get('model', 'auto').lower().strip()

    forecasts = _generate_all_forecasts()

    target_forecast = None
    if canonical_key in forecasts:
        target_forecast = forecasts[canonical_key]
    else:
        # Check direct lowercase key or exact title match
        for k, f in forecasts.items():
            if k == canonical_key or k.lower() == canonical_key.lower():
                target_forecast = f
                break

    if not target_forecast:
        # Valid technical skill from trusted registry that is unobserved in this specific vacancy dataset
        last_p = SkillFrequencyEngine.MAX_HISTORICAL_PERIOD
        future_p = PreprocessingService.generate_forecast_periods(last_p, horizon=requested_horizon)
        return jsonify({
            "success": True,
            "data": {
                "forecast": {
                    "skill": canonical_display,
                    "skill_key": canonical_key,
                    "category": category,
                    "sub_categories": sub_categories,
                    "horizon": f"{requested_horizon}M",
                    "current_demand": 0.0,
                    "predicted_demand": 0.0,
                    "lower_bound": 0.0,
                    "upper_bound": 0.0,
                    "confidence_label": "Insufficient historical observations in dataset",
                    "trend": "STABLE",
                    "trend_label": "⚪ Insufficient Data",
                    "growth_rate": "0.0%",
                    "relative_growth": "0.0%",
                    "model_name": "Naive Baseline",
                    "mae": 0.0,
                    "rmse": 0.0,
                    "mape": 0.0,
                    "reliability": "INSUFFICIENT_HISTORICAL_DATA",
                    "periods": SkillFrequencyEngine.get_continuous_timeline()[-12:],
                    "historical_rates": [0.0] * 12,
                    "forecast_periods": future_p,
                    "forecast_rates": [0.0] * requested_horizon,
                    "forecast_lower_bounds": [0.0] * requested_horizon,
                    "forecast_upper_bounds": [0.0] * requested_horizon,
                    "model_comparisons": [],
                    "all_model_predictions": {},
                    "has_sufficient_data": False,
                    "notice": f"The technical skill '{canonical_display}' is recognized, but has insufficient historical records in the active vacancy database to produce a high-confidence forecast."
                }
            }
        }), 200

    # Slice forecast arrays to requested horizon
    fc_copy = dict(target_forecast)
    # Ensure display name adheres to canonical registry display name
    fc_copy["skill"] = canonical_display
    fc_copy["category"] = category
    fc_copy["sub_categories"] = sub_categories
    fc_copy["horizon"] = f"{requested_horizon}M"
    fc_copy["forecast_periods"] = target_forecast["forecast_periods"][:requested_horizon]
    fc_copy["forecast_rates"] = target_forecast["forecast_rates"][:requested_horizon]
    fc_copy["forecast_lower_bounds"] = target_forecast["forecast_lower_bounds"][:requested_horizon]
    fc_copy["forecast_upper_bounds"] = target_forecast["forecast_upper_bounds"][:requested_horizon]
    fc_copy["predicted_demand"] = fc_copy["forecast_rates"][-1] if fc_copy["forecast_rates"] else fc_copy["current_demand"]

    # Slice all model predictions
    sliced_models = {}
    for m_name, preds in target_forecast.get("all_model_predictions", {}).items():
        sliced_models[m_name] = preds[:requested_horizon]
    fc_copy["all_model_predictions"] = sliced_models

    # If a specific algorithm was requested
    model_name_map = {
        "naive": "Naive Baseline",
        "moving_average": "Moving Average",
        "linear_regression": "Linear Regression",
        "exponential_smoothing": "Exponential Smoothing"
    }
    if requested_model in model_name_map:
        specific_name = model_name_map[requested_model]
        if specific_name in sliced_models:
            fc_copy["forecast_rates"] = sliced_models[specific_name]
            fc_copy["model_name"] = specific_name
            fc_copy["predicted_demand"] = fc_copy["forecast_rates"][-1]

    return jsonify({
        "success": True,
        "data": {
            "forecast": fc_copy
        }
    }), 200

@forecasting_bp.route('/compare', methods=['GET', 'OPTIONS'])
def compare_skills():
    """
    Compare multiple skills side-by-side.
    Query: ?skills=python,java,sql,react&horizon=36
    """
    if request.method == 'OPTIONS':
        return ('', 204)

    raw_skills = request.args.get('skills', 'python,sql,react,aws')
    raw_skill_list = [s.strip() for s in raw_skills.split(',') if s.strip()]
    horizon = int(request.args.get('horizon', 36))
    if horizon not in (6, 12, 24, 36):
        horizon = 36

    # Validate each skill against SkillRegistry
    valid_skills_info = []
    invalid_skills = []
    accumulated_suggestions = []

    for s in raw_skill_list:
        v = SkillRegistry.validate_skill(s)
        if v["is_valid"]:
            valid_skills_info.append(v)
        else:
            invalid_skills.append(s)
            accumulated_suggestions.extend(v.get("suggestions", []))

    if not valid_skills_info:
        # None of the entered skills are recognized
        return jsonify({
            "success": False,
            "error": "INVALID_SKILL",
            "message": f"None of the entered terms ({', '.join(invalid_skills)}) are recognized technical skills.",
            "suggestions": list(dict.fromkeys(accumulated_suggestions))[:3] or ["Python", "Java", "JavaScript"]
        }), 400

    forecasts = _generate_all_forecasts()
    comparison_results = []
    periods = []

    for v in valid_skills_info:
        canonical_key = v["canonical_key"]
        canonical_display = v["display_name"]
        target = forecasts.get(canonical_key)
        if target:
            if not periods:
                periods = target.get("forecast_periods", [])[:horizon]
            comparison_results.append({
                "skill": canonical_display,
                "category": v.get("category", target.get("category", "General Technical")),
                "current_demand": target.get("current_demand", 0.0),
                "predicted_demand": target.get("forecast_rates", [])[horizon - 1] if len(target.get("forecast_rates", [])) >= horizon else target.get("predicted_demand", 0.0),
                "growth_rate": target.get("growth_rate", "+0.0%"),
                "trend": target.get("trend", "STABLE"),
                "trend_label": target.get("trend_label", "Stable"),
                "model_name": target.get("model_name", "Exponential Smoothing"),
                "mae": target.get("mae", 0.0),
                "reliability": target.get("reliability", "HIGH"),
                "forecast_rates": target.get("forecast_rates", [])[:horizon]
            })

    response_data = {
        "horizon": f"{horizon}M",
        "forecast_periods": periods,
        "skills": comparison_results
    }
    if invalid_skills:
        response_data["ignored_invalid_skills"] = invalid_skills

    return jsonify({
        "success": True,
        "data": response_data
    }), 200

@forecasting_bp.route('/recommendations', methods=['GET', 'OPTIONS'])
@jwt_required
def get_personalized_forecast_recommendations():
    """
    Get personalized future skill recommendations combining candidate resume gap + market demand trends.
    """
    if request.method == 'OPTIONS':
        return ('', 204)
    user = getattr(request, 'current_user', None)
    user_id = str(user.get("_id", user.get("id")))

    my_resumes = ResumeModel.find_by_user(user_id)
    if not my_resumes:
        return jsonify({"success": False, "message": "Please upload a resume first."}), 400

    latest_resume_id = str(my_resumes[0].get("_id"))

    force_refresh = request.args.get('refresh', '').lower() in ['true', '1', 'yes']
    rec_cache_key = (user_id, latest_resume_id)
    now_ts = time.time()
    if not force_refresh and rec_cache_key in _USER_FORECAST_REC_CACHE:
        entry = _USER_FORECAST_REC_CACHE[rec_cache_key]
        if now_ts - entry["timestamp"] < 1800:
            return jsonify(entry["data"]), 200

    analysis_doc = ResumeAnalysisModel.find_by_resume_id(latest_resume_id)
    if not analysis_doc:
        return jsonify({"success": False, "message": "Please analyze your resume first."}), 400

    analysis_json = ResumeAnalysisModel.to_json(analysis_doc)

    # MANDATORY VALIDATION GUARD
    if analysis_json.get("validation_status") != "VALID_RESUME" or analysis_json.get("resume_score") is None:
        return jsonify({
            "success": False,
            "status": "FORECAST_BLOCKED",
            "message": "Personalized forecasting is unavailable because the uploaded document is not a valid resume.",
            "error": "INVALID_DOCUMENT"
        }), 400

    # Fetch candidate profile & candidate skills
    from app.services.role_inference_service import RoleInferenceEngine
    candidate_profile = RoleInferenceEngine.infer_candidate_profile(analysis_json)
    candidate_skills = analysis_json.get("technical_skills", []) + analysis_json.get("soft_skills", [])

    all_jobs = JobService.get_all_jobs()
    target_job = all_jobs[0] if all_jobs else {}
    user_json = UserModel.to_json(user)

    gap_res = SkillGapEngine.analyze_skill_gap(analysis_json, user_json, target_job)
    forecasts = _generate_all_forecasts(force_refresh=force_refresh)

    recommendations = ForecastingRecommendationEngine.generate_recommendations(gap_res, forecasts, candidate_profile, candidate_skills)

    response_payload = {
        "success": True,
        "data": {
            "target_role": candidate_profile.get("professional_identity", target_job.get("title", "Professional")),
            "domain": candidate_profile.get("professional_domain", "GENERAL_PROFESSIONAL"),
            "recommendations": recommendations
        }
    }

    while len(_USER_FORECAST_REC_CACHE) >= 20:
        oldest_k = next(iter(_USER_FORECAST_REC_CACHE))
        _USER_FORECAST_REC_CACHE.pop(oldest_k, None)

    _USER_FORECAST_REC_CACHE[rec_cache_key] = {
        "timestamp": now_ts,
        "data": response_payload
    }

    return jsonify(response_payload), 200
