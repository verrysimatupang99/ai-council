"""
FastAPI Backend for AI Council Dashboard
"""

import os
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from ...core.config import Config
from ...core.council import CouncilCoordinator

app = FastAPI(title="AI Council Dashboard")

# Initialize coordinator
config = Config()
coordinator = CouncilCoordinator(config)

# Get the directory of the current file
current_dir = Path(__file__).parent
static_dir = current_dir / "static"

@app.get("/api/sessions")
async def get_sessions():
    """Get all discussion sessions"""
    try:
        return coordinator.storage.get_history(limit=50)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/sessions/{session_id}")
async def get_session_details(session_id: str):
    """Get full details for a specific session"""
    session = coordinator.storage.get_session_details(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session

# Serve static files
app.mount("/", StaticFiles(directory=str(static_dir), html=True), name="static")

@app.get("/")
async def read_index():
    return FileResponse(str(static_dir / "index.html"))
