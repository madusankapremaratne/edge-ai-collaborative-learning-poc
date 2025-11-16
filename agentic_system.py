"""
Agentic AI System for Collaborative Learning
Implements three types of agents using template-based logic (simulating LLM inference)
"""

from typing import List, Dict, Any
from datetime import datetime, timedelta

# ============================================================================
# PERSONAL AI ASSISTANT (Runs on Student Device - Edge)
# ============================================================================
class PersonalAIAssistant:
    """
    Personal AI agent for individual students.
    Tracks own contributions and provides gentle nudges.
    """
    
    def __init__(self):
        self.nudge_templates = {
            "inactivity": {
                "icon": "📢",
                "title": "Time to Contribute!",
                "message": "You haven't contributed this week. Your team might need help with {task}.",
                "action": "Start with a 30-minute session on {task}"
            },
            "communication": {
                "icon": "💬",
                "title": "Communication Tip",
                "message": "Your recent message was quite direct. Try framing as a question: \"{suggestion}\"",
                "action": "Use collaborative language to encourage discussion"
            },
            "role_mismatch": {
                "icon": "🔄",
                "title": "Skills Alignment",
                "message": "You're strong at {your_skill}, but mostly working on {current_task}. Consider {suggestion}.",
                "action": "Explore leveraging your {your_skill} skills"
            },
            "good_work": {
                "icon": "⭐",
                "title": "Great Progress!",
                "message": "You've contributed {hours} hours this week - keep up the momentum!",
                "action": "Consider documenting your work"
            },
            "deadline_approaching": {
                "icon": "⏰",
                "title": "Milestone Approaching",
                "message": "{milestone} is due on {date}. Current task: {task}",
                "action": "Check milestone progress and coordinate with team"
            }
        }
    
    def generate_nudges(self, student: str, group_id: str, data: Dict) -> List[Dict[str, str]]:
        """Generate personalized nudges for a student."""
        nudges = []
        
        contributions = data["contributions"].get(group_id, {}).get(student, [])
        group_contribs = data["contributions"].get(group_id, {})
        total_hours = sum(c["duration_hours"] for c in contributions)
        
        # Check for inactivity
        if not contributions:
            nudges.append({
                "icon": self.nudge_templates["inactivity"]["icon"],
                "title": self.nudge_templates["inactivity"]["title"],
                "message": f"You haven't contributed yet. Your team is working on the project now!",
                "action": "Check with your group about task assignments"
            })
        elif len(contributions) > 0:
            last_contrib = max([c["date"] for c in contributions])
            days_since = (datetime.now() - last_contrib).days
            if days_since >= 3:
                tasks = list(set(c["task"] for c in contributions))
                nudges.append({
                    "icon": self.nudge_templates["inactivity"]["icon"],
                    "title": self.nudge_templates["inactivity"]["title"],
                    "message": f"It's been {days_since} days since you last worked. The team might need your help!",
                    "action": "Catch up on project progress and rejoin"
                })
        
        # Check participation balance
        all_contrib_hours = {s: sum(c["duration_hours"] for c in group_contribs.get(s, []))
                            for s in group_contribs.keys()}
        max_hours = max(all_contrib_hours.values()) if all_contrib_hours else 0
        avg_hours = sum(all_contrib_hours.values()) / len(all_contrib_hours) if all_contrib_hours else 0
        
        if max_hours > 0 and total_hours < avg_hours * 0.5:
            nudges.append({
                "icon": "⚖️",
                "title": "Ensure Fair Load",
                "message": f"You've contributed {total_hours} hours while others are doing more. "
                          f"Consider taking on additional tasks?",
                "action": "Discuss workload distribution with team"
            })
        
        # Positive reinforcement
        if total_hours >= 5:
            nudges.append({
                "icon": self.nudge_templates["good_work"]["icon"],
                "title": self.nudge_templates["good_work"]["title"],
                "message": f"Great work! You've contributed {total_hours} hours. Keep the momentum!",
                "action": "Keep up the consistent effort"
            })
        
        # Deadline check
        milestones = data["milestones"].get(group_id, [])
        upcoming = [m for m in milestones if m["status"] == "In Progress" or m["status"] == "Not Started"]
        if upcoming:
            nudges.append({
                "icon": self.nudge_templates["deadline_approaching"]["icon"],
                "title": self.nudge_templates["deadline_approaching"]["title"],
                "message": f"'{upcoming[0]['name']}' is due {upcoming[0]['due_date']}. "
                          f"Current status: {upcoming[0]['status']}",
                "action": "Coordinate timing with your team"
            })
        
        return nudges if nudges else [
            {
                "icon": "✅",
                "title": "All Good!",
                "message": "You're on track. Keep collaborating with your team.",
                "action": "Continue with current tasks"
            }
        ]

