"""
Sample dataset for distributed edge-AI agents POC
Simulates a 3-group course project scenario with student contributions
"""

import json
from datetime import datetime, timedelta
from random import random, choice, randint

# Define 3 groups with 4 students each
GROUPS = {
    "Group_A": {
        "name": "Web Development Team",
        "project": "E-commerce Platform",
        "students": ["Alice", "Bob", "Charlie", "Diana"],
        "deadline": "2024-12-20",
        "status": "At Risk"
    },
    "Group_B": {
        "name": "Data Analytics Team",
        "project": "Customer Behavior Analysis",
        "students": ["Eve", "Frank", "Grace", "Henry"],
        "deadline": "2024-12-20",
        "status": "Healthy"
    },
    "Group_C": {
        "name": "Mobile App Team",
        "project": "Task Manager App",
        "students": ["Iris", "Jack", "Kate", "Liam"],
        "deadline": "2024-12-20",
        "status": "Thriving"
    }
}

# Task categories for each project
TASK_CATEGORIES = {
    "Group_A": ["Frontend", "Backend", "Database", "Testing", "Documentation"],
    "Group_B": ["Data Collection", "Analysis", "Visualization", "Report Writing", "Presentation"],
    "Group_C": ["UI Design", "Backend Logic", "API Integration", "Testing", "Documentation"]
}

# Contribution events (last 2 weeks)
def generate_contributions():
    contributions = {}
    base_date = datetime.now() - timedelta(days=14)
    
    # Group A - Imbalanced (At Risk)
    contributions["Group_A"] = {
        "Alice": [
            {"date": base_date + timedelta(days=0, hours=14), "task": "Frontend", "action": "Committed code", "duration_hours": 2},
            {"date": base_date + timedelta(days=1, hours=10), "task": "Frontend", "action": "Reviewed PR", "duration_hours": 1},
            {"date": base_date + timedelta(days=3, hours=15), "task": "Frontend", "action": "Fixed bugs", "duration_hours": 3},
            {"date": base_date + timedelta(days=5, hours=9), "task": "Frontend", "action": "Updated component", "duration_hours": 2},
            {"date": base_date + timedelta(days=7, hours=11), "task": "Frontend", "action": "Completed feature", "duration_hours": 4},
            {"date": base_date + timedelta(days=10, hours=16), "task": "Frontend", "action": "Code review", "duration_hours": 1.5},
            {"date": base_date + timedelta(days=12, hours=13), "task": "Frontend", "action": "Merged PR", "duration_hours": 1},
        ],
        "Bob": [
            {"date": base_date + timedelta(days=1, hours=14), "task": "Backend", "action": "Designed API", "duration_hours": 3},
            {"date": base_date + timedelta(days=4, hours=10), "task": "Backend", "action": "Implemented endpoint", "duration_hours": 4},
            {"date": base_date + timedelta(days=8, hours=15), "task": "Backend", "action": "Fixed issues", "duration_hours": 2},
            {"date": base_date + timedelta(days=11, hours=9), "task": "Backend", "action": "Deployed", "duration_hours": 1},
        ],
        "Charlie": [
            {"date": base_date + timedelta(days=2, hours=14), "task": "Database", "action": "Created schema", "duration_hours": 2},
        ],
        "Diana": []  # No contributions yet
    }
    
    # Group B - Balanced (Healthy)
    contributions["Group_B"] = {
        "Eve": [
            {"date": base_date + timedelta(days=0, hours=10), "task": "Data Collection", "action": "Scraped data", "duration_hours": 3},
            {"date": base_date + timedelta(days=3, hours=14), "task": "Analysis", "action": "Cleaned dataset", "duration_hours": 2},
            {"date": base_date + timedelta(days=7, hours=11), "task": "Visualization", "action": "Created charts", "duration_hours": 2.5},
        ],
        "Frank": [
            {"date": base_date + timedelta(days=1, hours=15), "task": "Data Collection", "action": "Gathered sources", "duration_hours": 2},
            {"date": base_date + timedelta(days=4, hours=10), "task": "Analysis", "action": "Statistical test", "duration_hours": 3},
            {"date": base_date + timedelta(days=9, hours=13), "task": "Report Writing", "action": "Drafted section", "duration_hours": 2},
        ],
        "Grace": [
            {"date": base_date + timedelta(days=2, hours=11), "task": "Analysis", "action": "Data profiling", "duration_hours": 2.5},
            {"date": base_date + timedelta(days=5, hours=14), "task": "Visualization", "action": "Dashboard design", "duration_hours": 3},
            {"date": base_date + timedelta(days=10, hours=10), "task": "Report Writing", "action": "Finalized report", "duration_hours": 1.5},
        ],
        "Henry": [
            {"date": base_date + timedelta(days=3, hours=13), "task": "Analysis", "action": "Correlation analysis", "duration_hours": 2},
            {"date": base_date + timedelta(days=6, hours=15), "task": "Presentation", "action": "Created slides", "duration_hours": 3},
            {"date": base_date + timedelta(days=11, hours=9), "task": "Report Writing", "action": "Peer review", "duration_hours": 1},
        ]
    }
    
    # Group C - Excellent (Thriving)
    contributions["Group_C"] = {
        "Iris": [
            {"date": base_date + timedelta(days=0, hours=10), "task": "UI Design", "action": "Created mockups", "duration_hours": 4},
            {"date": base_date + timedelta(days=4, hours=14), "task": "UI Design", "action": "Refined design", "duration_hours": 2.5},
            {"date": base_date + timedelta(days=8, hours=11), "task": "Frontend", "action": "Implemented UI", "duration_hours": 3},
        ],
        "Jack": [
            {"date": base_date + timedelta(days=1, hours=15), "task": "Backend Logic", "action": "Core logic", "duration_hours": 4},
            {"date": base_date + timedelta(days=5, hours=10), "task": "API Integration", "action": "Connected API", "duration_hours": 3},
            {"date": base_date + timedelta(days=10, hours=13), "task": "Testing", "action": "Unit tests", "duration_hours": 2},
        ],
        "Kate": [
            {"date": base_date + timedelta(days=2, hours=14), "task": "Backend Logic", "action": "Database layer", "duration_hours": 3},
            {"date": base_date + timedelta(days=6, hours=11), "task": "API Integration", "action": "Error handling", "duration_hours": 2},
            {"date": base_date + timedelta(days=9, hours=15), "task": "Testing", "action": "Integration tests", "duration_hours": 2.5},
        ],
        "Liam": [
            {"date": base_date + timedelta(days=3, hours=13), "task": "Testing", "action": "QA testing", "duration_hours": 2},
            {"date": base_date + timedelta(days=7, hours=10), "task": "Documentation", "action": "API docs", "duration_hours": 3},
            {"date": base_date + timedelta(days=11, hours=14), "task": "Documentation", "action": "User guide", "duration_hours": 2},
        ]
    }
    
    return contributions

