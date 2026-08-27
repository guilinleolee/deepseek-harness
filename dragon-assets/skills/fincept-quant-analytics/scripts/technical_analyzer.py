"""
Technical Analysis Analyzer
CFA级别技术指标计算
"""

import numpy as np
from typing import List, Optional, Union
from collections import defaultdict


class TechnicalAnalyzer:
    """
    技术指标分析器

    支持：
    - 移动平均线 (SMA, EMA, WMA)
    - 动量指标 (RSI, MACD, Stochastic)
    - 波动率指标 (Bollinger Bands, ATR)
    - 趋势指标 (ADX, SuperTrend)
    - 交易信号生成
    """

    def __init__(self):
        self.defaults = {
            "rsi_period": 14,
            "macd_fast": 12,
            "macd_slow": 26,
            "macd_signal": 9,
            "bb_period": 20,
            "bb_std": 2,
            "atr_period": 14,
            "stoch_period": 14,
        }

    def calculate(
        self,
        prices: Union[List[float], np.ndarray],
        indicators: List[str],
    ) -> dict:
        """
        计算技术指标

        Args:
            prices: 价格序列
            indicators: 要计算的指标列表
                可选: sma, ema, wma, rsi, macd, bbands, atr, stoch, adx

        Returns:
            dict: 技术指标结果
        """
        prices = np.array(prices)
        results = {}

        for indicator in indicators:
            indicator_lower = indicator.lower()

            if indicator_lower == "sma":
                results["sma"] = self._sma(prices, 20)
            elif indicator_lower == "ema":
                results["ema"] = self._ema(prices, 12)
            elif indicator_lower == "wma":
                results["wma"] = self._wma(prices, 20)
            elif indicator_lower == "rsi":
                results["rsi"] = self._rsi(prices, self.defaults["rsi_period"])
            elif indicator_lower == "macd":
                results["macd"] = self._macd(
                    prices,
                    self.defaults["macd_fast"],
                    self.defaults["macd_slow"],
                    self.defaults["macd_signal"],
                )
            elif indicator_lower == "bbands":
                results["bbands"] = self._bollinger_bands(
                    prices, self.defaults["bb_period"], self.defaults["bb_std"]
                )
            elif indicator_lower == "atr":
                results["atr"] = self._atr(prices, self.defaults["atr_period"])
            elif indicator_lower == "stoch":
                results["stoch"] = self._stochastic(
                    prices, self.defaults["stoch_period"]
                )
            elif indicator_lower == "adx":
                results["adx"] = self._adx(prices, 14)
            else:
                results[indicator] = None

        return results

    def _sma(self, prices: np.ndarray, period: int) -> dict:
        """简单移动平均"""
        if len(prices) < period:
            return {"value": None, "signal": "neutral"}

        sma = np.convolve(prices, np.ones(period) / period, mode="valid")
        current_sma = sma[-1]
        current_price = prices[-1]

        if current_price > current_sma:
            signal = "bullish"
        elif current_price < current_sma:
            signal = "bearish"
        else:
            signal = "neutral"

        return {"value": round(current_sma, 2), "signal": signal, "history": sma.tolist()}

    def _ema(self, prices: np.ndarray, period: int) -> dict:
        """指数移动平均"""
        if len(prices) < period:
            return {"value": None, "signal": "neutral"}

        ema = [prices[0]]
        multiplier = 2 / (period + 1)

        for price in prices[1:]:
            ema.append((price - ema[-1]) * multiplier + ema[-1])

        current_ema = ema[-1]
        current_price = prices[-1]

        if current_price > current_ema:
            signal = "bullish"
        elif current_price < current_ema:
            signal = "bearish"
        else:
            signal = "neutral"

        return {"value": round(current_ema, 2), "signal": signal, "history": ema}

    def _wma(self, prices: np.ndarray, period: int) -> dict:
        """加权移动平均"""
        if len(prices) < period:
            return {"value": None, "signal": "neutral"}

        weights = np.arange(1, period + 1)
        wma = np.convolve(prices[-period:], weights, mode="valid") / weights.sum()

        current_wma = wma[-1]
        current_price = prices[-1]

        if current_price > current_wma:
            signal = "bullish"
        elif current_price < current_wma:
            signal = "bearish"
        else:
            signal = "neutral"

        return {"value": round(current_wma, 2), "signal": signal}

    def _rsi(self, prices: np.ndarray, period: int = 14) -> dict:
        """相对强弱指数"""
        if len(prices) < period + 1:
            return {"value": None, "signal": "neutral"}

        deltas = np.diff(prices)
        gains = np.where(deltas > 0, deltas, 0)
        losses = np.where(deltas < 0, -deltas, 0)

        avg_gain = np.mean(gains[-period:])
        avg_loss = np.mean(losses[-period:])

        if avg_loss == 0:
            rsi = 100
        else:
            rs = avg_gain / avg_loss
            rsi = 100 - (100 / (1 + rs))

        if rsi > 70:
            signal = "overbought"
        elif rsi < 30:
            signal = "oversold"
        else:
            signal = "neutral"

        return {"value": round(rsi, 2), "signal": signal}

    def _macd(
        self, prices: np.ndarray, fast: int, slow: int, signal: int
    ) -> dict:
        """MACD (Moving Average Convergence Divergence)"""
        if len(prices) < slow + signal:
            return {"macd": None, "signal_line": None, "histogram": None, "signal": "neutral"}

        # 计算EMA
        ema_fast = self._calc_ema(prices, fast)
        ema_slow = self._calc_ema(prices, slow)

        macd_line = ema_fast - ema_slow
        signal_line = self._calc_ema(macd_line, signal)
        histogram = macd_line - signal_line

        current_macd = macd_line[-1]
        current_signal = signal_line[-1]

        if current_macd > current_signal and histogram[-1] > 0:
            signal = "bullish"
        elif current_macd < current_signal and histogram[-1] < 0:
            signal = "bearish"
        else:
            signal = "neutral"

        return {
            "macd": round(current_macd, 4),
            "signal_line": round(current_signal, 4),
            "histogram": round(histogram[-1], 4),
            "signal": signal,
        }

    def _calc_ema(self, prices: np.ndarray, period: int) -> np.ndarray:
        """计算EMA序列"""
        multiplier = 2 / (period + 1)
        ema = [prices[0]]

        for price in prices[1:]:
            ema.append((price - ema[-1]) * multiplier + ema[-1])

        return np.array(ema)

    def _bollinger_bands(
        self, prices: np.ndarray, period: int = 20, std_dev: float = 2
    ) -> dict:
        """布林带"""
        if len(prices) < period:
            return {"upper": None, "middle": None, "lower": None, "signal": "neutral"}

        sma = np.mean(prices[-period:])
        std = np.std(prices[-period:])

        upper = sma + (std_dev * std)
        lower = sma - (std_dev * std)

        current_price = prices[-1]

        if current_price > upper:
            signal = "overbought"
        elif current_price < lower:
            signal = "oversold"
        else:
            signal = "neutral"

        return {
            "upper": round(upper, 2),
            "middle": round(sma, 2),
            "lower": round(lower, 2),
            "signal": signal,
            "bandwidth": round((upper - lower) / sma, 4),
        }

    def _atr(self, prices: np.ndarray, period: int = 14) -> dict:
        """平均真实波幅"""
        if len(prices) < period + 1:
            return {"value": None, "signal": "neutral"}

        high = prices[1:]
        low = prices[:-1]
        close = prices[:-1]

        tr = np.maximum(
            high - low,
            np.maximum(np.abs(high - close), np.abs(low - close))
        )

        atr = np.mean(tr[-period:])

        return {"value": round(atr, 4), "signal": "neutral"}

    def _stochastic(self, prices: np.ndarray, period: int = 14) -> dict:
        """随机指标"""
        if len(prices) < period:
            return {"k": None, "d": None, "signal": "neutral"}

        lows = np.min(prices[-period:])
        highs = np.max(prices[-period:])
        current = prices[-1]

        if highs == lows:
            k = 50
        else:
            k = 100 * (current - lows) / (highs - lows)

        return {"k": round(k, 2), "d": round(k * 0.7 + 50 * 0.3, 2), "signal": "neutral"}

    def _adx(self, prices: np.ndarray, period: int = 14) -> dict:
        """平均趋向指数"""
        if len(prices) < period + 2:
            return {"adx": None, "signal": "neutral"}

        high = prices[1:]
        low = prices[:-1]
        close = prices[:-1]

        plus_dm = np.where((high - np.roll(high, 1)) > (np.roll(low, 1) - low),
                            np.maximum(high - np.roll(high, 1), 0), 0)
        minus_dm = np.where((np.roll(low, 1) - low) > (high - np.roll(high, 1)),
                            np.maximum(np.roll(low, 1) - low, 0), 0)

        plus_dm[0] = 0
        minus_dm[0] = 0

        atr = self._atr(prices, period)["value"]

        if atr is None or atr == 0:
            return {"adx": None, "signal": "neutral"}

        plus_di = 100 * np.mean(plus_dm[-period:]) / atr
        minus_di = 100 * np.mean(minus_dm[-period:]) / atr

        dx = 100 * np.abs(plus_di - minus_di) / (plus_di + minus_di)
        adx = np.mean(dx[-period:])

        if adx > 25:
            signal = "strong_trend"
        elif adx > 15:
            signal = "weak_trend"
        else:
            signal = "no_trend"

        return {"adx": round(adx, 2), "signal": signal}

    def signals(self, ticker: str, indicators: dict) -> dict:
        """
        生成综合交易信号

        Args:
            ticker: 股票代码
            indicators: calculate()返回的指标结果

        Returns:
            dict: 综合交易信号
        """
        signal_counts = {"bullish": 0, "bearish": 0, "neutral": 0}
        details = {}

        for indicator_name, indicator_data in indicators.items():
            if indicator_data is None or indicator_data == {}:
                continue

            if isinstance(indicator_data, dict):
                if "signal" in indicator_data:
                    signal = indicator_data["signal"]
                    signal_counts[signal] = signal_counts.get(signal, 0) + 1
                    details[indicator_name] = signal
                elif "value" in indicator_data:
                    # 处理单一value的情况
                    details[indicator_name] = {"value": indicator_data["value"]}
            elif isinstance(indicator_data, list):
                details[indicator_name] = {"values": indicator_data}

        # 综合判断
        total = sum(signal_counts.values())
        bullish_ratio = signal_counts["bullish"] / total if total > 0 else 0
        bearish_ratio = signal_counts["bearish"] / total if total > 0 else 0

        if bullish_ratio > 0.6:
            combined = "bullish"
        elif bearish_ratio > 0.6:
            combined = "bearish"
        else:
            combined = "neutral"

        return {
            "ticker": ticker,
            "combined": combined,
            "bullish_count": signal_counts["bullish"],
            "bearish_count": signal_counts["bearish"],
            "neutral_count": signal_counts["neutral"],
            "details": details,
        }


if __name__ == "__main__":
    # 测试技术分析
    analyzer = TechnicalAnalyzer()

    # 模拟价格数据
    np.random.seed(42)
    prices = 100 + np.cumsum(np.random.randn(50) * 2)

    # 计算指标
    indicators = analyzer.calculate(prices.tolist(), ["sma", "ema", "rsi", "macd", "bbands", "atr"])

    print("Technical Analysis Results:")
    for name, data in indicators.items():
        if isinstance(data, dict) and "value" in data:
            print(f"  {name}: {data['value']} ({data.get('signal', 'neutral')})")

    # 生成信号
    signals = analyzer.signals("TEST", indicators)
    print(f"\nCombined Signal: {signals['combined']}")
    print(f"Bullish: {signals['bullish_count']}, Bearish: {signals['bearish_count']}, Neutral: {signals['neutral_count']}")