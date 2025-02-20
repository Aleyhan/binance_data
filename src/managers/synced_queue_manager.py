# src/managers/synced_queue_manager.py
from src.managers.queue_manager import QueueManager

class SyncedQueueManager:
    """Back ve front kuyruklarını eşzamanlı yöneten sınıf."""

    def __init__(self, back_queue: QueueManager, front_queue: QueueManager):
        self.back_queue = back_queue
        self.front_queue = front_queue

    def create_queue(self, name: str, maxsize: int = 100):
        """Her iki kuyruğu da aynı anda oluşturur."""
        self.back_queue.create_queue(name, maxsize)
        self.front_queue.create_queue(name, maxsize)

    async def put(self, name: str, data: dict):
        """
        Veriyi önce back kuyruğuna yazar, sonra front kuyruğuna kopyalar.
        Böylece front her zaman back'in kopyası olur.
        """
        await self.back_queue.put(name, data)   # 🗄️ Back kuyruğa yaz
        await self.front_queue.put(name, data)  # 📝 Front kuyruğa kopyala
