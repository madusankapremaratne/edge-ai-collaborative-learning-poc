# 🤖 Distributed Edge-AI Agents for Collaborative Learning - POC

**A Multi-Agent Framework for Equitable Group Work in Project-Based Education**

## 📋 Overview

This POC demonstrates a three-layer distributed AI system designed to solve classic problems in student group work:
- One or two students doing all the work
- Poor communication and conflicts
- Instructor inability to see what's really happening inside groups

### Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    INSTRUCTOR DASHBOARD                          │
│              (High-level Supervisory View)                       │
│         Runs on Instructor Device (or Server)                    │
└─────────────────────────────────────────────────────────────────┘
                              ↓
        ┌─────────────────────────────────────────┐
        │      GROUP AI FACILITATORS (3)           │
        │   Team-level Coordination & Analytics    │
        │        Runs on Server/Cloud              │
        └─────────────────────────────────────────┘
                  ↓              ↓              ↓
    ┌──────────────┐   ┌──────────────┐   ┌──────────────┐
    │ GROUP A      │   │ GROUP B      │   │ GROUP C      │
    │ AI Assistant │   │ AI Assistant │   │ AI Assistant │
    │ (4 devices)  │   │ (4 devices)  │   │ (4 devices)  │
    └──────────────┘   └──────────────┘   └──────────────┘
    (Runs on Each Student Device - Edge)
```

### Three Agent Types

| Agent | Level | Runs On | Purpose | Model |
|-------|-------|---------|---------|-------|
| **Personal AI Assistant** | Individual | Student Device (Edge) | Tracks personal contributions, provides nudges | Granite 4.0 Nano (350M) |
| **Group AI Facilitator** | Team | Server/Cloud | Analyzes team dynamics, detects imbalances | Qwen2.5-Coder (7B) |
| **Instructor Dashboard** | Institutional | Instructor Device | High-level alerts, minimal noise | gpt-oss-20b (20B) |

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- pip

### Installation

```bash
# Clone or navigate to project directory
cd edge-ai-collaborative-learning

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Run the POC

```bash
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`

## 📊 POC Features

### Dashboard Overview 🎯
- System-wide statistics
- Group health summary with color-coded status
- Participation distribution across all students

### Student Assistant 👤
- **Select your profile** from any student in the course
- **Personal dashboard** showing your contributions
- **AI-generated nudges** (template-based)
  - Inactivity detection
  - Communication suggestions
  - Workload balance alerts
  - Positive reinforcement
  - Deadline reminders
- **Contribution history** with detailed activity log

### Group Facilitator 👥
- **Participation balance analysis** with visualization
- **Group health analysis** detecting:
  - High participation imbalance
  - Inactive team members
  - Overdue milestones
  - Urgent communications
- **Milestone tracking** with status updates
- **Communication insights** from team messages

### Instructor Dashboard 📊
- **Course overview** metrics
- **AI-generated alerts** (only when necessary)
  - Critical participation issues
  - Missed deadlines
  - Communication problems
- **Group status matrix** showing health and issues
- **Intervention recommendations** for at-risk groups
- **System health** monitoring

## 📁 Project Structure

```
.
├── app.py                    # Main Streamlit application
├── sample_data.py           # Simulated course data (3 groups, 12 students)
├── agentic_system.py        # Three agent implementations
├── requirements.txt         # Python dependencies
└── README.md               # This file
```

## 🔬 Sample Dataset

The POC includes realistic simulated data:

### Groups (3)
1. **Group A (Web Development)** - Status: At Risk ⚠️
   - Alice (7 hrs), Bob (10 hrs), Charlie (2 hrs), Diana (0 hrs)
   - Imbalance detected: Alice & Bob doing most work
   
2. **Group B (Data Analytics)** - Status: Healthy 🟡
   - Eve, Frank, Grace, Henry (balanced ~6-7 hrs each)
   - Good communication, healthy participation
   
3. **Group C (Mobile App)** - Status: Thriving 🟢
   - Iris, Jack, Kate, Liam (all contributing ~7-8 hrs)
   - Excellent collaboration and communication

### Data Types
- **Contributions**: 40+ logged activities with timestamps, tasks, durations
- **Communications**: Team messages with tone analysis
- **Milestones**: Project phases with status tracking
- **Timeseries**: Last 2 weeks of activity

## 🤖 Edge-Based LLM Models Recommended

### For Production Deployment

| Use Case | Model | Size | Performance | Edge-Ready |
|----------|-------|------|-------------|-----------|
| Personal AI | Granite 4.0 Nano | 350M-1B | Strong agent tasks | ✅ Excellent |
| Group Facilitator | Qwen2.5-Coder | 7B | 91% HumanEval | ✅ Good |
| Instructor Agent | gpt-oss-20b | 20B | 85% MMLU | ✅ Good |

### Deployment Options

**Local/Edge Deployment:**
```bash
# Using Ollama (simplest)
ollama run granite4-nano
ollama run qwen2.5-coder-7b

# Using llama.cpp (optimized)
./llama-cli --model granite4-nano.gguf
```

