# frontend/app.py
import streamlit as st
import pandas as pd
import requests
import datetime
import json
import altair as alt
from typing import List, Dict
import os

# API Configuration
API_URL = "http://localhost:8000"

# Set page config
st.set_page_config(
    page_title="AI Productivity Assistant",
    page_icon="✅",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Helper functions
def fetch_dashboard_data():
    """Fetch all dashboard data from the API."""
    try:
        response = requests.get(f"{API_URL}/dashboard")
        return response.json() if response.status_code == 200 else None
    except Exception as e:
        st.error(f"Error connecting to the API: {str(e)}")
        return None

def add_task(task_data):
    """Add a new task via the API."""
    try:
        response = requests.post(f"{API_URL}/tasks", json=task_data)
        return response.json() if response.status_code == 200 else None
    except Exception as e:
        st.error(f"Error adding task: {str(e)}")
        return None

def complete_task(task_id):
    """Mark a task as complete via the API."""
    try:
        response = requests.put(f"{API_URL}/tasks/{task_id}/complete")
        return response.json() if response.status_code == 200 else None
    except Exception as e:
        st.error(f"Error completing task: {str(e)}")
        return None

def delete_task(task_id):
    """Delete a task via the API."""
    try:
        response = requests.delete(f"{API_URL}/tasks/{task_id}")
        return response.status_code == 200
    except Exception as e:
        st.error(f"Error deleting task: {str(e)}")
        return False

# App title
st.title("AI Productivity Assistant")

# Sidebar
st.sidebar.header("Navigation")
page = st.sidebar.selectbox("Choose a page", ["Dashboard", "Tasks", "Calendar", "Recommendations"])

# Fetch data
dashboard_data = fetch_dashboard_data()

if dashboard_data:
    # Display priority recommendation
    if dashboard_data.get('priority_recommendation'):
        rec = dashboard_data['priority_recommendation']
        rec_type = rec['type']
        
        if rec_type == 'break':
            st.info(rec['message'])
        elif rec_type == 'focus':
            st.success(rec['message'])
        elif rec_type == 'meeting_prep':
            st.warning(rec['message'])
        else:
            st.info(rec['message'])
    
    # Dashboard Page
    if page == "Dashboard":
        # Create three columns
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Today's Schedule")
            today_events = dashboard_data['calendar']['today_events']
            
            if today_events:
                for event in today_events:
                    start_time = datetime.datetime.fromisoformat(event['start'].replace('Z', '+00:00')).strftime('%I:%M %p')
                    st.write(f"**{start_time}** - {event['summary']}")
            else:
                st.write("No meetings scheduled for today.")
                
            st.subheader("Tasks Overview")
            tasks_data = {
                "Category": ["Pending", "Completed", "High Priority"],
                "Count": [
                    dashboard_data['tasks']['total_pending'],
                    dashboard_data['tasks']['total_completed'],
                    dashboard_data['tasks']['high_priority']
                ]
            }
            tasks_df = pd.DataFrame(tasks_data)
            
            # Create a simple bar chart
            chart = alt.Chart(tasks_df).mark_bar().encode(
                x='Category',
                y='Count',
                color=alt.Color('Category', scale=alt.Scale(
                    domain=['Pending', 'Completed', 'High Priority'],
                    range=['#ff9f1c', '#2ec4b6', '#e71d36']
                ))
            ).properties(height=200)
            
            st.altair_chart(chart, use_container_width=True)
        
        with col2:
            st.subheader("Smart Recommendations")
            
            for rec in dashboard_data['recommendations']:
                if rec['type'] == 'break':
                    st.info(rec['message'])
                elif rec['type'] == 'focus':
                    st.success(rec['message'])
                elif rec['type'] == 'meeting_prep':
                    st.warning(rec['message'])
                else:
                    st.info(rec['message'])
            
            st.subheader("Calendar Analysis")
            st.write(f"**Total meetings:** {dashboard_data['calendar']['analysis']['total_meetings']}")
            st.write(f"**Meeting hours:** {dashboard_data['calendar']['analysis']['total_meeting_hours']}")
            st.write(f"**Avg. meeting duration:** {dashboard_data['calendar']['analysis']['avg_meeting_duration']} hours")
            st.write(f"**Busiest day:** {dashboard_data['calendar']['analysis']['busiest_day']}")
    
    # Tasks Page
    elif page == "Tasks":
        st.subheader("Manage Your Tasks")
        
        # Form to add a new task
        with st.expander("Add New Task"):
            with st.form("task_form"):
                title = st.text_input("Task Title")
                col1, col2 = st.columns(2)
                with col1:
                    priority = st.selectbox("Priority", [1, 2, 3], format_func=lambda x: {1: "High", 2: "Medium", 3: "Low"}[x])
                    category = st.selectbox("Category", ["Work", "Personal", "Health", "Learning"])
                with col2:
                    due_date = st.date_input("Due Date (Optional)")
                    estimated_time = st.number_input("Estimated Time (min)", min_value=5, value=30, step=5)
                
                description = st.text_area("Description (Optional)")
                
                submit = st.form_submit_button("Add Task")
                
                if submit and title:
                    task_data = {
                        "title": title,
                        "description": description,
                        "due_date": due_date.isoformat() if due_date else None,
                        "priority": priority,
                        "estimated_time": estimated_time,
                        "category": category
                    }
                    
                    result = add_task(task_data)
                    if result:
                        st.success("Task added successfully!")
                        # Refresh data
                        dashboard_data = fetch_dashboard_