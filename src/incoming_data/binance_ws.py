# src/incoming_data/binance_ws.py
import asyncio
import json
import websockets
from src.managers.connection_manager import ConnectionManager
from src.global_queue.global_queue import synced_queue_manager
from src.config import EXCHANGE_SYMBOLS

processed_binance_data = None


async def binance_ws_listener(manager: ConnectionManager):
    """Binance WebSocket verisini, konfigürasyonda tanımlı tüm semboller için dinler ve ilgili kuyruklara iletir."""
    symbols = EXCHANGE_SYMBOLS.get("Binance", [])
    # Binance combined stream URL; semboller lowercase olarak kullanılmalıdır.
    streams = "/".join([f"{symbol}@bookTicker" for symbol in symbols])
    url = f"wss://stream.binance.com:9443/stream?streams={streams}"

    global processed_binance_data

    while True:
        try:
            async with websockets.connect(url) as ws:
                print("✅ Binance WebSocket'e bağlandı...")
                async for msg in ws:
                    msg_json = json.loads(msg)
                    # Combined stream formatı: {"stream": "btcusdt@bookTicker", "data": { ... }}
                    data = msg_json.get("data", {})
                    if not data:
                        continue

                    symbol = data.get("s", "").lower()  # sembol örn: BTCUSDT -> btcusdt
                    processed_binance_data = {
                        "exchange": "Binance",
                        "symbol": data.get("s"),
                        "best_bid_price": float(data.get("b", 0)),
                        "best_bid_qty": float(data.get("B", 0)),
                        "best_ask_price": float(data.get("a", 0)),
                        "best_ask_qty": float(data.get("A", 0)),
                    }
                    # Kuyruk ismi: "binance_<sembol>"
                    queue_key = f"Binance_{symbol}"
                    await synced_queue_manager.put(queue_key, processed_binance_data)
        except Exception as e:
            print(f"⚠️ Binance WebSocket bağlantı hatası: {e}")
            await asyncio.sleep(5)
