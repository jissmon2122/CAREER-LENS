import math

class BaseForecastModel:
    """Abstract Base Class for Time-Series Skill Demand Forecasting Models."""
    def fit(self, history):
        raise NotImplementedError
    def predict(self, horizon=3):
        raise NotImplementedError

class BaselineNaiveModel(BaseForecastModel):
    """Naive Baseline Model: Predicts the last observed demand rate for all future periods."""
    def fit(self, history):
        self.last_val = history[-1] if history else 0.0
        return self

    def predict(self, horizon=3):
        return [round(self.last_val, 2) for _ in range(horizon)]

class MovingAverageModel(BaseForecastModel):
    """Moving Average Model: Predicts using windowed moving average of recent observations."""
    def __init__(self, window=3):
        self.window = window

    def fit(self, history):
        if not history:
            self.ma_val = 0.0
        else:
            recent = history[-self.window:]
            self.ma_val = sum(recent) / len(recent)
        return self

    def predict(self, horizon=3):
        return [round(self.ma_val, 2) for _ in range(horizon)]

class LinearTrendModel(BaseForecastModel):
    """Linear Trend Model: Ordinary Least Squares (OLS) linear trend extrapolation."""
    def fit(self, history):
        self.history = history
        n = len(history)
        if n < 2:
            self.slope = 0.0
            self.intercept = history[0] if n == 1 else 0.0
            return self

        x = list(range(n))
        y = history
        mean_x = sum(x) / n
        mean_y = sum(y) / n

        num = sum((x[i] - mean_x) * (y[i] - mean_y) for i in range(n))
        den = sum((x[i] - mean_x) ** 2 for i in range(n))

        if den == 0:
            self.slope = 0.0
            self.intercept = mean_y
        else:
            self.slope = num / den
            self.intercept = mean_y - self.slope * mean_x

        return self

    def predict(self, horizon=3):
        n = len(self.history)
        preds = []
        for h in range(1, horizon + 1):
            val = self.intercept + self.slope * (n - 1 + h)
            preds.append(round(max(0.0, val), 2))
        return preds

class ExponentialSmoothingModel(BaseForecastModel):
    """Holt's Linear Exponential Smoothing Model with level (alpha) and trend (beta)."""
    def __init__(self, alpha=0.4, beta=0.2):
        self.alpha = alpha
        self.beta = beta

    def fit(self, history):
        self.history = history
        if not history:
            self.level = 0.0
            self.trend = 0.0
            return self
        if len(history) == 1:
            self.level = history[0]
            self.trend = 0.0
            return self

        # Initialize level & trend
        level = history[0]
        trend = history[1] - history[0]

        for i in range(1, len(history)):
            val = history[i]
            last_level = level
            level = self.alpha * val + (1 - self.alpha) * (level + trend)
            trend = self.beta * (level - last_level) + (1 - self.beta) * trend

        self.level = level
        self.trend = trend
        return self

    def predict(self, horizon=3):
        preds = []
        for h in range(1, horizon + 1):
            val = self.level + h * self.trend
            preds.append(round(max(0.0, val), 2))
        return preds
