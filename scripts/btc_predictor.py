#!/usr/bin/env python3
"""
BTC Price Prediction Bot
Prediksi harga BTC 5 menit ke depan menggunakan simple moving average + trend
"""

import requests
import time
from datetime import datetime

# Konfigurasi
COINGECKO_API = "https://api.coingecko.com/api/v3"
SYMBOL = "bitcoin"
CURRENCY = "usd"
PREDICTION_MINUTES = 5
HISTORY_COUNT = 10  # Ambil 10 data terakhir

def get_btc_price_history():
    """Ambil histori harga BTC"""
    url = f"{COINGECKO_API}/coins/{SYMBOL}/market_chart"
    params = {
        "vs_currency": CURRENCY,
        "days": 1,  # 1 hari terakhir
        "interval": "minute"  # Per menit
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        data = response.json()

        if "prices" not in data:
            print(f"❌ Error: {data.get('error', 'Unknown error')}")
            return None

        prices = data["prices"]
        # Ambil data terakhir sesuai HISTORY_COUNT
        return prices[-HISTORY_COUNT:]

    except Exception as e:
        print(f"❌ Error fetching data: {e}")
        return None

def calculate_prediction(history):
    """Hitung prediksi menggunakan SMA + Linear Trend"""
    if len(history) < 3:
        return None

    # Ekstrak harga saja
    prices = [p[1] for p in history]

    # Method 1: Simple Moving Average (SMA)
    sma = sum(prices) / len(prices)

    # Method 2: Linear Trend Extrapolation
    n = len(prices)
    x = list(range(n))
    y = prices

    # Calculate slope (m) dan intercept (b) untuk y = mx + b
    x_mean = sum(x) / n
    y_mean = sum(y) / n

    numerator = sum((x[i] - x_mean) * (y[i] - y_mean) for i in range(n))
    denominator = sum((x[i] - x_mean) ** 2 for i in range(n))

    if denominator == 0:
        slope = 0
    else:
        slope = numerator / denominator

    intercept = y_mean - slope * x_mean

    # Prediksi 5 menit ke depan (x = n + 5)
    predicted_x = n + PREDICTION_MINUTES
    linear_prediction = slope * predicted_x + intercept

    # Method 3: Weighted Average (lebih berat ke data terbaru)
    weights = [i+1 for i in range(n)]  # [1, 2, 3, ..., n]
    weighted_avg = sum(prices[i] * weights[i] for i in range(n)) / sum(weights)

    # Gabungkan prediksi (average dari 3 method)
    final_prediction = (sma + linear_prediction + weighted_avg) / 3

    return {
        "current_price": prices[-1],
        "sma": sma,
        "linear": linear_prediction,
        "weighted": weighted_avg,
        "final": final_prediction,
        "trend": "📈 UP" if slope > 0 else "📉 DOWN",
        "slope": slope
    }

def main():
    print("=" * 50)
    print("🤖 BTC Price Prediction Bot")
    print("=" * 50)
    print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("-" * 50)

    # Ambil data
    print("📡 Mengambil data harga BTC...")
    history = get_btc_price_history()

    if history is None:
        print("❌ Gagal mengambil data")
        return

    # Hitung prediksi
    result = calculate_prediction(history)

    if result is None:
        print("❌ Data tidak cukup untuk prediksi")
        return

    # Tampilkan hasil
    current = result["current_price"]
    predicted = result["final"]
    change = predicted - current
    change_pct = (change / current) * 100

    print(f"\n💰 Harga Saat Ini: ${current:,.2f}")
    print(f"🎯 Prediksi ({PREDICTION_MINUTES} menit): ${predicted:,.2f}")
    print(f"📊 Perubahan: {change:+,.2f} ({change_pct:+.2f}%)")
    print(f"\n📈 Trend: {result['trend']}")
    print(f"   - SMA: ${result['sma']:,.2f}")
    print(f"   - Linear: ${result['linear']:,.2f}")
    print(f"   - Weighted: ${result['weighted']:,.2f}")
    print(f"   - Slope: {result['slope']:.4f}")

    # Disclaimer
    print("\n" + "=" * 50)
    print("⚠️ Disclaimer: Prediksi ini hanya untuk belajar!")
    print("   Jangan gunakan untuk keputusan investasi nyata.")
    print("=" * 50)

if __name__ == "__main__":
    main()
