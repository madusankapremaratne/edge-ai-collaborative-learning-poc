"""
LLM Integration for Edge AI Collaborative Learning Platform
Supports multiple LLM providers: Ollama, OpenAI, Hugging Face
"""

import logging
from typing import Optional, Dict, Any, List
from abc import ABC, abstractmethod
import requests
import json
from datetime import datetime

from config import config

logger = logging.getLogger(__name__)


class LLMProvider(ABC):
    """Abstract base class for LLM providers"""

    @abstractmethod
    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_tokens: int = 500,
        temperature: float = 0.7,
        **kwargs
    ) -> str:
        """Generate text from prompt"""
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """Check if LLM provider is available"""
        pass


class OllamaProvider(LLMProvider):
    """Ollama local LLM provider"""

    def __init__(self, base_url: str, model: str, timeout: int = 120):
        self.base_url = base_url.rstrip('/')
        self.model = model
        self.timeout = timeout

    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_tokens: int = 500,
        temperature: float = 0.7,
        **kwargs
    ) -> str:
        """Generate text using Ollama"""
        try:
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})

            payload = {
                "model": self.model,
                "messages": messages,
                "stream": False,
                "options": {
                    "temperature": temperature,
                    "num_predict": max_tokens,
                }
            }

            response = requests.post(
                f"{self.base_url}/api/chat",
                json=payload,
                timeout=self.timeout
            )
            response.raise_for_status()

            result = response.json()
            return result.get("message", {}).get("content", "")

        except requests.exceptions.RequestException as e:
            logger.error(f"Ollama API error: {e}")
            raise RuntimeError(f"Ollama API error: {e}")
        except Exception as e:
            logger.error(f"Unexpected error in Ollama provider: {e}")
            raise

    def is_available(self) -> bool:
        """Check if Ollama is running"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            return response.status_code == 200
        except:
            return False


class OpenAIProvider(LLMProvider):
    """OpenAI API provider (also compatible with OpenAI-like APIs)"""

    def __init__(self, api_key: str, model: str, base_url: str):
        self.api_key = api_key
        self.model = model
        self.base_url = base_url.rstrip('/')

    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_tokens: int = 500,
        temperature: float = 0.7,
        **kwargs
    ) -> str:
        """Generate text using OpenAI API"""
        try:
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})

            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }

            payload = {
                "model": self.model,
                "messages": messages,
                "max_tokens": max_tokens,
                "temperature": temperature,
            }

            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload,
                timeout=60
            )
            response.raise_for_status()

            result = response.json()
            return result["choices"][0]["message"]["content"]

        except requests.exceptions.RequestException as e:
            logger.error(f"OpenAI API error: {e}")
            raise RuntimeError(f"OpenAI API error: {e}")
        except Exception as e:
            logger.error(f"Unexpected error in OpenAI provider: {e}")
            raise

    def is_available(self) -> bool:
        """Check if OpenAI API is configured"""
        return self.api_key is not None and len(self.api_key) > 0


class MockLLMProvider(LLMProvider):
    """Mock LLM provider for testing and development"""

    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_tokens: int = 500,
        temperature: float = 0.7,
        **kwargs
    ) -> str:
        """Generate mock response based on prompt keywords"""
        prompt_lower = prompt.lower()

        # Nudge generation
        if "nudge" in prompt_lower or "suggestion" in prompt_lower:
            if "inactive" in prompt_lower:
                return "It looks like you haven't contributed to your group project in a few days. Consider checking in with your team and seeing how you can help move the project forward."
            elif "workload" in prompt_lower:
                return "Your contribution level is lower than your teammates. Try to balance the workload by taking on additional tasks or helping with existing ones."
            elif "deadline" in prompt_lower:
                return "Don't forget about the upcoming milestone deadline! Make sure you're on track to complete your assigned tasks."
            else:
                return "Great work on your recent contributions! Keep up the collaborative effort with your team."

        # Group analysis
        elif "group" in prompt_lower or "team" in prompt_lower:
            if "imbalance" in prompt_lower:
                return "The workload appears to be unevenly distributed. Consider redistributing tasks to ensure all team members are contributing equally."
            elif "health" in prompt_lower:
                return "The team is showing signs of communication issues. Schedule a team meeting to address concerns and realign on project goals."
            else:
                return "The team is functioning well with balanced participation and good communication."

        # Instructor recommendations
        elif "instructor" in prompt_lower or "intervention" in prompt_lower:
            if "alert" in prompt_lower:
                return "Group Alpha requires immediate attention due to significant participation imbalance and overdue milestones. Consider scheduling a check-in meeting."
            else:
                return "Overall course engagement is healthy. Monitor Group Alpha for potential intervention needs."

        return "AI-generated insight based on current data and patterns."

    def is_available(self) -> bool:
        """Mock provider is always available"""
        return True


class LLMService:
    """Main LLM service that manages different providers"""

    def __init__(self):
        self.provider = self._initialize_provider()
        logger.info(f"LLM Service initialized with provider: {type(self.provider).__name__}")

    def _initialize_provider(self) -> LLMProvider:
        """Initialize the appropriate LLM provider based on configuration"""

        # If mock mode is enabled, use mock provider
        if config.MOCK_LLM_RESPONSES:
            logger.info("Using Mock LLM Provider (MOCK_LLM_RESPONSES=true)")
            return MockLLMProvider()

        # Try to initialize based on configured provider
        if config.LLM_PROVIDER == "ollama":
            provider = OllamaProvider(
                base_url=config.OLLAMA_BASE_URL,
                model=config.OLLAMA_MODEL,
                timeout=config.OLLAMA_TIMEOUT
            )
            if provider.is_available():
                return provider
            else:
                logger.warning("Ollama is not available, falling back to Mock provider")
                return MockLLMProvider()

        elif config.LLM_PROVIDER == "openai":
            if config.OPENAI_API_KEY:
                return OpenAIProvider(
                    api_key=config.OPENAI_API_KEY,
                    model=config.OPENAI_MODEL,
                    base_url=config.OPENAI_BASE_URL
                )
            else:
                logger.warning("OpenAI API key not configured, falling back to Mock provider")
                return MockLLMProvider()

        else:
            logger.warning(f"Unknown LLM provider: {config.LLM_PROVIDER}, using Mock provider")
            return MockLLMProvider()

    def generate_nudge(
        self,
        student_name: str,
        contribution_data: Dict[str, Any],
        nudge_type: str,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """Generate a personalized nudge for a student"""

        # Build context-aware prompt
        prompt = f"""Generate a friendly, encouraging nudge for a student in a collaborative learning environment.

