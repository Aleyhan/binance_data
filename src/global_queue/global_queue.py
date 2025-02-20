# src/global_queue/global_queue.py
from src.managers.queue_manager import QueueManager
from src.managers.synced_queue_manager import SyncedQueueManager

# 🗄️ Back ve 📄 Front için ayrı QueueManager örnekleri
global_queue_manager_back = QueueManager()
global_queue_manager_front = QueueManager()

# 🔄 Back ve front kuyruklarını senkronize eden manager
synced_queue_manager = SyncedQueueManager(global_queue_manager_back, global_queue_manager_front)

def initialize_queues():
    """Başlangıçta gerekli tüm kuyrukları oluşturur."""
    for queue_name in ["binance", "btcturk"]:
        synced_queue_manager.create_queue(queue_name, maxsize=200)
