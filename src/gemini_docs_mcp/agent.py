"""Agent module for querying documentation using CrewAI and Gemini via OpenRouter."""

import os

from crewai import LLM, Agent, Crew, Task


async def query_docs(doc_content: str, prompt: str) -> str:
    """Query documentation content using a CrewAI agent.

    Args:
        doc_content: The full document content to analyze.
        prompt: The user's question or prompt about the document.

    Returns:
        The agent's response as a string.
    """
    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        raise ValueError("OPENROUTER_API_KEY environment variable is not set")

    llm = LLM(
        model="openrouter/x-ai/grok-4.1-fast",
        api_key=api_key,
        streaming=False,
    )

    agent = Agent(
        role="Documentation Expert",
        goal="Answer questions accurately based on the provided documentation content",
        backstory=(
            "You are an expert at reading and understanding technical documentation. "
            "You provide clear, accurate, and helpful answers based solely on the "
            "documentation content provided to you."
        ),
        llm=llm,
        verbose=False,
    )

    task = Task(
        description=f"""Based on the following documentation content, answer this question:

{prompt}

Documentation content:
{doc_content}""",
        expected_output="A clear and accurate answer to the question based on the documentation.",
        agent=agent,
    )

    crew = Crew(
        agents=[agent],
        tasks=[task],
        verbose=False,
    )

    result = await crew.kickoff_async()
    print(f"[DEBUG] CrewAI result type: {type(result)}, value: {result}")
    return str(result)
