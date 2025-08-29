import asyncio
import json
import logging
import os
from typing import Dict, List, Optional

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
import uvicorn

from . import engine, io


logger = logging.getLogger(__name__)


class GameManager:
    """Manages game instances and WebSocket connections."""
    
    def __init__(self):
        self.games: Dict[str, engine.Board] = {}
        self.connections: Dict[str, List[WebSocket]] = {}
        self.default_game_id = "default"
        
    def create_game(self, game_id: str = None, width: int = 8, height: int = 8, 
                   players: int = 4, bots: int = 0) -> str:
        """Create a new game instance."""
        if game_id is None:
            game_id = self.default_game_id
            
        board = engine.Board(width=width, height=height, players=players, bots=bots)
        board.listeners.append(GameUpdateListener(self, game_id))
        self.games[game_id] = board
        self.connections[game_id] = []
        
        return game_id
    
    def get_game(self, game_id: str = None) -> Optional[engine.Board]:
        """Get a game instance."""
        if game_id is None:
            game_id = self.default_game_id
            
        return self.games.get(game_id)
    
    def ensure_default_game(self) -> engine.Board:
        """Ensure the default game exists."""
        if self.default_game_id not in self.games:
            self.create_game()
        return self.games[self.default_game_id]
    
    async def add_connection(self, game_id: str, websocket: WebSocket):
        """Add a WebSocket connection for a game."""
        if game_id not in self.connections:
            self.connections[game_id] = []
        self.connections[game_id].append(websocket)
        
    async def remove_connection(self, game_id: str, websocket: WebSocket):
        """Remove a WebSocket connection for a game."""
        if game_id in self.connections:
            try:
                self.connections[game_id].remove(websocket)
            except ValueError:
                pass
    
    async def broadcast_to_game(self, game_id: str, message: dict):
        """Broadcast a message to all connections for a game."""
        if game_id not in self.connections:
            return
            
        # Remove disconnected connections
        active_connections = []
        for connection in self.connections[game_id]:
            try:
                await connection.send_json(message)
                active_connections.append(connection)
            except Exception:
                # Connection is dead, skip it
                pass
        
        self.connections[game_id] = active_connections


class GameUpdateListener:
    """Listener for game updates to broadcast via WebSocket."""
    
    def __init__(self, manager: GameManager, game_id: str):
        self.manager = manager
        self.game_id = game_id
        
    def refresh_square(self, square, in_game=True):
        """Called when a square is updated."""
        asyncio.create_task(self._broadcast_square_update(square))
        
    async def _broadcast_square_update(self, square):
        """Broadcast square update to connected clients."""
        board = self.manager.get_game(self.game_id)
        if not board:
            return
            
        message = {
            "type": "square_update",
            "square": {
                "x": square.x,
                "y": square.y,
                "value": square.value,
                "player": square.player.number if square.player else None,
                "color": square.color
            },
            "game_state": self._serialize_board(board)
        }
        
        await self.manager.broadcast_to_game(self.game_id, message)
        
    def _serialize_board(self, board: engine.Board) -> dict:
        """Serialize board state for JSON."""
        return {
            "width": board.width,
            "height": board.height,
            "actual_player": board.actual_player.number,
            "players": [
                {
                    "number": p.number,
                    "active": p.active,
                    "amount": p.amount,
                    "is_bot": hasattr(p, 'is_bot') and p.is_bot,
                    "color": p.color
                }
                for p in board.players
            ],
            "squares": [
                [
                    {
                        "value": board[x, y].value,
                        "player": board[x, y].player.number if board[x, y].player else None,
                        "color": board[x, y].color
                    }
                    for y in range(board.height)
                ]
                for x in range(board.width)
            ],
            "is_expecting_move": board.is_expecting_move(),
            "is_victory": board.is_victory(),
            "history_position": board.history_position,
            "history_length": len(board.history)
        }


# Global game manager
game_manager = GameManager()

# FastAPI app
app = FastAPI(title="The Great Privatization API", version="0.2.0")

# Mount static files for web UI
static_dir = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")


@app.get("/", response_class=HTMLResponse)
async def get_index():
    """Serve the main HTML page."""
    html_file = os.path.join(os.path.dirname(__file__), "static", "index.html")
    if os.path.exists(html_file):
        return FileResponse(html_file)
    else:
        # Inline HTML if static files don't exist yet
        return HTMLResponse("""
        <!DOCTYPE html>
        <html>
        <head>
            <title>The Great Privatization</title>
        </head>
        <body>
            <h1>The Great Privatization Web Interface</h1>
            <p>Web interface will be available soon. Use API endpoints:</p>
            <ul>
                <li><a href="/api/game">/api/game</a> - Get game state</li>
                <li><a href="/docs">/docs</a> - API documentation</li>
            </ul>
        </body>
        </html>
        """)


