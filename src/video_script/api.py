"""FastAPI REST API for Video Script Writer."""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, List
import uvicorn

from video_script.core import (
    generate_script,
    generate_scene_breakdown,
    suggest_broll,
    generate_hook,
    generate_thumbnail_ideas,
    estimate_duration,
    STYLES,
)

app = FastAPI(
    title="Video Script Writer API",
    description="REST API for Video Script Writer",
    version="1.0.0",
)


# ---------------------------------------------------------------------------
# Pydantic models
# ---------------------------------------------------------------------------

class GenerateScriptRequest(BaseModel):
    topic: str = Field(..., description="Video topic")
    duration: int = Field(..., description="Target duration in minutes")
    style: str = Field(..., description=f"Script style. Options: {STYLES}")
    audience: Optional[str] = Field(None, description="Target audience")


class SceneBreakdownRequest(BaseModel):
    topic: str = Field(..., description="Video topic")
    duration: int = Field(..., description="Target duration in minutes")
    style: str = Field(..., description=f"Script style. Options: {STYLES}")


class SuggestBrollRequest(BaseModel):
    topic: str = Field(..., description="Video topic")
    section_text: str = Field(..., description="Script section text for B-roll context")
    num_suggestions: int = Field(3, description="Number of B-roll suggestions")


class GenerateHookRequest(BaseModel):
    topic: str = Field(..., description="Video topic")
    style: str = Field(..., description=f"Script style. Options: {STYLES}")
    num_hooks: int = Field(3, description="Number of hooks to generate")


class ThumbnailIdeasRequest(BaseModel):
    topic: str = Field(..., description="Video topic")
    style: str = Field(..., description=f"Script style. Options: {STYLES}")
    num_ideas: int = Field(3, description="Number of thumbnail ideas")


class EstimateDurationRequest(BaseModel):
    script_text: str = Field(..., description="Full script text")


class TextResponse(BaseModel):
    result: str


class StringListResponse(BaseModel):
    items: List[str]


class DurationResponse(BaseModel):
    estimated_minutes: float


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "video-script-writer"}


@app.get("/styles")
async def get_styles():
    """Return the list of supported script styles."""
    return {"styles": STYLES}


@app.post("/generate", response_model=TextResponse)
async def api_generate_script(req: GenerateScriptRequest):
    """Generate a complete video script."""
    try:
        result = generate_script(
            topic=req.topic,
            duration=req.duration,
            style=req.style,
            audience=req.audience,
        )
        return TextResponse(result=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/scene-breakdown")
async def api_generate_scene_breakdown(req: SceneBreakdownRequest):
    """Generate a scene-by-scene breakdown."""
    try:
        sections = generate_scene_breakdown(
            topic=req.topic,
            duration=req.duration,
            style=req.style,
        )
        return {"sections": sections}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/suggest-broll", response_model=StringListResponse)
async def api_suggest_broll(req: SuggestBrollRequest):
    """Suggest B-roll footage for a script section."""
    try:
        suggestions = suggest_broll(
            topic=req.topic,
            section_text=req.section_text,
            num_suggestions=req.num_suggestions,
        )
        return StringListResponse(items=suggestions)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/hooks", response_model=StringListResponse)
async def api_generate_hook(req: GenerateHookRequest):
    """Generate attention-grabbing hooks for a video."""
    try:
        hooks = generate_hook(
            topic=req.topic,
            style=req.style,
            num_hooks=req.num_hooks,
        )
        return StringListResponse(items=hooks)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/thumbnail-ideas", response_model=StringListResponse)
async def api_generate_thumbnail_ideas(req: ThumbnailIdeasRequest):
    """Generate thumbnail ideas for a video."""
    try:
        ideas = generate_thumbnail_ideas(
            topic=req.topic,
            style=req.style,
            num_ideas=req.num_ideas,
        )
        return StringListResponse(items=ideas)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/estimate-duration", response_model=DurationResponse)
async def api_estimate_duration(req: EstimateDurationRequest):
    """Estimate the spoken duration of a script."""
    try:
        minutes = estimate_duration(script_text=req.script_text)
        return DurationResponse(estimated_minutes=minutes)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
