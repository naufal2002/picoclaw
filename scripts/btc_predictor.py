#!/usr/bin/env python3
"""
BTC Price Prediction Bot
Prediksi harga BTC 5 menit ke depan menggunakan data real-time dari Binance
"""

import requests
from datetime import datetime, timezone

PREDICTION_MINUTES = 5
HISTORY_COUNT = 20  # 20 candle terakhir (1 menit each)


def get_btc_realtime():
    """Ambil harga BTC real-time dari Binance"""
    try:
        resp = requests.get(
            "https://api.binance.com/api/v3/ticker/price",
            params={"symbol": "BTCUSDT"},
            timeout=5,
        )
        return float(resp.json()["price"])
    except Exception as e:
        print(f"❌ Error harga real-time: {e}")
        return None


def get_btc_klines():
    """Ambil 1-menit candlestick data dari Binance (real-time)"""
    try:
        resp = requests.get(
            "https://api.binance.com/api/v3/klines",
            params={
                "symbol": "BTCUSDT",
                "interval": "1m",
                "limit": HISTORY_COUNT,
            },
            timeout=5,
        )
        data = resp.json()
        # Format: [open_time, open, high, low, close, volume, ...]
        return [
            {
                "time": datetime.fromtimestamp(k[0] / 1000, tz=timezone.utc),
                "open": float(k[1]),
                "high": float(k[2]),
                "low": float(k[3]),
                "close": float(k[4]),
                "volume": float(k[5]),
            }
            for k in data
        ]
    except Exception as e:
        print(f"❌ Error klines: {e}")
        return None


def calculate_prediction(klines, current_price):
    """Prediksi pakai SMA + Linear Trend + Weighted + Volume-Weighted"""
    closes = [k["close"] for k in klines]
    volumes = [k["volume"] for k in klines]
    n = len(closes)

    # 1) SMA
    sma = sum(closes) / n

    # 2) Linear Trend
    x_mean = (n - 1) / 2
    y_mean = sum(closes) / n
    num = sum((i - x_mean) * (closes[i] - y_mean) for i in range(n))
    den = sum((i - x_mean) ** 2 for i in range(n))
    slope = num / den if den else 0
    intercept = y_mean - slope * x_mean
    linear = slope * (n + PREDICTION_MINUTES) + intercept

    # 3) Weighted MA (data terbaru lebih berat)
    weights = list(range(1, n + 1))
    wma = sum(closes[i] * weights[i] for i in range(n)) / sum(weights)

    # 4) Volume-Weighted MA
    total_vol = sum(volumes)
    if total_vol > 0:
        vwma = sum(closes[i] * volumes[i] for i in range(n)) / total_vol
    else:
        vwma = sma

    # Final: rata-rata 4 metode
    prediction = (sma + linear + wma + vwma) / 4

    # RSI sederhana (14 period atau n jika kurang)
    gains, losses = [], []
    for i in range(1, n):
        diff = closes[i] - closes[i - 1]
        gains.append(max(diff, 0))
        losses.append(max(-diff, 0))
    avg_gain = sum(gains) / len(gains) if gains else 0
    avg_loss = sum(losses) / len(losses) if losses else 0
    rsi = 100 - (100 / (1 + avg_gain / avg_loss)) if avg_loss > 0 else 100

    # Volatility
    mean_price = sum(closes) / n
    variance = sum((p - mean_price) ** 2 for p in closes) / n
    volatility = variance ** 0.5

    return {
        "current": current_price,
        "prediction": prediction,
        "sma": sma,
        "linear": linear,
        "wma": wma,
        "vwma": vwma,
        "slope": slope,
        "rsi": rsi,
        "volatility": volatility,
        "trend": "📈 UP" if slope > 0 else "📉 DOWN",
        "high": max(closes),
        "low": min(closes),
    }


def main():
    print("=" * 50)
    print("🤖 BTC Real-Time Prediction")
    print("=" * 50)
    print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"📊 Data: Binance BTCUSDT (1m x {HISTORY_COUNT})")
    print("-" * 50)

    current = get_btc_realtime()
    if current is None:
        return

    klines = get_btc_klines()
    if klines is None or len(klines) < 3:
        print("❌ Data tidak cukup")
        return

    r = calculate_prediction(klines, current)

    change = r["prediction"] - r["current"]
    pct = (change / r["current"]) * 100

    print(f"\n💰 Harga Real-Time : ${r['current']:,.2f}")
    print(f"🎯 Prediksi {PREDICTION_MINUTES}m    : ${r['prediction']:,.2f}")
    print(f"📊 Perubahan       : {change:+,.2f} ({pct:+.3f}%)")
    print(f"\n{r['trend']} Trend (slope: {r['slope']:.2f}/menit)")
    print(f"📉 Low  (20m): ${r['low']:,.2f}")
    print(f"📈 High (20m): ${r['high']:,.2f}")
    print(f"📏 Volatility : ${r['volatility']:,.2f}")
    print(f"📊 RSI        : {r['rsi']:.1f}", end="")
    if r["rsi"] > 70:
        print(" (Overbought ⚠️)")
    elif r["rsi"] < 30:
        print(" (Oversold ⚠️)")
    else:
        print(" (Normal)")
    print(f"\n🔍 Detail Metode:")
    print(f"   SMA  : ${r['sma']:,.2f}")
    print(f"   Linear: ${r['linear']:,.2f}")
    print(f"   WMA  : ${r['wma']:,.2f}")
    print(f"   VWMA : ${r['vwma']:,.2f}")

    print("\n" + "=" * 50)
    print("⚠️ Disclaimer: Prediksi untuk belajar saja!")
    print("=" * 50)


if __name__ == "__main__":
    main()
