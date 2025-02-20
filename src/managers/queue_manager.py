import asyncio
from collections import deque

class LimitedQueue(asyncio.Queue):
    """Sınırlı kapasiteye sahip bir kuyruk."""

    def __init__(self, maxsize: int = 100):
        super().__init__(maxsize=maxsize)
        self._deque = deque(maxlen=maxsize)

    async def put(self, item):
        """Kuyruğa veri ekler, kapasite dolduysa en eski veriyi siler."""
        self._deque.append(item)

    async def get(self):
        """Kuyruktan veri çeker."""
        if self._deque:
            return self._deque.popleft()
        raise asyncio.QueueEmpty("Kuyruk boş.")

    def size(self):
        """Kuyruktaki mevcut veri sayısını döndürür."""
        return len(self._deque)

    def all_items(self):
        """Tüm kuyruk elemanlarını liste olarak döndürür."""
        return list(self._deque)


class QueueManager:
    """Tüm veri kuyruklarını yöneten sınıf."""

    def __init__(self):
        self.queues = {}

    def create_queue(self, name: str, maxsize: int = 100):
        """Belirtilen isimde bir kuyruk oluşturur (zaten varsa oluşturmaz)."""
        if name not in self.queues:
            self.queues[name] = LimitedQueue(maxsize=maxsize)
        return self.queues[name]

    def get_queue(self, name: str):
        """Var olan bir kuyruğu döndürür."""
        return self.queues.get(name, None)

    async def put(self, name: str, data):
        """Belirtilen kuyruğa veri ekler."""
        queue = self.get_queue(name)
        if queue:
            await queue.put(data)
        else:
            raise ValueError(f"⚠️ '{name}' isimli bir kuyruk bulunamadı.")

    async def get(self, name: str):
        """Belirtilen kuyruktan veri çeker."""
        queue = self.get_queue(name)
        if queue:
            return await queue.get()
        else:
            raise ValueError(f"⚠️ '{name}' isimli bir kuyruk bulunamadı.")

    def size(self, name: str):
        """Belirtilen kuyruğun boyutunu döndürür."""
        queue = self.get_queue(name)
        return queue.size() if queue else 0

    def all_items(self, name: str):
        """Belirtilen kuyruğun tüm elemanlarını döndürür."""
        queue = self.get_queue(name)
        return queue.all_items() if queue else []