# ============================================================================
# GROUP AI FACILITATOR (Team-Level Coordination)
# ============================================================================
class GroupAIFacilitator:
    """
    Group-level AI agent that analyzes team dynamics and facilitates collaboration.
    """
    
    def __init__(self):
        self.imbalance_threshold = 0.6  # If one person does >60%, flag it
    
    def analyze_group(self, group_id: str, data: Dict) -> Dict[str, Any]:
        """Comprehensive group analysis."""
        analysis = {
            "group_id": group_id,
            "group_name": data["groups"][group_id]["name"],
            "timestamp": datetime.now().isoformat(),
            "metrics": {}
        }
        
        contributions = data["contributions"].get(group_id, {})
        students = data["groups"][group_id]["students"]
        
        # Calculate contribution metrics
        total_hours = 0
        individual_hours = {}
        
        for student in students:
            hours = sum(c["duration_hours"] for c in contributions.get(student, []))
            individual_hours[student] = hours
            total_hours += hours
        
        analysis["metrics"]["total_hours"] = total_hours
        analysis["metrics"]["individual_hours"] = individual_hours
        analysis["metrics"]["avg_hours"] = total_hours / len(students) if students else 0
        analysis["metrics"]["participation_rate"] = len([h for h in individual_hours.values() if h > 0]) / len(students)
        
        return analysis
    
    def detect_imbalances(self, group_id: str, data: Dict) -> List[Dict[str, str]]:
        """Detect participation imbalances and potential issues."""
        alerts = []
        
        contributions = data["contributions"].get(group_id, {})
        students = data["groups"][group_id]["students"]
        
        individual_hours = {s: sum(c["duration_hours"] for c in contributions.get(s, []))
                           for s in students}
        total_hours = sum(individual_hours.values())
        
        # Find overloaded students
        for student, hours in individual_hours.items():
            if total_hours > 0:
                percentage = hours / total_hours
                if percentage > self.imbalance_threshold:
                    alerts.append({
                        "severity": "high",
                        "student": student,
                        "message": f"⚠️ **{student}** is doing {percentage*100:.1f}% of the work. "
                                  f"Consider redistributing tasks for better balance."
                    })
        
        # Find inactive students
        inactive = [s for s, h in individual_hours.items() if h == 0]
        if inactive:
            alerts.append({
                "severity": "high",
                "message": f"🔴 {', '.join(inactive)} {'has' if len(inactive) == 1 else 'have'} "
                          f"not contributed yet. Immediate action needed."
            })
        
        # Check milestone progress
        milestones = data["milestones"].get(group_id, [])
        overdue = [m for m in milestones if m["status"] == "Not Started" and 
                  datetime.strptime(m["due_date"], "%Y-%m-%d") < datetime.now()]
        if overdue:
            alerts.append({
                "severity": "high",
                "message": f"🔴 Milestone '{overdue[0]['name']}' is overdue. Urgent: catch up required."
            })
        
        # Check for communication issues
        communications = data["communications"].get(group_id, [])
        urgent_msgs = [c for c in communications if c["tone"] == "urgent"]
        if urgent_msgs:
            alerts.append({
                "severity": "medium",
                "message": f"🟡 Team communication shows urgency. {len(urgent_msgs)} urgent message(s) detected. "
                          f"Consider team sync."
            })
        
        return alerts
    
    def suggest_rebalancing(self, group_id: str, data: Dict) -> List[Dict[str, str]]:
        """Suggest task rebalancing strategies."""
        suggestions = []
        
        contributions = data["contributions"].get(group_id, {})
        students = data["groups"][group_id]["students"]
        
        individual_hours = {s: sum(c["duration_hours"] for c in contributions.get(s, []))
                           for s in students}
        
        # Find overloaded and underutilized
        overloaded = [s for s, h in individual_hours.items() if h > 5]
        underutilized = [s for s, h in individual_hours.items() if h < 2]
        
        if overloaded and underutilized:
            suggestions.append({
                "type": "rebalance",
                "message": f"Move some tasks from {overloaded[0]} to {underutilized[0]} for better balance.",
                "rationale": "Improves team equity and engagement"
            })
        
        return suggestions

