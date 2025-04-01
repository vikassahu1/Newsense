# backend/app/task_management.py
import datetime
import uuid
from typing import List, Dict, Optional
import json
import os

class TaskManager:
    def __init__(self, data_file='data/tasks.json'):
        self.data_file = data_file
        self.tasks: List[Dict] = self._load_tasks()
        
    def _load_tasks(self) -> List[Dict]:
        """Load tasks from the JSON file or return an empty list."""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                return []
        else:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(self.data_file), exist_ok=True)
            return []
    
    def _save_tasks(self):
        """Save tasks to the JSON file."""
        with open(self.data_file, 'w') as f:
            json.dump(self.tasks, f, indent=2)
    
    def add_task(self, title: str, description: str = "", 
                 due_date: Optional[str] = None, 
                 priority: int = 2, 
                 estimated_time: int = 30,
                 category: str = "Work") -> Dict:
        """
        Add a new task. 
        Priority: 1 (High), 2 (Medium), 3 (Low)
        Estimated time in minutes
        """
        task = {
            "id": str(uuid.uuid4()),
            "title": title,
            "description": description,
            "due_date": due_date,
            "priority": priority,
            "estimated_time": estimated_time,
            "category": category,
            "completed": False,
            "created_at": datetime.datetime.now().isoformat()
        }
        
        self.tasks.append(task)
        self._save_tasks()
        return task
    
    def get_tasks(self, include_completed: bool = False) -> List[Dict]:
        """Get all tasks, optionally filtering out completed ones."""
        if include_completed:
            return self.tasks
        return [task for task in self.tasks if not task.get('completed', False)]
    
    def get_task(self, task_id: str) -> Optional[Dict]:
        """Get a specific task by ID."""
        for task in self.tasks:
            if task["id"] == task_id:
                return task
        return None
    
    def update_task(self, task_id: str, **kwargs) -> Optional[Dict]:
        """Update a task with the provided fields."""
        task = self.get_task(task_id)
        if task:
            for key, value in kwargs.items():
                if value is not None:
                    task[key] = value
            task["updated_at"] = datetime.datetime.now().isoformat()
            self._save_tasks()
        return task
    
    def complete_task(self, task_id: str) -> Optional[Dict]:
        """Mark a task as completed."""
        return self.update_task(task_id, completed=True)
    
    def delete_task(self, task_id: str) -> bool:
        """Delete a task by ID."""
        task = self.get_task(task_id)
        if task:
            self.tasks.remove(task)
            self._save_tasks()
            return True
        return False
    
    def prioritize_tasks(self) -> List[Dict]:
        """
        Prioritize tasks based on due date, priority, and estimated time.
        This is a basic prioritization algorithm - in a real app, you'd use ML.
        """
        # Sort tasks by priority and due date
        sorted_tasks = sorted(
            self.get_tasks(),
            key=lambda x: (x.get('priority', 2), x.get('due_date', '9999-12-31'))
        )
        return sorted_tasks