**Framework:**
- **LangChain** or **CrewAI** for agentic orchestration
- **Ollama** or **vLLM** for inference server
- **LiteLLM** for unified API across models

## 🔄 POC vs Production

### Current POC (Template-Based)
- ✅ Demonstrates three-layer architecture
- ✅ Shows all features at basic level
- ✅ Uses realistic simulated data
- ⏳ Nudges are template-based
- ⏳ No actual LLM inference (for speed)

### Production Implementation
- 🔜 Integrate Granite 4.0 Nano via Ollama
- 🔜 Implement CrewAI for multi-agent coordination
- 🔜 Add persistent storage (PostgreSQL)
- 🔜 Implement real-time collaboration features
- 🔜 Add FERPA/GDPR compliance layer
- 🔜 Fine-tune models for institutional context
- 🔜 Deploy personal agents on student devices
- 🔜 Implement end-to-end encryption for privacy

## 🛠️ Customization

### Add Your Own Data

Edit `sample_data.py`:
```python
GROUPS = {
    "Group_YOUR_NAME": {
        "name": "Your Group Name",
        "project": "Your Project",
        "students": ["Student1", "Student2", ...],
        "deadline": "2024-12-20",
        "status": "Healthy"
    },
    ...
}
```

### Customize Nudges

Edit `agentic_system.py` > `PersonalAIAssistant.nudge_templates`:
```python
self.nudge_templates = {
    "your_nudge_type": {
        "icon": "🎯",
        "title": "Your Title",
        "message": "Your message with {variables}",
        "action": "Your suggested action"
    }
}
```

### Adjust Detection Thresholds

In `agentic_system.py`:
```python
self.imbalance_threshold = 0.6  # Flag if >60% from one person
self.alert_threshold = 0.5      # Alert if >50% inactive
```

## 🎓 Educational Value

This POC demonstrates:
1. **Multi-Agent Systems**: How different AI agents at different scopes coordinate
2. **Privacy-by-Design**: Data aggregation from personal → team → institutional
3. **Edge AI**: Running inference on constrained devices
4. **Agentic Frameworks**: LangChain/CrewAI patterns
5. **Human-Centered AI**: Nudges vs mandates; alerts vs micromanagement

## 📈 Metrics Tracked

### Personal Level
- Contribution hours per task
- Activity frequency
- Communication patterns
- Deadline adherence

### Group Level
- Participation balance
- Task distribution
- Milestone progress
- Team communication health

### Institutional Level
- Group health status
- At-risk identification
- Overall participation rate
- Intervention needs

## 🔐 Privacy Considerations

The architecture ensures privacy through:
1. **Local First**: Personal AI runs on student device
2. **Aggregation**: Only aggregated metrics shared upward
3. **Selective Exposure**: Instructor sees trends, not raw conversations
4. **Opt-in Transparency**: Students see what's being tracked
5. **Data Minimization**: Only necessary data retained

## 🚦 Next Steps to Production

1. **Phase 1: Model Integration**
   - [ ] Set up Ollama with Granite 4.0 Nano
   - [ ] Test inference latency on target devices
   - [ ] Implement LangChain agent loop

2. **Phase 2: Real Data**
   - [ ] Connect to LMS (Canvas, Blackboard, Moodle)
   - [ ] Integrate real-time activity feeds
   - [ ] Set up persistent data storage

3. **Phase 3: Multi-Agent Coordination**
   - [ ] Implement CrewAI for agent cooperation
   - [ ] Add agent memory and state management
   - [ ] Test multi-group scenarios

4. **Phase 4: Deployment & Compliance**
   - [ ] Implement FERPA compliance layer
   - [ ] Deploy personal agents to student devices
   - [ ] Security audit and penetration testing

5. **Phase 5: Refinement**
   - [ ] Institution-specific fine-tuning
   - [ ] User feedback collection
   - [ ] Performance optimization

## 📚 Resources

### Open-Source Models
- [Granite Models (IBM)](https://github.com/ibm-granite)
- [Qwen Models (Alibaba)](https://github.com/QwenLM)
- [Mistral Models](https://huggingface.co/mistralai)

### Agentic Frameworks
- [LangChain](https://python.langchain.com/)
- [CrewAI](https://crewai.com/)
- [Ollama](https://ollama.ai/)

### Deployment
- [vLLM](https://vllm.ai/) - Fast LLM inference
- [llama.cpp](https://github.com/ggerganov/llama.cpp) - Optimized inference
- [MLX](https://github.com/ml-explore/mlx) - Apple Silicon optimization

## 📞 Support

For questions or issues:
1. Check the sample data format in `sample_data.py`
2. Review agent logic in `agentic_system.py`
3. Ensure all dependencies are installed: `pip install -r requirements.txt`

## 📄 License

This POC is provided as-is for educational and research purposes.

---

**Built for:** Educational Technology Innovation
**Status:** Proof of Concept (Template-Based)
**Last Updated:** November 2025
