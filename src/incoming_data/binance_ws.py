# src/incoming_data/binance_ws.py
import asyncio
import json
import websockets
from src.managers.connection_manager import ConnectionManager
from src.global_queue.global_queue import synced_queue_manager

processed_binance_data = None

async def binance_ws_listener(manager: ConnectionManager):
    """Binance WebSocket verisini dinler ve kuyruklara iletir."""
    url = "wss://stream.binance.com:9443/ws/btcusdt@bookTicker"
    global processed_binance_data

    while True:
        try:
            async with websockets.connect(url) as ws:
                print("✅ Binance WebSocket'e bağlandı...")

                async for msg in ws:
                    data = json.loads(msg)
                    processed_binance_data = {
                        "exchange": "Binance",
                        "symbol": data["s"],
                        "best_bid_price": float(data["b"]),
                        "best_bid_qty": float(data["B"]),
                        "best_ask_price": float(data["a"]),
                        "best_ask_qty": float(data["A"]),
                    }

                    # 🔄 Tek bir put çağrısıyla hem back hem front güncellenir
                    await synced_queue_manager.put("binance", processed_binance_data)

        except Exception as e:
            print(f"⚠️ Binance WebSocket bağlantı hatası: {e}")
            await asyncio.sleep(5)
