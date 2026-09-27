from datetime import datetime
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
        now = datetime.utcnow()

        skill_key = data.get("skill", "").lower().strip()

        doc = {
            "skill": skill_key,
            "horizon": data.get("horizon", "6M"),
            "current_demand": data.get("current_demand"),
            "predicted_demand": data.get("predicted_demand"),
            "lower_bound": data.get("lower_bound"),
            "upper_bound": data.get("upper_bound"),
            "trend": data.get("trend"),
            "growth_rate": data.get("growth_rate"),
            "model_name": data.get("model_name"),
            "mae": data.get("mae"),
            "rmse": data.get("rmse"),
            "reliability": data.get("reliability"),
            "historical_rates": data.get("historical_rates", []),
            "periods": data.get("periods", []),
            "forecast_periods": data.get("forecast_periods", []),
            "forecast_rates": data.get("forecast_rates", []),
            "algorithm_version": "1.0",
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
            "skill": doc.get("skill"),
            "horizon": doc.get("horizon"),
            "current_demand": doc.get("current_demand"),
            "predicted_demand": doc.get("predicted_demand"),
            "lower_bound": doc.get("lower_bound"),
            "upper_bound": doc.get("upper_bound"),
            "trend": doc.get("trend"),
            "growth_rate": doc.get("growth_rate"),
            "model_name": doc.get("model_name"),
            "mae": doc.get("mae"),
            "rmse": doc.get("rmse"),
            "reliability": doc.get("reliability"),
            "historical_rates": doc.get("historical_rates", []),
            "periods": doc.get("periods", []),
            "forecast_periods": doc.get("forecast_periods", []),
            "forecast_rates": doc.get("forecast_rates", []),
            "updated_at": str(doc.get("updated_at", ""))
        }