# Communication records
def generate_communications():
    communications = {
        "Group_A": [
            {"date": "2024-12-10", "from": "Alice", "to": "Diana", "message": "Diana, can you help with database setup?", "tone": "direct"},
            {"date": "2024-12-11", "from": "Bob", "to": "Group", "message": "Need database schema ASAP", "tone": "urgent"},
            {"date": "2024-12-12", "from": "Charlie", "to": "Alice", "message": "Schema done but backend might need tweaks", "tone": "informative"},
        ],
        "Group_B": [
            {"date": "2024-12-10", "from": "Eve", "to": "Group", "message": "Data collected! Everyone please validate", "tone": "collaborative"},
            {"date": "2024-12-11", "from": "Grace", "to": "Eve", "message": "Great work! I'll start analysis", "tone": "supportive"},
        ],
        "Group_C": [
            {"date": "2024-12-10", "from": "Iris", "to": "Group", "message": "Mockups ready for feedback", "tone": "collaborative"},
            {"date": "2024-12-11", "from": "Jack", "to": "Iris", "message": "Looks great! Starting backend development", "tone": "supportive"},
        ]
    }
    return communications

# Milestones
def generate_milestones():
    milestones = {
        "Group_A": [
            {"name": "Requirements Document", "due_date": "2024-11-30", "status": "Completed"},
            {"name": "Design & Architecture", "due_date": "2024-12-05", "status": "Completed"},
            {"name": "Core Features Implementation", "due_date": "2024-12-15", "status": "In Progress"},
            {"name": "Testing & QA", "due_date": "2024-12-18", "status": "Not Started"},
        ],
        "Group_B": [
            {"name": "Data Collection Plan", "due_date": "2024-12-02", "status": "Completed"},
            {"name": "Raw Data Gathered", "due_date": "2024-12-08", "status": "Completed"},
            {"name": "Analysis & Visualization", "due_date": "2024-12-15", "status": "In Progress"},
            {"name": "Final Report & Presentation", "due_date": "2024-12-20", "status": "Not Started"},
        ],
        "Group_C": [
            {"name": "Design Phase", "due_date": "2024-12-05", "status": "Completed"},
            {"name": "Development Sprint 1", "due_date": "2024-12-12", "status": "Completed"},
            {"name": "Development Sprint 2", "due_date": "2024-12-17", "status": "In Progress"},
            {"name": "Deployment & Documentation", "due_date": "2024-12-20", "status": "Scheduled"},
        ]
    }
    return milestones

# Generate all data
def get_all_data():
    return {
        "groups": GROUPS,
        "contributions": generate_contributions(),
        "communications": generate_communications(),
        "milestones": generate_milestones()
    }

if __name__ == "__main__":
    data = get_all_data()
    print(json.dumps(data, indent=2, default=str))
