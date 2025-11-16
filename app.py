"""
Distributed Edge-AI Agents for Collaborative Learning
POC Application - Streamlit Interface

Demonstrates:
1. Personal AI Assistant (Student View)
2. Group AI Facilitator (Analytics)
3. Instructor Dashboard (Supervisory)
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
from sample_data import get_all_data
from agentic_system import (
    PersonalAIAssistant,
    GroupAIFacilitator,
    InstructorDashboard
)

# Page config
st.set_page_config(
    page_title="Distributed Edge-AI Agents",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Title and description
st.title("🤖 Distributed Edge-AI Agents for Collaborative Learning")
st.markdown("""
**Multi-Agent Framework for Equitable Group Work in Project-Based Education**

This POC demonstrates how AI agents at different levels (personal, group, institutional) 
can enhance student collaboration while maintaining privacy and reducing instructor overhead.
""")

# Load data
@st.cache_data
def load_data():
    return get_all_data()

data = load_data()

# Initialize agents
@st.cache_resource
def init_agents():
    personal_assistant = PersonalAIAssistant()
    group_facilitator = GroupAIFacilitator()
    instructor_dashboard = InstructorDashboard()
    return personal_assistant, group_facilitator, instructor_dashboard

personal_ai, group_ai, instructor_ai = init_agents()

# Sidebar Navigation
st.sidebar.title("📋 Navigation")
view = st.sidebar.radio(
    "Select View",
    ["🎯 Dashboard Overview", 
     "👤 Student Assistant", 
     "👥 Group Facilitator", 
     "📊 Instructor Dashboard"]
)

st.sidebar.divider()
st.sidebar.markdown("### ℹ️ About This POC")
st.sidebar.markdown("""
**Three-Layer Architecture:**
- **Personal AI**: Runs on student devices (edge)
- **Group AI**: Coordinates team-level metrics
- **Instructor AI**: Provides high-level oversight

**Edge Models Used:**
- Personal: Granite 4.0 Nano (350M)
- Group: Qwen2.5-Coder (7B)
- Instructor: gpt-oss-20b

