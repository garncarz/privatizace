import pytest
import asyncio
import json
from fastapi.testclient import TestClient

from privatizace import web, engine


@pytest.fixture
def client():
    """Create a test client for the web API."""
    return TestClient(web.app)


@pytest.fixture
def game_manager():
    """Create a fresh game manager for testing."""
    manager = web.GameManager()
    manager.create_game("test", width=4, height=4, players=2, bots=0)
    return manager


def test_get_game_state(client):
    """Test getting game state via REST API."""
    # Ensure there's a default game
    web.game_manager.ensure_default_game()
    
    response = client.get("/api/game")
    assert response.status_code == 200
    
    data = response.json()
    assert "width" in data
    assert "height" in data
    assert "players" in data
    assert "squares" in data
    assert data["width"] == 8  # default width
    assert data["height"] == 8  # default height


def test_create_new_game(client):
    """Test creating a new game via REST API."""
    response = client.post("/api/game/new", params={
        "width": 4,
        "height": 4,
        "players": 2,
        "bots": 0
    })
    assert response.status_code == 200
    
    data = response.json()
    assert "game_id" in data
    assert "game_state" in data
    assert data["game_state"]["width"] == 4
    assert data["game_state"]["height"] == 4
    assert len(data["game_state"]["players"]) == 2


@pytest.mark.asyncio
async def test_make_move(client):
    """Test making a move via REST API."""
    # Create a test game
    response = client.post("/api/game/new", params={
        "width": 4,
        "height": 4,
        "players": 2,
        "bots": 0
    })
    assert response.status_code == 200
    
    # Make a move
    response = client.post("/api/game/move", params={
        "x": 0,
        "y": 0
    })
    assert response.status_code == 200
    
    data = response.json()
    # The square should now have value 1 and belong to player 0
    assert data["squares"][0][0]["value"] == 1
    assert data["squares"][0][0]["player"] == 0


def test_history_navigation(client):
    """Test history navigation via REST API."""
    # Create a game and make a move first
    client.post("/api/game/new", params={
        "width": 4,
        "height": 4,
        "players": 2,
        "bots": 0
    })
    
    client.post("/api/game/move", params={"x": 0, "y": 0})
    
    # Go back in history
    response = client.post("/api/game/history/backward")
    assert response.status_code == 200
    
    data = response.json()
    # Should be back at the initial state
    assert data["history_position"] == 0


def test_invalid_move(client):
    """Test invalid move handling."""
    # Create a game
    client.post("/api/game/new", params={
        "width": 4,
        "height": 4,
        "players": 2,
        "bots": 0
    })
    
    # Make the same move twice (second should fail)
    client.post("/api/game/move", params={"x": 0, "y": 0})
    response = client.post("/api/game/move", params={"x": 0, "y": 0})
    
    # Should get a 400 error for invalid move
    assert response.status_code == 400


def test_game_serialization(game_manager):
    """Test game state serialization."""
    board = game_manager.get_game("test")
    listener = web.GameUpdateListener(game_manager, "test")
    
    serialized = listener._serialize_board(board)
    
    assert serialized["width"] == 4
    assert serialized["height"] == 4
    assert len(serialized["players"]) == 2
    assert len(serialized["squares"]) == 4
    assert len(serialized["squares"][0]) == 4
    assert serialized["is_expecting_move"] is True
    assert serialized["is_victory"] is False


@pytest.mark.asyncio
async def test_websocket_connection():
    """Test WebSocket connection functionality."""
    # This is a basic test - full WebSocket testing would require more setup
    manager = web.GameManager()
    manager.create_game("test-ws", width=4, height=4, players=2, bots=0)
    
    # Test that the manager can handle connections
    assert "test-ws" in manager.games
    assert "test-ws" in manager.connections
    assert len(manager.connections["test-ws"]) == 0


def test_root_endpoint(client):
    """Test the root endpoint serves HTML."""
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers.get("content-type", "")