# backend/app/main.py
from fastapi import FastAPI, HTTPException, Depends, Body
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import datetime
import os

# Import our modules with local paths
from integrations.google_calendar import get_upcoming_events, analyze_calendar_data, get_today_events
from task_management import TaskManager
from ai.recommendation_engine import RecommendationEngine

app = FastAPI(title="AI Productivity Assistant API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For production, restrict this to your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create instances of our services
task_manager = TaskManager()
recommendation_engine = RecommendationEngine()

# Pydantic models for request/response validation
class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = ""
    due_date: Optional[str] = None
    priority: int = 2
    estimated_time: int = 30
    category: str = "Work"

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    due_date: Optional[str] = None
    priority: Optional[int] = None
    estimated_time: Optional[int] = None
    category: Optional[str] = None
    completed: Optional[bool] = None

# Routes for tasks
@app.get("/tasks", response_model=List[dict])
async def get_tasks(include_completed: bool = False):
    return task_manager.get_tasks(include_completed)

@app.post("/tasks", response_model=dict)
async def create_task(task: TaskCreate):
    return task_manager.add_task(
        title=task.title,
        description=task.description,
        due_date=task.due_date,
        priority=task.priority,
        estimated_time=task.estimated_time,
        category=task.category
    )

@app.get("/tasks/{task_id}", response_model=dict)
async def get_task(task_id: str):
    task = task_manager.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@app.put("/tasks/{task_id}", response_model=dict)
async def update_task(task_id: str, task_update: TaskUpdate):
    updated_task = task_manager.update_task(task_id, **task_update.dict(exclude_unset=True))
    if not updated_task:
        raise HTTPException(status_code=404, detail="Task not found")
    return updated_task

@app.put("/tasks/{task_id}/complete", response_model=dict)
async def complete_task(task_id: str):
    completed_task = task_manager.complete_task(task_id)
    if not completed_task:
        raise HTTPException(status_code=404, detail="Task not found")
    return completed_task

@app.delete("/tasks/{task_id}")
async def delete_task(task_id: str):
    success = task_manager.delete_task(task_id)
    if not success:
        raise HTTPException(status_code=404, detail="Task not found")
    return {"message": "Task deleted successfully"}

# Routes for calendar
@app.get("/calendar/events")
async def get_calendar_events(days: int = 7):
    try:
        events = get_upcoming_events(days)
        return {"events": events}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching calendar events: {str(e)}")

@app.get("/calendar/analysis")
async def get_calendar_analysis():
    try:
        events = get_upcoming_events(days=14)
        analysis = analyze_calendar_data(events)
        return analysis
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analyzing calendar data: {str(e)}")

# Routes for recommendations
@app.get("/recommendations/schedule")
async def get_schedule_recommendations():
    try:
        events = get_upcoming_events(days=1)
        tasks = task_manager.prioritize_tasks()
        recommendations = recommendation_engine.get_schedule_recommendation(events, tasks)
        return recommendations
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating recommendations: {str(e)}")

@app.get("/recommendations/smart")
async def get_smart_recommendations():
    try:
        events = get_upcoming_events(days=1)
        tasks = task_manager.prioritize_tasks()
        completed_tasks = [t for t in task_manager.get_tasks(include_completed=True) if t['completed']]
        recommendations = recommendation_engine.get_smart_recommendations(events, tasks, completed_tasks)
        return recommendations
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating smart recommendations: {str(e)}")

# Dashboard data
@app.get("/dashboard")
async def get_dashboard_data():
    try:
        # Get all the data needed for the dashboard
        events = get_upcoming_events(days=7)
        calendar_analysis = analyze_calendar_data(events)
        tasks = task_manager.get_tasks(include_completed=False)
        completed_tasks = [t for t in task_manager.get_tasks(include_completed=True) if t['completed']]
        
        # Get today's scheduled meetings
        today = datetime.datetime.now().date()
        today_events = [
            e for e in events 
            if 'T' in e['start'] and datetime.datetime.fromisoformat(
                e['start'].replace('Z', '+00:00')).date() == today
        ]
        
        # Get recommendations
        smart_recs = recommendation_engine.get_smart_recommendations(events, tasks, completed_tasks)
        
        return {
            "calendar": {
                "events": events,
                "analysis": calendar_analysis,
                "today_events": today_events
            },
            "tasks": {
                "pending": tasks,
                "completed": completed_tasks,
                "total_pending": len(tasks),
                "total_completed": len(completed_tasks),
                "high_priority": len([t for t in tasks if t['priority'] == 1])
            },
            "recommendations": smart_recs['recommendations'],
            "priority_recommendation": smart_recs['priority_recommendation']
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating dashboard data: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)