**Agentic Framework:** LangChain/CrewAI
""")

# ============================================================================
# VIEW 1: DASHBOARD OVERVIEW
# ============================================================================
if view == "🎯 Dashboard Overview":
    st.header("System Overview - All Groups")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Groups", len(data["groups"]))
    with col2:
        st.metric("Total Students", sum(len(g["students"]) for g in data["groups"].values()))
    with col3:
        st.metric("Active Contributions", sum(
            len([c for c in contributions if contributions[c]])
            for contributions in data["contributions"].values()
        ))
    
    st.divider()
    
    # Group Health Summary
    st.subheader("Group Health Summary")
    health_data = []
    for group_id, group_info in data["groups"].items():
        health_data.append({
            "Group": group_info["name"],
            "Project": group_info["project"],
            "Status": group_info["status"],
            "Students": len(group_info["students"]),
            "Deadline": group_info["deadline"]
        })
    
    health_df = pd.DataFrame(health_data)
    
    # Color code by status
    def status_color(status):
        if status == "Thriving":
            return "🟢"
        elif status == "Healthy":
            return "🟡"
        else:
            return "🔴"
    
    health_df["Status"] = health_df["Status"].apply(lambda x: f"{status_color(x)} {x}")
    
    st.dataframe(health_df, use_container_width=True, hide_index=True)
    
    # Participation Distribution Chart
    st.subheader("Participation Distribution (Last 2 Weeks)")
    
    participation_data = []
    for group_id, contributions in data["contributions"].items():
        for student, actions in contributions.items():
            total_hours = sum(a["duration_hours"] for a in actions)
            participation_data.append({
                "Group": data["groups"][group_id]["name"],
                "Student": student,
                "Hours": total_hours
            })
    
    part_df = pd.DataFrame(participation_data)
    
    fig = px.bar(
        part_df,
        x="Student",
        y="Hours",
        color="Group",
        title="Hours Contributed by Student (Last 2 Weeks)",
        barmode="group"
    )
    st.plotly_chart(fig, use_container_width=True)

# ============================================================================
# VIEW 2: STUDENT ASSISTANT
# ============================================================================
elif view == "👤 Student Assistant":
    st.header("Personal AI Assistant - Student View")
    st.markdown("*Simulates an AI agent running on a student's device (Edge)*")
    
    # Student selection
    all_students = []
    for group_id, group_info in data["groups"].items():
        for student in group_info["students"]:
            all_students.append((student, group_id, group_info["name"]))
    
    selected_student = st.selectbox(
        "Select Your Profile",
        options=[s[0] for s in all_students],
        format_func=lambda x: f"{x}"
    )
    
    # Find student's group
    student_group = next((s[1] for s in all_students if s[0] == selected_student), None)
    student_group_name = next((s[2] for s in all_students if s[0] == selected_student), None)
    
    if student_group:
        st.info(f"👥 **Group:** {student_group_name}")
        st.info(f"📍 **Project:** {data['groups'][student_group]['project']}")
        
        st.divider()
        
        # Personal Dashboard
        st.subheader("Your Contribution Dashboard")
        
        # Get student's contributions
        student_contribs = data["contributions"].get(student_group, {}).get(selected_student, [])
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Hours", sum(c["duration_hours"] for c in student_contribs))
        with col2:
            st.metric("Tasks Completed", len(student_contribs))
        with col3:
            st.metric("Last Activity", 
                     student_contribs[-1]["date"].strftime("%m-%d") if student_contribs else "None")
        with col4:
            st.metric("Status", "✅ Active" if student_contribs else "⚠️ Inactive")
        
        st.divider()
        
        # Personal AI Nudges (Template-based)
        st.subheader("🤖 AI Assistant Suggestions")
        
        nudges = personal_ai.generate_nudges(
            student=selected_student,
            group_id=student_group,
            data=data
        )
        
        for i, nudge in enumerate(nudges, 1):
            with st.container():
                col_icon, col_content = st.columns([0.5, 9.5])
                with col_icon:
                    st.markdown(nudge["icon"])
                with col_content:
                    st.write(f"**{nudge['title']}**")
                    st.write(nudge['message'])
                    if nudge.get('action'):
                        st.caption(f"💡 Suggested action: {nudge['action']}")
            st.divider()
        
        # Contribution History
        st.subheader("Your Contribution History")
        if student_contribs:
            contrib_df = pd.DataFrame(student_contribs)
            contrib_df['date'] = pd.to_datetime(contrib_df['date']).dt.strftime('%Y-%m-%d %H:%M')
            st.dataframe(contrib_df[['date', 'task', 'action', 'duration_hours']], 
                        use_container_width=True, hide_index=True)
        else:
            st.warning("No contributions yet. Get started!")

# ============================================================================
# VIEW 3: GROUP FACILITATOR
# ============================================================================
elif view == "👥 Group Facilitator":
    st.header("Group AI Facilitator - Team Analytics")
    st.markdown("*Analyzes group-level metrics and dynamics*")
    
    # Group selection
    group_options = [(gid, g["name"]) for gid, g in data["groups"].items()]
    selected_group = st.selectbox(
        "Select Group",
        options=[g[0] for g in group_options],
        format_func=lambda x: next(g[1] for g in group_options if g[0] == x)
    )
    
    group_info = data["groups"][selected_group]
    
    # Group Overview
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Project", group_info["project"][:15] + "...")
    with col2:
        st.metric("Team Size", len(group_info["students"]))
    with col3:
        st.metric("Status", group_info["status"])
    with col4:
        st.metric("Deadline", group_info["deadline"])
    
    st.divider()
    
    # Get group analysis
    analysis = group_ai.analyze_group(selected_group, data)
    
    # Participation Balance
    st.subheader("Participation Balance Analysis")
    
    participation = []
    for student in group_info["students"]:
        hours = sum(
            c["duration_hours"] 
            for c in data["contributions"].get(selected_group, {}).get(student, [])
        )
        participation.append({"Student": student, "Hours": hours})
    
    part_df = pd.DataFrame(participation)
    
    fig = go.Figure(data=[
        go.Bar(x=part_df["Student"], y=part_df["Hours"], 
               marker_color=['#1f77b4' if h > 0 else '#ff7f0e' for h in part_df["Hours"]])
    ])
    fig.update_layout(
        title="Hours Contributed by Team Member",
        xaxis_title="Student",
        yaxis_title="Hours",
        height=400
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Imbalance Detection
    st.subheader("🔍 Group Health Analysis")
    
    health_alerts = group_ai.detect_imbalances(selected_group, data)
    
    if health_alerts:
        for alert in health_alerts:
            if alert["severity"] == "high":
                st.error(alert["message"])
            elif alert["severity"] == "medium":
                st.warning(alert["message"])
            else:
                st.info(alert["message"])
    else:
        st.success("✅ Group balance looks healthy!")
    
    st.divider()
    
    # Milestone Tracking
    st.subheader("📅 Milestone Progress")
    
    milestones = data["milestones"].get(selected_group, [])
    for milestone in milestones:
        status_icon = "✅" if milestone["status"] == "Completed" else (
            "⏳" if milestone["status"] == "In Progress" else "⭕"
        )
        st.write(f"{status_icon} **{milestone['name']}** - {milestone['status']} (Due: {milestone['due_date']})")
    
    st.divider()
    
    # Communication Summary
    st.subheader("💬 Communication Insights")
    
    comms = data["communications"].get(selected_group, [])
    if comms:
        st.info(f"📊 {len(comms)} messages analyzed")
        for comm in comms[-3:]:  # Last 3
            st.caption(f"**{comm['from']} → {comm['to']}** ({comm['date']})")
            st.write(f"> {comm['message']}")
            st.caption(f"Tone: {comm['tone']}")
    else:
        st.info("No communications recorded yet")

# ============================================================================
# VIEW 4: INSTRUCTOR DASHBOARD
# ============================================================================
elif view == "📊 Instructor Dashboard":
    st.header("Instructor Supervisory Dashboard")
    st.markdown("*High-level overview without micromanaging - AI filters the noise*")
    
    # Overall Statistics
    st.subheader("Course Overview")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Groups", len(data["groups"]))
    with col2:
        total_students = sum(len(g["students"]) for g in data["groups"].values())
        st.metric("Students", total_students)
    with col3:
        thriving = sum(1 for g in data["groups"].values() if g["status"] == "Thriving")
        healthy = sum(1 for g in data["groups"].values() if g["status"] == "Healthy")
        at_risk = sum(1 for g in data["groups"].values() if g["status"] == "At Risk")
        st.metric("At Risk Groups", at_risk)
    with col4:
        st.metric("Course End", "2024-12-20")
    
    st.divider()
    
    # Critical Alerts
    st.subheader("⚠️ AI-Generated Alerts (Only When Necessary)")
    
    alerts = instructor_ai.generate_alerts(data)
    
    if alerts:
        for alert in alerts:
            if alert["priority"] == "critical":
                with st.container():
                    st.error(f"🔴 **{alert['group']}**: {alert['message']}")
                    st.caption(f"Recommended Action: {alert.get('action', 'Review group performance')}")
            elif alert["priority"] == "warning":
                with st.container():
                    st.warning(f"🟡 **{alert['group']}**: {alert['message']}")
    else:
        st.success("✅ All groups are performing well!")
    
    st.divider()
    
    # Group Status Matrix
    st.subheader("Group Status Summary")
    
    status_data = []
    for group_id, group_info in data["groups"].items():
        group_alerts = instructor_ai.get_group_alerts(group_id, data)
        status_data.append({
            "Group": group_info["name"],
            "Project": group_info["project"],
            "Status": group_info["status"],
            "Students": len(group_info["students"]),
            "Issues": len(group_alerts)
        })
    
    status_df = pd.DataFrame(status_data)
    
    # Highlight by status
    def highlight_status(val):
        if val == "🟢 Thriving":
            return "color: green; font-weight: bold"
        elif val == "🟡 Healthy":
            return "color: orange; font-weight: bold"
        else:
            return "color: red; font-weight: bold"
    
    st.dataframe(status_df, use_container_width=True, hide_index=True)
    
    st.divider()
    
    # Intervention Recommendations
    st.subheader("💡 Intervention Recommendations")
    
    recommendations = instructor_ai.get_recommendations(data)
    
    if recommendations:
        for i, rec in enumerate(recommendations, 1):
            with st.expander(f"**Recommendation {i}: {rec['title']}**"):
                st.write(rec["description"])
                st.info(f"**Target Group:** {rec['target_group']}")
                st.caption(f"**Impact:** {rec['impact']}")
    else:
        st.info("No specific interventions recommended at this time.")
    
    st.divider()
    
    # System Health
    st.subheader("🔧 System Health")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Edge AI Active", "✅ 12 Personal Agents")
    with col2:
        st.metric("Group Facilitators", "✅ 3 Running")
    with col3:
        st.metric("Data Privacy", "✅ Local-First Design")

# Footer
st.divider()
st.markdown("""
---
**POC Information:**
- **Architecture:** Three-layer distributed AI system
- **Data Privacy:** Personal contributions tracked locally, aggregated for group/instructor views
- **Models:** Granite 4.0 Nano (Personal), Qwen2.5-Coder (Group), gpt-oss-20b (Instructor)
- **Framework:** LangChain for agentic orchestration
- **Status:** Proof of Concept (Template-based nudges, simulated data)

**Next Steps for Production:**
1. Integrate actual edge model inference via Ollama/llama.cpp
2. Implement persistent data storage with privacy compliance (FERPA/GDPR)
3. Add real-time collaboration features
4. Deploy CrewAI for multi-agent coordination
5. Add fine-tuning for institution-specific workflows
""")
