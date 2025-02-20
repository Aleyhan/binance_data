from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Request

router = APIRouter()

@router.websocket("/ws/ticker")
async def websocket_endpoint(websocket: WebSocket):
    manager = websocket.app.state.connection_manager
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()  # İstemciden mesaj beklenmiyorsa kaldırabilirsin
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        print("🛑 Bir istemci bağlantıyı kapattı.")


@router.get("/queue/{exchange_name}")
async def get_queue_data(exchange_name: str, request: Request):
    queue_manager = request.app.state.queue_manager
    try:
        data = await queue_manager.get(exchange_name)
        return data
    except ValueError as e:
        return {"error": str(e)}
