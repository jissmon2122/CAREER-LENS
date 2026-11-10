import math

class BaseForecastModel:
    """Abstract Base Class for Time-Series Skill Demand Forecasting Models."""
    def fit(self, history):
        raise NotImplementedError
    def predict(self, horizon=36):
        raise NotImplementedError
    def predict_with_intervals(self, horizon=36, alpha=0.05):
        raise NotImplementedError

class BaselineNaiveModel(BaseForecastModel):
    """
    Naive Baseline Model:
    Predicts the last observed demand rate for all future periods:
        y_{t+h} = y_t
    Standard error based on historical sample standard deviation.
    """
    def __init__(self):
        self.last_val = 0.0
        self.std_err = 1.0

    def fit(self, history):
        if not history:
            self.last_val = 0.0
            self.std_err = 1.0
        else:
            self.last_val = float(history[-1])
            if len(history) > 1:
                # Historical 1-step errors
                diffs = [history[i] - history[i - 1] for i in range(1, len(history))]
                variance = sum(d ** 2 for d in diffs) / len(diffs)
                self.std_err = max(0.5, math.sqrt(variance))
            else:
                self.std_err = 1.0
        return self

    def predict(self, horizon=36):
        val = round(max(0.0, min(100.0, self.last_val)), 2)
        return [val for _ in range(horizon)]

    def predict_with_intervals(self, horizon=36):
        preds = self.predict(horizon)
        lower = []
        upper = []
        # Prediction interval grows with sqrt(h)
        for h in range(1, horizon + 1):
            margin = 1.96 * self.std_err * math.sqrt(h / 3.0)
            low = round(max(0.0, preds[h - 1] - margin), 2)
            up = round(min(100.0, preds[h - 1] + margin), 2)
            lower.append(low)
            upper.append(up)
        return preds, lower, upper

class MovingAverageModel(BaseForecastModel):
    """
    Moving Average Model:
    Forecasts future demand as the rolling average of the recent window observations:
        y_{t+h} = (1 / w) * sum_{i=0}^{w-1} y_{t-i}
    Includes multi-step smoothing with recency weighting.
    """
    def __init__(self, window=6):
        self.window = window
        self.ma_val = 0.0
        self.std_err = 1.0

    def fit(self, history):
        if not history:
            self.ma_val = 0.0
            self.std_err = 1.0
        else:
            w = min(len(history), self.window)
            recent = history[-w:]
            self.ma_val = sum(recent) / w
            if len(history) > 1:
                diffs = [history[i] - self.ma_val for i in range(max(0, len(history) - w), len(history))]
                variance = sum(d ** 2 for d in diffs) / max(1, len(diffs))
                self.std_err = max(0.5, math.sqrt(variance))
            else:
                self.std_err = 1.0
        return self

    def predict(self, horizon=36):
        val = round(max(0.0, min(100.0, self.ma_val)), 2)
        return [val for _ in range(horizon)]

    def predict_with_intervals(self, horizon=36):
        preds = self.predict(horizon)
        lower = []
        upper = []
        for h in range(1, horizon + 1):
            margin = 1.96 * self.std_err * math.sqrt(1.0 + (h / float(self.window)))
            low = round(max(0.0, preds[h - 1] - margin), 2)
            up = round(min(100.0, preds[h - 1] + margin), 2)
            lower.append(low)
            upper.append(up)
        return preds, lower, upper

