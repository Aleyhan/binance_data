# main.py
import asyncio
import uvicorn
from fastapi import FastAPI
from contextlib import asynccontextmanager
from starlette.datastructures import State

from src.managers.connection_manager import ConnectionManager
from src.incoming_data.binance_ws import binance_ws_listener
from src.incoming_data.btcturk_ws import btcturk_ws_listener
from src.outgoing_data.outgoing_data_reader import outgoing_data_reader
from src.routes.routes import router
from src.global_queue.global_queue import global_queue_manager_front, synced_queue_manager, initialize_queues

@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state: State  # IDE'nin app.state'i tanımasını sağlar

    connection_manager = ConnectionManager()

    # ✅ Kuyrukları oluştur
    initialize_queues()

    # Uygulama genelindeki kuyruklar app.state'e atanıyor
    app.state.queue_manager = global_queue_manager_front
    app.state.connection_manager = connection_manager


    # 🟢 WebSocket dinleyicileri
    task_binance = asyncio.create_task(binance_ws_listener(connection_manager))
    task_btcturk = asyncio.create_task(btcturk_ws_listener(connection_manager))

    print("🚀 WebSocket dinleyicileri başlatıldı.")

    # 📤 Outgoing data okuyucusu
    task_outgoing = asyncio.create_task(outgoing_data_reader(connection_manager))

    yield  # Uygulama çalışırken

    # 🛑 Görevleri sonlandır
    task_binance.cancel()
    task_btcturk.cancel()
    task_outgoing.cancel()
    print("🛑 Uygulama kapatılıyor...")

app = FastAPI(lifespan=lifespan)
app.include_router(router)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
