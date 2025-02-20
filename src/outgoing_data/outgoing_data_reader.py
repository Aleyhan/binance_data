# src/outgoing_data/outgoing_data_reader.py
import asyncio
from typing import Dict, Any
from src.managers.connection_manager import ConnectionManager
from src.global_queue.global_queue import global_queue_manager_front
from src.config import EXCHANGE_SYMBOLS

async def outgoing_data_reader(
    connection_manager: ConnectionManager,
    poll_interval: float = 0.5
):
    """
    Tüm exchange–sembol kuyruklarından sürekli veri çekip,
    eğer veride bir değişiklik varsa WebSocket istemcilerine güncellenmiş veriyi broadcast eder.
    """
    # Her exchange–sembol çifti için en son veriyi saklayan sözlük
    last_values: Dict[str, Any] = {}
    for exchange, symbols in EXCHANGE_SYMBOLS.items():
        for symbol in symbols:
            key = f"{exchange}_{symbol}"
            last_values[key] = None

    prev_merged_data = None

    while True:
        merged_data = {}
        for key in last_values.keys():
            try:
                data = await global_queue_manager_front.get(key)
                if data is not None:
                    last_values[key] = data
            except asyncio.QueueEmpty:
                pass
            merged_data[key] = last_values[key]

        if merged_data != prev_merged_data:
            await connection_manager.broadcast(merged_data)
            prev_merged_data = merged_data.copy()
        await asyncio.sleep(poll_interval)
