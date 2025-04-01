# backend/app/ai/recommendation_engine.py
import datetime
import random
from typing import List, Dict, Any

class RecommendationEngine:
    def __init__(self):
        self.focus_tips = [
            "Close email and messaging apps during your focus time",
            "Use the Pomodoro Technique: 25 minutes of focus followed by a 5-minute break",
            "Work on your most challenging task during your peak energy hours",
            "Try noise-canceling headphones or background noise to minimize distractions",
            "Set clear goals for each work session"
        ]
        
        self.break_recommendations = [
            "Take a short walk to refresh your mind",
            "Do a quick stretching routine to reduce tension",
            "Practice deep breathing for 2 minutes",
            "Look at something 20 feet away for 20 seconds to reduce eye strain",
            "Hydrate with a glass of water"
        ]
    
    def get_schedule_recommendation(self, events: List[Dict], tasks: List[Dict]) -> Dict[str, Any]:
        """
        Generate schedule recommendations based on events and tasks.
        For now, return mock data.
        """
        return {
            "recommendations": [
                {
                    "type": "focus",
                    "message": "Consider scheduling your high-priority tasks in the morning when you're most productive."
                },
                {
                    "type": "break",
                    "message": "Take a 15-minute break between meetings to recharge."
                }
            ]
        }
    
    def get_smart_recommendations(self, events: List[Dict], tasks: List[Dict], completed_tasks: List[Dict]) -> Dict[str, Any]:
        """
        Generate smart recommendations based on events, tasks, and completed tasks.
        For now, return mock data.
        """
        # Mock priority recommendation
        priority_rec = {
            "type": "focus",
            "message": "Focus on completing the high-priority project review task before the team meeting."
        }

        # Mock general recommendations
        recommendations = [
            {
                "type": "break",
                "message": "You have a 30-minute gap between meetings. Perfect time for a short break."
            },
            {
                "type": "meeting_prep",
                "message": "Prepare for the upcoming team meeting by reviewing the project status."
            }
        ]

        return {
            "priority_recommendation": priority_rec,
            "recommendations": recommendations
        }
    
    def get_focus_recommendation(self) -> str:
        """Get a random focus tip."""
        return random.choice(self.focus_tips)
    
    def get_break_recommendation(self) -> str:
        """Get a random break recommendation."""
        return random.choice(self.break_recommendations)