# ============================================================================
# INSTRUCTOR DASHBOARD AGENT
# ============================================================================
class InstructorDashboard:
    """
    Instructor-level AI agent that provides high-level alerts and recommendations.
    Filters noise and only alerts on critical issues.
    """
    
    def __init__(self):
        self.alert_threshold = 0.5  # Only alert if >50% of team is inactive
    
    def generate_alerts(self, data: Dict) -> List[Dict[str, str]]:
        """Generate critical alerts for instructor attention."""
        alerts = []
        
        for group_id, group_info in data["groups"].items():
            group_alerts = self.get_group_alerts(group_id, data)
            
            # Only escalate critical issues
            critical = [a for a in group_alerts if a.get("severity") == "high"]
            if len(critical) >= 2:  # Multiple critical issues
                alerts.append({
                    "priority": "critical",
                    "group": group_info["name"],
                    "message": f"Multiple issues detected: {', '.join([a['message'][:30] for a in critical])}",
                    "action": "Review group immediately"
                })
            elif critical:
                alerts.append({
                    "priority": "warning",
                    "group": group_info["name"],
                    "message": critical[0]["message"],
                    "action": "Monitor this group"
                })
        
        return alerts
    
    def get_group_alerts(self, group_id: str, data: Dict) -> List[Dict[str, str]]:
        """Get all alerts for a specific group."""
        facilitator = GroupAIFacilitator()
        return facilitator.detect_imbalances(group_id, data)
    
    def get_recommendations(self, data: Dict) -> List[Dict[str, str]]:
        """Get actionable recommendations for instructor."""
        recommendations = []
        
        for group_id, group_info in data["groups"].items():
            if group_info["status"] == "At Risk":
                recommendations.append({
                    "title": f"Support {group_info['name']}",
                    "description": f"This group is at risk. Consider scheduling a check-in or providing additional resources.",
                    "target_group": group_info["name"],
                    "impact": "High - Could improve group success rate"
                })
        
        # Check for patterns
        facilitator = GroupAIFacilitator()
        all_analyses = {
            gid: facilitator.analyze_group(gid, data)
            for gid in data["groups"].keys()
        }
        
        # If overall participation is low
        avg_participation = sum(a["metrics"]["participation_rate"] for a in all_analyses.values()) / len(all_analyses)
        if avg_participation < 0.8:
            recommendations.append({
                "title": "Course-Wide Engagement",
                "description": "Overall participation is lower than expected. Consider sending a reminder email or hosting an office hour.",
                "target_group": "Whole Class",
                "impact": "Medium - Could boost overall engagement"
            })
        
        return recommendations
    
    def generate_summary(self, data: Dict) -> Dict[str, Any]:
        """Generate executive summary for instructor."""
        summary = {
            "total_groups": len(data["groups"]),
            "thriving": sum(1 for g in data["groups"].values() if g["status"] == "Thriving"),
            "healthy": sum(1 for g in data["groups"].values() if g["status"] == "Healthy"),
            "at_risk": sum(1 for g in data["groups"].values() if g["status"] == "At Risk"),
            "total_alerts": len(self.generate_alerts(data)),
            "recommendations": len(self.get_recommendations(data))
        }
        return summary
