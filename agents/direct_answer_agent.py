from agents.base import BaseAgent

class DirectAnswerAgent(BaseAgent):
    def run(self, prompt, history=None):
        history = history or []
        history_str = "\n".join([f"{m.get('sender', 'unknown')}: {m.get('message', '')}" for m in history])

        full_prompt = f"""You are a helpful and friendly AI assistant specialized in data-related tasks. Your personality is professional yet approachable.

Analyze the user's prompt and the conversation history to provide a direct, concise, and conversational answer.

**Instructions:**
- Do not attempt to write or modify SQL.
- If the question is about your identity, explain that you are an AI assistant for data tasks.
- If the question is outside of your scope (e.g., about the weather, politics, etc.), politely decline to answer.
- Keep your answers short and to the point.

**Conversation History:**
{history_str}

**User Prompt:** {prompt}

**Your Answer:**"""

        response = self.model.generate_content(full_prompt)
        return response.parts[0].text.strip()
