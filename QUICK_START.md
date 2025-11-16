# 🚀 Quick Start Guide

## Installation (2 minutes)

```bash
# 1. Navigate to project directory
cd edge-ai-collaborative-learning

# 2. Create Python environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt
```

## Run the POC (1 minute)

```bash
streamlit run app.py
```

Browser will open automatically at `http://localhost:8501`

## Explore the Four Views

### 1️⃣ Dashboard Overview 🎯
- See all 3 groups at a glance
- View total participation across 12 students
- Visualize hours contributed

### 2️⃣ Student Assistant 👤
- **Select any student** from dropdown (e.g., "Alice")
- See personalized dashboard with:
  - ✅ Your contribution hours
  - ✨ AI nudges (5 types of intelligent suggestions)
  - 📋 Full activity history

### 3️⃣ Group Facilitator 👥
- **Pick a group** (A, B, or C)
- Analyze team health:
  - 🔍 Participation balance chart
  - ⚠️ Group alerts (imbalances, inactive members)
  - 📅 Milestone tracking
  - 💬 Communication insights

### 4️⃣ Instructor Dashboard 📊
- **High-level view** of entire course
- 🚨 Only critical alerts shown (no noise)
- 💡 Actionable recommendations for each group
- 🔧 System health status

## Sample Data Highlights

**Group A (At Risk ⚠️)**
- Alice: 7 hours (working hard)
- Bob: 10 hours (overloaded)
- Charlie: 2 hours (minimal)
- Diana: 0 hours (inactive!)
→ Clear imbalance detected

**Group B (Healthy 🟡)**
- Eve, Frank, Grace, Henry: 6-7 hours each
- Well-balanced team
- Good communication

**Group C (Thriving 🟢)**
- All students: 7-8 hours
- Strong collaboration
- On-track with milestones

## 🤖 AI Features Demonstrated

### Personal AI Nudges (Student View)
1. **Inactivity Alert** - "You haven't contributed this week"
2. **Communication Tips** - "Try framing as a question"
3. **Workload Balance** - "You're doing less than average"
4. **Positive Reinforcement** - "Great progress!"
5. **Deadline Reminders** - "Milestone approaching"

### Group AI Analysis (Facilitator View)
- Detects participation >60% concentration
- Flags inactive team members
- Tracks milestone progress
- Analyzes communication tone

### Instructor AI Alerts (Dashboard View)
- Only alerts on critical issues (multiple problems)
- Provides recommended interventions
- Shows course-wide engagement patterns

## 📊 Key Metrics

Each view shows different metrics:
- **Personal**: Hours, tasks, activity dates
- **Group**: Total hours, participation %, imbalance %, inactive count
- **Instructor**: At-risk groups, alert count, recommendations

## 🎯 What This POC Shows

✅ Three-layer distributed AI architecture
✅ All features at basic level
✅ Realistic group dynamics
✅ Privacy-by-design (aggregation upward)
✅ Practical nudges (not intrusive)
✅ Template-based LLM preparation

## 🔜 Next: Edge LLM Integration

Once comfortable with POC:

```bash
# Install Ollama (https://ollama.ai/)
ollama run granite4-nano

# Update app.py to use real model:
# Replace template nudges with LangChain agent calls
```

## 🐛 Troubleshooting

**"ModuleNotFoundError: No module named 'streamlit'"**
→ Run: `pip install -r requirements.txt`

**"App not responding at localhost:8501"**
→ Wait 10-15 seconds for Streamlit to start
→ Check terminal for errors

**"Can't find sample_data.py"**
→ Ensure all files are in same directory
→ Run from project root: `streamlit run app.py`

## 💡 Tips

- Click on different groups to see different dynamics
- Try each student in Group A (Alice vs Diana) to see contrasting nudges
- Compare Group A alerts to Group C to see healthy vs at-risk patterns
- Switch between views to see how same data looks at different levels

## 📚 Key Files

| File | Purpose |
|------|---------|
| `app.py` | Main Streamlit interface (4 views) |
| `sample_data.py` | Simulated course data |
| `agentic_system.py` | Three agent implementations |
| `requirements.txt` | Python dependencies |
| `README.md` | Full documentation |

Enjoy exploring the POC! 🎉
