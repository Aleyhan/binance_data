# src/incoming_data/binance_futures_ws.py
import asyncio
import json
import websockets
from src.managers.connection_manager import ConnectionManager
from src.global_queue.global_queue import synced_queue_manager
from src.config import EXCHANGE_SYMBOLS

processed_binance_futures_data = None

async def binance_futures_ws_listener(manager: ConnectionManager):
    """Binance USDT-M Vadeli İşlemler WebSocket verisini, konfigürasyonda tanımlı tüm semboller için dinler ve ilgili kuyruklara iletir."""
    symbols = EXCHANGE_SYMBOLS.get("BinanceFutures", [])
    # Binance USDT-M Vadeli İşlemler combined stream URL; semboller lowercase olarak kullanılmalıdır.
    streams = "/".join([f"{symbol.lower()}@bookTicker" for symbol in symbols])
    url = f"wss://fstream.binance.com/stream?streams={streams}"

    global processed_binance_futures_data

    while True:
        try:
            async with websockets.connect(url) as ws:
                print("✅ Binance USDT-M Vadeli İşlemler WebSocket'e bağlandı...")
                async for msg in ws:
                    msg_json = json.loads(msg)
                    # Combined stream formatı: {"stream": "btcusdt@bookTicker", "data": { ... }}
                    data = msg_json.get("data", {})
                    if not data:
                        continue

                    symbol = data.get("s", "").lower()  # sembol örn: BTCUSDT -> btcusdt
                    processed_binance_futures_data = {
                        "exchange": "BinanceFutures",
                        "symbol": data.get("s"),
                        "best_bid_price": float(data.get("b", 0)),
                        "best_bid_qty": float(data.get("B", 0)),
                        "best_ask_price": float(data.get("a", 0)),
                        "best_ask_qty": float(data.get("A", 0)),
                    }
                    # Kuyruk ismi: "binance_futures_<sembol>"
                    queue_key = f"BinanceFutures_{symbol.upper()}"
                    await synced_queue_manager.put(queue_key, processed_binance_futures_data)
        except Exception as e:
            print(f"⚠️ Binance USDT-M Vadeli İşlemler WebSocket bağlantı hatası: {e}")
            await asyncio.sleep(5)