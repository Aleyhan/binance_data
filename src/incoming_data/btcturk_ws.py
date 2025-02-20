# src/incoming_data/btcturk_ws.py
import asyncio
import json
import websockets
from src.managers.connection_manager import ConnectionManager
from src.global_queue.global_queue import synced_queue_manager


processed_btcturk_data = None

async def btcturk_ws_listener(manager: ConnectionManager):
    """BTCTurk WebSocket verisini dinler ve kuyruklara iletir."""
    url = "wss://ws-feed-pro.btcturk.com/"
    subscription_message = [151, {"type": 151, "channel": "ticker", "event": "BTCUSDT", "join": True}]
    global processed_btcturk_data

    while True:
        try:
            async with websockets.connect(url) as ws:
                print("✅ BTCTurk WebSocket'e bağlandı...")
                await ws.send(json.dumps(subscription_message))

                async for msg in ws:
                    data = json.loads(msg)
                    if isinstance(data, list) and len(data) > 1 and isinstance(data[1], dict):
                        ticker = data[1]
                        try:
                            processed_btcturk_data = {
                                "exchange": "BTCTurk",
                                "symbol": ticker["PS"],
                                "best_bid_price": float(ticker["B"]),
                                "best_bid_qty": float(ticker["BA"]),
                                "best_ask_price": float(ticker["A"]),
                                "best_ask_qty": float(ticker["AA"]),
                            }

                            # 🔄 Tek bir put çağrısıyla hem back hem front güncellenir
                            await synced_queue_manager.put("btcturk", processed_btcturk_data)

                            # await manager.broadcast(processed_btcturk_data)

                        except KeyError as e:
                            print(f"⚠️ Veri formatı hatası: {e}")

        except Exception as e:
            print(f"⚠️ BTCTurk WebSocket bağlantı hatası: {e}")
            await asyncio.sleep(5)