@app.get("/api/game")
async def get_game_state(game_id: str = "default"):
    """Get the current game state."""
    board = game_manager.get_game(game_id)
    if not board:
        board = game_manager.ensure_default_game()
    
    listener = GameUpdateListener(game_manager, game_id)
    return listener._serialize_board(board)


@app.post("/api/game/new")
async def create_new_game(
    game_id: str = "default", 
    width: int = 8, 
    height: int = 8, 
    players: int = 4, 
    bots: int = 0
):
    """Create a new game."""
    try:
        created_game_id = game_manager.create_game(game_id, width, height, players, bots)
        board = game_manager.get_game(created_game_id)
        
        # Broadcast game creation
        await game_manager.broadcast_to_game(created_game_id, {
            "type": "game_created",
            "game_id": created_game_id
        })
        
        listener = GameUpdateListener(game_manager, created_game_id)
        return {
            "game_id": created_game_id,
            "game_state": listener._serialize_board(board)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/game/move")
async def make_move(x: int, y: int, game_id: str = "default"):
    """Make a move in the game."""
    board = game_manager.get_game(game_id)
    if not board:
        raise HTTPException(status_code=404, detail="Game not found")
    
    try:
        await board.play(x, y)
        
        # Broadcast move made
        await game_manager.broadcast_to_game(game_id, {
            "type": "move_made",
            "x": x,
            "y": y,
            "player": board.actual_player.number
        })
        
        listener = GameUpdateListener(game_manager, game_id)
        return listener._serialize_board(board)
        
    except engine.WinnerException as e:
        # Broadcast game over
        await game_manager.broadcast_to_game(game_id, {
            "type": "game_over",
            "winner": str(e)
        })
        
        listener = GameUpdateListener(game_manager, game_id)
        return {
            "game_over": True,
            "winner": str(e),
            "game_state": listener._serialize_board(board)
        }
        
    except engine.SquareException as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/game/history/{direction}")
async def navigate_history(direction: str, game_id: str = "default"):
    """Navigate game history (forward/backward)."""
    board = game_manager.get_game(game_id)
    if not board:
        raise HTTPException(status_code=404, detail="Game not found")
    
    try:
        step = 1 if direction == "forward" else -1
        board.history_jump(step)
        
        listener = GameUpdateListener(game_manager, game_id)
        return listener._serialize_board(board)
        
    except engine.HistoryException as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.websocket("/ws/{game_id}")
async def websocket_endpoint(websocket: WebSocket, game_id: str = "default"):
    """WebSocket endpoint for real-time game updates."""
    await websocket.accept()
    
    # Ensure game exists
    board = game_manager.get_game(game_id)
    if not board:
        board = game_manager.ensure_default_game()
        game_id = "default"
    
    await game_manager.add_connection(game_id, websocket)
    
    try:
        # Send current game state
        listener = GameUpdateListener(game_manager, game_id)
        await websocket.send_json({
            "type": "game_state",
            "game_state": listener._serialize_board(board)
        })
        
        # Handle incoming messages
        while True:
            try:
                data = await websocket.receive_json()
                
                if data.get("type") == "move":
                    x, y = data.get("x"), data.get("y")
                    if x is not None and y is not None:
                        try:
                            await board.play(x, y)
                        except engine.WinnerException as e:
                            await websocket.send_json({
                                "type": "game_over",
                                "winner": str(e)
                            })
                        except engine.SquareException as e:
                            await websocket.send_json({
                                "type": "error",
                                "message": str(e)
                            })
                            
                elif data.get("type") == "new_game":
                    width = data.get("width", 8)
                    height = data.get("height", 8)
                    players = data.get("players", 4)
                    bots = data.get("bots", 0)
                    
                    game_manager.create_game(game_id, width, height, players, bots)
                    board = game_manager.get_game(game_id)
                    
                    await websocket.send_json({
                        "type": "game_created",
                        "game_state": listener._serialize_board(board)
                    })
                    
            except json.JSONDecodeError:
                await websocket.send_json({
                    "type": "error", 
                    "message": "Invalid JSON"
                })
                
    except WebSocketDisconnect:
        await game_manager.remove_connection(game_id, websocket)


def run_server(host: str = "127.0.0.1", port: int = 8000, **kwargs):
    """Run the web server."""
    logger.info(f"Starting web server on {host}:{port}")
    uvicorn.run(app, host=host, port=port, **kwargs)


# For running directly
if __name__ == "__main__":
    import logging
    logging.basicConfig(level=logging.INFO)
    run_server()