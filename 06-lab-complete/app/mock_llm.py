"""Deterministic local LLM substitute used by the deployment lab."""
import time


RESPONSES = {
    "docker": "Docker packages an application and its dependencies into a portable container.",
    "deploy": "Deployment makes an application available on infrastructure where users can access it.",
    "health": "All systems are operational.",
}


def ask(question: str, delay: float = 0.05) -> str:
    time.sleep(delay)
    lowered = question.lower()
    for keyword, response in RESPONSES.items():
        if keyword in lowered:
            return response
    return "The production AI agent received your question successfully."
