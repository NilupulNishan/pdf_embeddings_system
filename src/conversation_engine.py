"""
Conversational query engine.

Wraps SmartRetriever with chat memory so the system
can understand follow-up questions using previous context.
"""

import logging
from src.retriever import SmartRetriever
from src.chat_memory import ChatMemoryManager

logger = logging.getLogger(__name__)


class ConversationEngine:
    """
    Handles conversational RAG queries.

    Combines:
    - Chat memory
    - SmartRetriever
    - Query formatting
    """

    def __init__(self, collection_name: str, max_turns: int = 5):
        """
        Initialize conversation engine.

        Args:
            collection_name: Chroma collection to query
            max_turns: number of conversation turns to remember
        """
        self.collection_name = collection_name
        self.retriever = SmartRetriever(collection_name)
        self.memory = ChatMemoryManager(max_turns=max_turns)

        logger.info(f"ConversationEngine initialized for collection: {collection_name}")

    def chat(self, query: str):
        """
        Process conversational query.

        Args:
            query: User question

        Returns:
            QueryResponse object
        """

        # Get previous conversation
        context = self.memory.get_context()

        # Build conversational query
        if context:
            full_query = f"""
Previous conversation:
{context}

Current question:
{query}
"""
        else:
            full_query = query

        # Query retriever
        response = self.retriever.query(full_query)

        # Store messages if successful
        if response.retrieval_successful:
            self.memory.add_user_message(query)
            self.memory.add_assistant_message(response.answer)

        return response

    def reset(self):
        """
        Reset conversation history.
        """
        self.memory.clear()
        logger.info("Conversation memory cleared")

    def get_history(self):
        """
        Return conversation history.
        """
        return self.memory.get_history()