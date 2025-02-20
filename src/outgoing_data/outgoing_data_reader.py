import asyncio
from typing import Dict, Any
from src.managers.connection_manager import ConnectionManager
from src.global_queue.global_queue import global_queue_manager_front, global_queue_manager_back


async def outgoing_data_reader(
    connection_manager: ConnectionManager,
    poll_interval: float = 0.5
):
    """
    Kuyruklardan sürekli veri çeker, gelen verileri 'last_values' sözlüğünde tutar.
    'merged_data' eski durumdan farklıysa WebSocket üzerinden broadcast eder.
    poll_interval: Kuyrukları bu sıklıkta (saniye cinsinden) kontrol eder.
    """
    last_values: Dict[str, Any] = {
        "binance": None,
        "btcturk": None
    }

    # Bir önceki yayınlanan birleşik veriyi tutar
    prev_merged_data: Dict[str, Any] = None

    while True:
        for q_name in ["binance", "btcturk"]:
            try:
                data = await global_queue_manager_front.get(q_name)  # Kuyruktan veri çek
                if data is not None:
                    # Yeni veri geldiyse last_values'ı güncelle
                    last_values[q_name] = data
            except asyncio.QueueEmpty:
                # Veri yoksa eski değeri koru
                pass

        # Mevcut en güncel verileri birleştir
        merged_data = {
            "binance": last_values["binance"],
            "btcturk": last_values["btcturk"]
        }

        # merged_data, daha önce gönderdiğimiz durumdan farklı mı?
        if merged_data != prev_merged_data:
            # Farklıysa WebSocket bağlantılarına yayınla
            await connection_manager.broadcast(merged_data)
            prev_merged_data = merged_data  # Yayınladığımız veriyi güncelle

        # Çok sık döngüye girmemek için bir miktar bekleyelim
        await asyncio.sleep(poll_interval)

