"""
Chat Memory Manager for conversational RAG queries.

This module stores recent conversation history and formats it
so it can be passed to the LLM along with the current query.
"""

from typing import List, Dict


class ChatMemoryManager:
    """
    Manages conversation history for contextual queries.

    Features
    --------
    - Stores user and assistant messages
    - Limits memory to last N conversation turns
    - Formats history into LLM-friendly context
    - Allows clearing memory for new sessions
    """

    def __init__(self, max_turns: int = 5):
        """
        Initialize memory manager.

        Args:
            max_turns: Number of previous Q&A pairs to keep
        """
        self.max_turns = max_turns
        self.history: List[Dict[str, str]] = []

    def add_user_message(self, message: str):
        """
        Store user message.

        Args:
            message: User question
        """
        self.history.append({
            "role": "user",
            "content": message
        })

    def add_assistant_message(self, message: str):
        """
        Store assistant response.

        Args:
            message: LLM response
        """
        self.history.append({
            "role": "assistant",
            "content": message
        })

    def get_context(self) -> str:
        """
        Convert recent conversation history into a context string.

        Returns:
            Formatted conversation history
        """
        if not self.history:
            return ""

        # Keep only last N conversation turns
        recent_history = self.history[-self.max_turns * 2:]

        context_lines = []

        for msg in recent_history:
            role = msg["role"]
            content = msg["content"]

            if role == "user":
                context_lines.append(f"User: {content}")
            else:
                context_lines.append(f"Assistant: {content}")

        return "\n".join(context_lines)

    def clear(self):
        """
        Reset conversation history.
        """
        self.history = []

    def get_history(self) -> List[Dict[str, str]]:
        """
        Return full conversation history.

        Returns:
            List of message dictionaries
        """
        return self.history