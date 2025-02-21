# src/config.py

# Burada borsaların ve ilgili sembollerin listesini düzenleyebilirsiniz.
# Binance için semboller küçük harf (lowercase) olarak kullanılmalı (combined stream URL buna göre oluşturuluyor).
EXCHANGE_SYMBOLS = {
    "Binance": ["BTCUSDT", "ethusdt", "xrpusdt"],
    "BTCTurk": ["btcusdt", "ethusdt", "xrpusdt"],
    "BinanceFutures": ["btcusdt", "ethusdt", "xrpusdt"],
}