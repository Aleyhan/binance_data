# src/routes/routes.py
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Request

router = APIRouter()

@router.websocket("/ws/ticker")
async def websocket_endpoint(websocket: WebSocket):
    manager = websocket.app.state.connection_manager
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()  # Eğer istemciden gelen mesaj beklenmiyorsa kaldırılabilir
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        print("🛑 Bir istemci bağlantıyı kapattı.")

@router.get("/queue/{queue_name}")
async def get_queue_data(queue_name: str, request: Request):
    queue_manager = request.app.state.queue_manager
    try:
        data = await queue_manager.get(queue_name)
        return data
    except ValueError as e:
        return {"error": str(e)}