class LinearTrendModel(BaseForecastModel):
    """
    Linear Trend Model:
    Ordinary Least Squares (OLS) linear trend regression with asymptotic dampening.
    Formula:
        y_{t+h} = beta_0 + beta_1 * (n - 1 + sum_{i=1}^h gamma^(i-1))
    Where gamma = 0.96 prevents unrealistic linear explosion over 36 periods,
    and bounds predictions strictly to [0.0%, 100.0%].
    """
    def __init__(self, dampening=0.96):
        self.dampening = dampening
        self.slope = 0.0
        self.intercept = 0.0
        self.n = 0
        self.std_err = 1.0

    def fit(self, history):
        self.n = len(history)
        if self.n < 2:
            self.slope = 0.0
            self.intercept = history[0] if self.n == 1 else 0.0
            self.std_err = 1.0
            return self

        x = list(range(self.n))
        y = history
        mean_x = sum(x) / self.n
        mean_y = sum(y) / self.n

        num = sum((x[i] - mean_x) * (y[i] - mean_y) for i in range(self.n))
        den = sum((x[i] - mean_x) ** 2 for i in range(self.n))

        if den == 0:
            self.slope = 0.0
            self.intercept = mean_y
            self.std_err = 1.0
        else:
            self.slope = num / den
            self.intercept = mean_y - self.slope * mean_x

            # Calculate residual standard error
            residuals = [y[i] - (self.intercept + self.slope * x[i]) for i in range(self.n)]
            ss_res = sum(r ** 2 for r in residuals)
            df = max(1, self.n - 2)
            self.std_err = max(0.5, math.sqrt(ss_res / df))

        return self

    def predict(self, horizon=36):
        if self.n == 0:
            return [0.0 for _ in range(horizon)]

        preds = []
        effective_step = float(self.n - 1)

        for h in range(1, horizon + 1):
            # Dampen step increments for long horizons to avoid runaway trends
            step_increment = self.dampening ** (h - 1)
            effective_step += step_increment
            val = self.intercept + self.slope * effective_step
            clamped = round(max(0.0, min(100.0, val)), 2)
            preds.append(clamped)

        return preds

    def predict_with_intervals(self, horizon=36):
        preds = self.predict(horizon)
        lower = []
        upper = []

        for h in range(1, horizon + 1):
            # Regression prediction standard error expanding over horizon
            h_factor = math.sqrt(1.0 + (1.0 / max(1, self.n)) + ((h ** 2) / float(max(1, self.n * 5))))
            margin = 1.96 * self.std_err * h_factor
            low = round(max(0.0, preds[h - 1] - margin), 2)
            up = round(min(100.0, preds[h - 1] + margin), 2)
            lower.append(low)
            upper.append(up)

        return preds, lower, upper

class ExponentialSmoothingModel(BaseForecastModel):
    """
    Damped Holt's Linear Exponential Smoothing Model (Gardner & McKenzie):
        l_t = alpha * y_t + (1 - alpha) * (l_{t-1} + phi * b_{t-1})
        b_t = beta * (l_t - l_{t-1}) + (1 - beta) * phi * b_{t-1}
        y_{t+h} = l_t + (sum_{i=1}^h phi^i) * b_t
    Prevents overshooting and guarantees smooth saturation for up to 36 periods.
    """
    def __init__(self, alpha=0.35, beta=0.15, phi=0.92):
        self.alpha = alpha
        self.beta = beta
        self.phi = phi
        self.level = 0.0
        self.trend = 0.0
        self.std_err = 1.0

    def fit(self, history):
        if not history:
            self.level = 0.0
            self.trend = 0.0
            self.std_err = 1.0
            return self

        if len(history) == 1:
            self.level = float(history[0])
            self.trend = 0.0
            self.std_err = 1.0
            return self

        # Robust initialization
        level = float(history[0])
        trend = float(history[1] - history[0])
        one_step_errors = []

        for i in range(1, len(history)):
            val = float(history[i])
            pred_val = level + self.phi * trend
            one_step_errors.append(val - pred_val)

            last_level = level
            level = self.alpha * val + (1.0 - self.alpha) * (level + self.phi * trend)
            trend = self.beta * (level - last_level) + (1.0 - self.beta) * self.phi * trend

        self.level = level
        self.trend = trend

        if one_step_errors:
            mse = sum(e ** 2 for e in one_step_errors) / len(one_step_errors)
            self.std_err = max(0.5, math.sqrt(mse))
        else:
            self.std_err = 1.0

        return self

    def predict(self, horizon=36):
        preds = []
        cumulative_phi = 0.0

        for h in range(1, horizon + 1):
            cumulative_phi += self.phi ** h
            val = self.level + cumulative_phi * self.trend
            clamped = round(max(0.0, min(100.0, val)), 2)
            preds.append(clamped)

        return preds

    def predict_with_intervals(self, horizon=36):
        preds = self.predict(horizon)
        lower = []
        upper = []

        cumulative_var_factor = 0.0
        for h in range(1, horizon + 1):
            cumulative_var_factor += (self.phi ** (2 * (h - 1)))
            margin = 1.96 * self.std_err * math.sqrt(max(1.0, cumulative_var_factor))
            low = round(max(0.0, preds[h - 1] - margin), 2)
            up = round(min(100.0, preds[h - 1] + margin), 2)
            lower.append(low)
            upper.append(up)

        return preds, lower, upper