Student: {student_name}
Nudge Type: {nudge_type}

Current Contribution Data:
- Total Hours: {contribution_data.get('total_hours', 0)}
- Tasks Completed: {contribution_data.get('tasks_completed', 0)}
- Last Activity: {contribution_data.get('last_activity', 'N/A')}

"""
        if context:
            prompt += f"\nAdditional Context:\n"
            for key, value in context.items():
                prompt += f"- {key}: {value}\n"

        prompt += """
Generate a short, personalized message (2-3 sentences) that:
1. Is supportive and encouraging, not critical
2. Provides actionable suggestions
3. Maintains student privacy and dignity
4. Uses a friendly, conversational tone
"""

        system_prompt = "You are a helpful AI learning assistant for collaborative education. Your role is to encourage student engagement and teamwork in a positive, supportive manner."

        try:
            response = self.provider.generate(
                prompt=prompt,
                system_prompt=system_prompt,
                max_tokens=150,
                temperature=0.7
            )
            return response.strip()
        except Exception as e:
            logger.error(f"Error generating nudge: {e}")
            # Fallback to template-based nudge
            return self._fallback_nudge(nudge_type, student_name)

    def analyze_group_health(
        self,
        group_name: str,
        participation_data: Dict[str, float],
        issues: List[str]
    ) -> Dict[str, Any]:
        """Analyze group health and provide recommendations"""

        prompt = f"""Analyze the health of a collaborative learning group and provide recommendations.

