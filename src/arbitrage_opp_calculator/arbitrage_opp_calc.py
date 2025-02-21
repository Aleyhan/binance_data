import aiofiles
import datetime
import json


async def log_arbitrage_opportunity(arbitrage_data: dict, log_file: str = "arbitrage_log.txt", json_log_file: str = "arbitrage_log.json"):
    """
    Arbitraj fırsatını hem okunabilir metin formatında hem de JSON formatında loglar.

    Args:
        arbitrage_data (dict): Arbitraj hesaplaması sonuçları.
        log_file (str): İnsan okunabilir log dosyası (varsayılan: "arbitrage_log.txt").
        json_log_file (str): JSON formatındaki log dosyası (varsayılan: "arbitrage_log.json").
    """
    try:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # ✅ Metin formatında log
        log_entry = (
            f"\n========== ARBITRAJ FIRSATI =========="
            f"\nTarih       : {timestamp}"
            f"\nSembol      : {arbitrage_data['symbol']}"
            f"\nAlış Borsası: {arbitrage_data['buy_exchange']} (Fiyat: {arbitrage_data['buy_price']})"
            f"\nSatış Borsası: {arbitrage_data['sell_exchange']} (Fiyat: {arbitrage_data['sell_price']})"
            f"\nFiyat Farkı : {arbitrage_data['price_difference']} USDT"
            f"\nYüzdelik Fark: {arbitrage_data['percentage_difference']}%"
            f"\nEşik Aşıldı : {'✅ Evet' if arbitrage_data['above_threshold'] else '❌ Hayır'}"
            f"\n======================================\n"
        )

        async with aiofiles.open(log_file, mode="a") as file:
            await file.write(log_entry)

        # ✅ JSON formatında log (doğru JSON formatı sağlanır)
        json_log_entry = {
            "timestamp": timestamp,
            "symbol": arbitrage_data['symbol'],
            "buy_exchange": arbitrage_data['buy_exchange'],
            "buy_price": arbitrage_data['buy_price'],
            "sell_exchange": arbitrage_data['sell_exchange'],
            "sell_price": arbitrage_data['sell_price'],
            "price_difference": arbitrage_data['price_difference'],
            "percentage_difference": arbitrage_data['percentage_difference'],
            "above_threshold": arbitrage_data['above_threshold']
        }

        # Eğer dosya boşsa bir liste oluştur, değilse mevcut JSON dizisine ekle
        try:
            async with aiofiles.open(json_log_file, mode="r") as json_file:
                content = await json_file.read()
                logs = json.loads(content) if content else []
        except (FileNotFoundError, json.JSONDecodeError):
            logs = []

        logs.append(json_log_entry)

        async with aiofiles.open(json_log_file, mode="w") as json_file:
            await json_file.write(json.dumps(logs, indent=4))

    except Exception as e:
        print(f"🚨 Log yazma hatası: {e}")



async def calculate_arbitrage_opportunity(data1: dict, data2: dict, threshold: float = 0.3) -> dict:
    """
    İki borsadaki fiyatlar arasındaki farkı ve yüzdelik farkı hesaplar.

    Args:
        data1 (dict): İlk borsanın fiyat verisi (alış yapılacak borsa).
        data2 (dict): İkinci borsanın fiyat verisi (satış yapılacak borsa).
        threshold (float): Yüzdelik fark eşiği (varsayılan %0.3).

    Returns:
        dict: Arbitraj hesaplamalarının sonuçları ve tablo başlığı.
    """
    symbol = data1.get("symbol", "Unknown")

    buy_price = data1.get("best_bid_price", 0)
    sell_price = data2.get("best_ask_price", 0)

    price_difference = sell_price - buy_price
    percentage_difference = ((price_difference / buy_price) * 100) if buy_price else 0
    above_threshold = percentage_difference >= threshold

    table_head = f"Buy-{data1.get('exchange')}/Sell-{data2.get('exchange')}"

    result = {
        "symbol": symbol,
        "buy_exchange": data1.get("exchange"),
        "sell_exchange": data2.get("exchange"),
        "buy_price": buy_price,
        "sell_price": sell_price,
        "price_difference": round(price_difference, 2),
        "percentage_difference": round(percentage_difference, 3),
        "above_threshold": above_threshold,
        "table_head": table_head
    }

    # Eğer eşik aşıldıysa asenkron log kaydı yap
    if above_threshold:
        await log_arbitrage_opportunity(result)

    return result



async def process_merged_data_for_arbitrage_BTCTurk2BinanceFutures(merged_data: dict, threshold: float = 0.00001) -> dict:
    """
    merged_data içindeki verileri kullanarak BTCTurk'ten alış ve BinanceFutures'tan satış için
    arbitraj fırsatını hesaplar ve merged_data'ya ekler.
    """
    for symbol in set(key.split('_')[1] for key in merged_data.keys()):
        btcturk_key = f"BTCTurk_{symbol}"
        binance_futures_key = f"BinanceFutures_{symbol}"

        btcturk_data = merged_data.get(btcturk_key)
        binance_futures_data = merged_data.get(binance_futures_key)

        if btcturk_data and binance_futures_data:
            arbitrage_result = await calculate_arbitrage_opportunity(btcturk_data, binance_futures_data, threshold)
            merged_data[f"arbitrage_{symbol}"] = arbitrage_result

    return merged_data



# Örnek kullanım
# if __name__ == "__main__":
#     merged_data_example = {
#         "BTCTurk_btcusdt": {
#             "exchange": "BTCTurk",
#             "symbol": "BTCUSDT",
#             "best_bid_price": 98500.00,
#             "best_bid_qty": 1.5,
#             "best_ask_price": 98600.00,
#             "best_ask_qty": 0.8
#         },
#         "BinanceFutures_btcusdt": {
#             "exchange": "BinanceFutures",
#             "symbol": "BTCUSDT",
#             "best_bid_price": 98600.00,
#             "best_bid_qty": 2.0,
#             "best_ask_price": 98610.00,
#             "best_ask_qty": 1.0
#         }
#     }
#
#     updated_merged_data = process_merged_data_for_arbitrage_BTCTurk2BinanceFutures(merged_data_example)
#     from pprint import pprint
#     pprint(updated_merged_data)

