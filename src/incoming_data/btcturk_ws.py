# src/incoming_data/btcturk_ws.py
import asyncio
import json
import websockets
from src.managers.connection_manager import ConnectionManager
from src.global_queue.global_queue import synced_queue_manager
from src.config import EXCHANGE_SYMBOLS

processed_btcturk_data = None


async def btcturk_ws_listener(manager: ConnectionManager):
    """BTCTurk WebSocket verisini, konfigürasyonda tanımlı tüm semboller için dinler ve ilgili kuyruklara iletir."""
    url = "wss://ws-feed-pro.btcturk.com/"
    symbols = EXCHANGE_SYMBOLS.get("BTCTurk", [])

    global processed_btcturk_data

    while True:
        try:
            async with websockets.connect(url) as ws:
                print("✅ BTCTurk WebSocket'e bağlandı...")
                # Her sembol için abonelik mesajı gönderilir.
                for symbol in symbols:
                    subscription_message = [
                        151,
                        {"type": 151, "channel": "ticker", "event": symbol.upper(), "join": True}
                    ]
                    await ws.send(json.dumps(subscription_message))

                async for msg in ws:
                    data = json.loads(msg)
                    if isinstance(data, list) and len(data) > 1 and isinstance(data[1], dict):
                        ticker = data[1]
                        # "PS" alanını kontrol ediyoruz:
                        raw_symbol = ticker.get("PS", "")
                        if not raw_symbol:
                            print("⚠️ BTCTurk veri formatı beklenildiği gibi değil, 'PS' alanı eksik. Mesaj:", ticker)
                            continue  # Eğer sembol bilgisi boşsa, bu mesajı atla

                        symbol = raw_symbol.lower()
                        processed_btcturk_data = {
                            "exchange": "BTCTurk",
                            "symbol": raw_symbol,
                            "best_bid_price": float(ticker.get("B", 0)),
                            "best_bid_qty": float(ticker.get("BA", 0)),
                            "best_ask_price": float(ticker.get("A", 0)),
                            "best_ask_qty": float(ticker.get("AA", 0)),
                        }
                        # Kuyruk ismi: "btcturk_<sembol>" şeklinde oluşturuluyor.
                        queue_key = f"BTCTurk_{symbol}"
                        await synced_queue_manager.put(queue_key, processed_btcturk_data)
        except Exception as e:
            print(f"⚠️ BTCTurk WebSocket bağlantı hatası: {e}")
            await asyncio.sleep(5)
