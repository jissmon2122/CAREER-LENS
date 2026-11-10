from datetime import datetime, timezone
from bson import ObjectId
from app.db import get_collection

class SkillForecastModel:
    """Skill Forecast Collection Model & Operations."""

    COLLECTION_NAME = 'skill_forecasts'
    _in_memory_store = {}

    @staticmethod
    def get_collection():
        return get_collection(SkillForecastModel.COLLECTION_NAME)

    @staticmethod
    def save_forecast(data):
        coll = SkillForecastModel.get_collection()
        now = datetime.now(timezone.utc)
        skill_key = data.get("skill", "").lower().strip()

        doc = {
            "skill": skill_key,
            "skill_display": data.get("skill_display") or skill_key.title(),
            "category": data.get("category", "General Technical"),
            "sub_categories": data.get("sub_categories", []),
            "horizon": data.get("horizon", "36M"),
            "current_demand": data.get("current_demand"),
            "predicted_demand": data.get("predicted_demand"),
            "lower_bound": data.get("lower_bound"),
            "upper_bound": data.get("upper_bound"),
            "confidence_label": data.get("confidence_label"),
            "trend": data.get("trend"),
            "trend_label": data.get("trend_label"),
            "growth_rate": data.get("growth_rate"),
            "relative_growth": data.get("relative_growth"),
            "model_name": data.get("model_name"),
            "mae": data.get("mae"),
            "rmse": data.get("rmse"),
            "mape": data.get("mape"),
            "reliability": data.get("reliability"),
            "historical_rates": data.get("historical_rates", []),
            "periods": data.get("periods", []),
            "forecast_periods": data.get("forecast_periods", []),
            "forecast_rates": data.get("forecast_rates", []),
            "forecast_lower_bounds": data.get("forecast_lower_bounds", []),
            "forecast_upper_bounds": data.get("forecast_upper_bounds", []),
            "model_comparisons": data.get("model_comparisons", []),
            "all_model_predictions": data.get("all_model_predictions", {}),
            "algorithm_version": "2.0",
            "updated_at": now
        }

        if coll is not None:
            coll.update_one(
                {"skill": skill_key},
                {"$set": doc},
                upsert=True
            )
            return coll.find_one({"skill": skill_key})
        else:
            doc["_id"] = ObjectId()
            SkillForecastModel._in_memory_store[skill_key] = doc
            return doc

    @staticmethod
    def get_all_forecasts():
        coll = SkillForecastModel.get_collection()
        if coll is not None:
            docs = list(coll.find({}))
            for d in docs:
                if "_id" in d:
                    d["_id"] = str(d["_id"])
                if "updated_at" in d and hasattr(d["updated_at"], "isoformat"):
                    d["updated_at"] = d["updated_at"].isoformat()
            return docs
        return list(SkillForecastModel._in_memory_store.values())

    @staticmethod
    def save_forecasts_batch(forecast_docs):
        if not forecast_docs:
            return
        coll = SkillForecastModel.get_collection()
        now = datetime.now(timezone.utc)
        if coll is not None:
            from pymongo import UpdateOne
            ops = []
            for data in forecast_docs:
                skill_key = data.get("skill", "").lower().strip()
                doc = {
                    "skill": skill_key,
                    "skill_display": data.get("skill_display") or skill_key.title(),
                    "category": data.get("category", "General Technical"),
                    "sub_categories": data.get("sub_categories", []),
                    "horizon": data.get("horizon", "36M"),
                    "current_demand": data.get("current_demand"),
                    "predicted_demand": data.get("predicted_demand"),
                    "lower_bound": data.get("lower_bound"),
                    "upper_bound": data.get("upper_bound"),
                    "confidence_label": data.get("confidence_label"),
                    "trend": data.get("trend"),
                    "trend_label": data.get("trend_label"),
                    "growth_rate": data.get("growth_rate"),
                    "relative_growth": data.get("relative_growth"),
                    "model_name": data.get("model_name"),
                    "mae": data.get("mae"),
                    "rmse": data.get("rmse"),
                    "mape": data.get("mape"),
                    "reliability": data.get("reliability"),
                    "historical_rates": data.get("historical_rates", []),
                    "periods": data.get("periods", []),
                    "forecast_periods": data.get("forecast_periods", []),
                    "forecast_rates": data.get("forecast_rates", []),
                    "forecast_lower_bounds": data.get("forecast_lower_bounds", []),
                    "forecast_upper_bounds": data.get("forecast_upper_bounds", []),
                    "model_comparisons": data.get("model_comparisons", []),
                    "all_model_predictions": data.get("all_model_predictions", {}),
                    "algorithm_version": "2.0",
                    "updated_at": now
                }
                ops.append(UpdateOne({"skill": skill_key}, {"$set": doc}, upsert=True))
            if ops:
                try:
                    coll.bulk_write(ops, ordered=False)
                except Exception:
                    pass
        else:
            for data in forecast_docs:
                skill_key = data.get("skill", "").lower().strip()
                SkillForecastModel._in_memory_store[skill_key] = data

    @staticmethod
    def find_by_skill(skill):
        if not skill:
            return None
        sk_key = skill.lower().strip()
        coll = SkillForecastModel.get_collection()

        if coll is not None:
            return coll.find_one({"skill": sk_key})
        return SkillForecastModel._in_memory_store.get(sk_key)

    @staticmethod
    def to_json(doc):
        if not doc:
            return None
        return {
            "id": str(doc.get("_id", "")),
            "skill": doc.get("skill_display") or doc.get("skill", "").title(),
            "skill_key": doc.get("skill", "").lower(),
            "category": doc.get("category", "General Technical"),
            "sub_categories": doc.get("sub_categories", []),
            "horizon": doc.get("horizon", "36M"),
            "current_demand": doc.get("current_demand"),
            "predicted_demand": doc.get("predicted_demand"),
            "lower_bound": doc.get("lower_bound"),
            "upper_bound": doc.get("upper_bound"),
            "confidence_label": doc.get("confidence_label"),
            "trend": doc.get("trend"),
            "trend_label": doc.get("trend_label"),
            "growth_rate": doc.get("growth_rate"),
            "relative_growth": doc.get("relative_growth"),
            "model_name": doc.get("model_name"),
            "mae": doc.get("mae"),
            "rmse": doc.get("rmse"),
            "mape": doc.get("mape"),
            "reliability": doc.get("reliability"),
            "historical_rates": doc.get("historical_rates", []),
            "periods": doc.get("periods", []),
            "forecast_periods": doc.get("forecast_periods", []),
            "forecast_rates": doc.get("forecast_rates", []),
            "forecast_lower_bounds": doc.get("forecast_lower_bounds", []),
            "forecast_upper_bounds": doc.get("forecast_upper_bounds", []),
            "model_comparisons": doc.get("model_comparisons", []),
            "all_model_predictions": doc.get("all_model_predictions", {}),
            "updated_at": str(doc.get("updated_at", ""))
        }