Group: {group_name}

Participation Distribution:
"""
        for student, hours in participation_data.items():
            prompt += f"- {student}: {hours} hours\n"

        if issues:
            prompt += f"\nDetected Issues:\n"
            for issue in issues:
                prompt += f"- {issue}\n"

        prompt += """
Provide:
1. Overall health assessment (1-2 sentences)
2. Top 3 specific recommendations for improvement
3. Suggested action items for the team

Format as JSON with keys: assessment, recommendations (list), action_items (list)
"""

        system_prompt = "You are an AI facilitator for collaborative learning groups. Your role is to identify issues and suggest constructive interventions."

        try:
            response = self.provider.generate(
                prompt=prompt,
                system_prompt=system_prompt,
                max_tokens=400,
                temperature=0.6
            )

            # Try to parse as JSON, otherwise return structured response
            try:
                return json.loads(response)
            except json.JSONDecodeError:
                return {
                    "assessment": response[:200],
                    "recommendations": ["Review participation balance", "Improve communication", "Realign task distribution"],
                    "action_items": ["Schedule team meeting", "Redistribute tasks", "Set clear milestones"]
                }
        except Exception as e:
            logger.error(f"Error analyzing group health: {e}")
            return self._fallback_group_analysis(issues)

    def generate_instructor_alert(
        self,
        group_name: str,
        issues: List[str],
        metrics: Dict[str, Any]
    ) -> str:
        """Generate an alert message for instructors"""

        prompt = f"""Generate a concise alert for an instructor about a collaborative learning group that needs attention.

Group: {group_name}

Issues Detected:
"""
        for issue in issues:
            prompt += f"- {issue}\n"

        prompt += f"\nKey Metrics:\n"
        for key, value in metrics.items():
            prompt += f"- {key}: {value}\n"

        prompt += """
Generate a brief alert (3-4 sentences) that:
1. Summarizes the critical issues
2. Explains potential impact on learning outcomes
3. Suggests immediate intervention steps
"""

        system_prompt = "You are an AI dashboard for instructors managing multiple collaborative learning groups. Focus on actionable insights."

        try:
            response = self.provider.generate(
                prompt=prompt,
                system_prompt=system_prompt,
                max_tokens=200,
                temperature=0.6
            )
            return response.strip()
        except Exception as e:
            logger.error(f"Error generating instructor alert: {e}")
            return f"Group {group_name} requires attention due to: {', '.join(issues[:2])}"

    def _fallback_nudge(self, nudge_type: str, student_name: str) -> str:
        """Fallback template-based nudge when LLM fails"""
        templates = {
            "inactivity": f"Hi {student_name}! We noticed you haven't contributed in a few days. Your team would love to hear from you!",
            "workload": f"Hey {student_name}, looks like you might have some extra capacity. Your teammates could use your help!",
            "deadline": f"Reminder: Your team has an upcoming deadline. Make sure you're on track!",
            "positive": f"Great work, {student_name}! Your contributions are making a real difference.",
            "communication": f"Don't forget to check in with your team regularly. Communication is key!"
        }
        return templates.get(nudge_type, f"Keep up the great work, {student_name}!")

    def _fallback_group_analysis(self, issues: List[str]) -> Dict[str, Any]:
        """Fallback group analysis when LLM fails"""
        return {
            "assessment": "The group shows signs of imbalance that require attention.",
            "recommendations": [
                "Redistribute workload among team members",
                "Improve team communication patterns",
                "Set clear expectations and deadlines"
            ],
            "action_items": [
                "Schedule a team synchronization meeting",
                "Review and reassign tasks",
                "Establish regular check-in schedule"
            ]
        }

    def is_healthy(self) -> bool:
        """Check if LLM service is functioning"""
        return self.provider.is_available()


# Singleton instance
llm_service = LLMService()
