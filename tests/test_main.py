import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from pathlib import Path

# Ensures we import from the actual package structure
from ai_teaching_agent.main import (
    handler, 
    initialize_agent, 
    load_skill, 
    parallel_team_node,
    CourseState
)

# --- Fixtures ---

@pytest.fixture
def mock_messages():
    return [{"role": "user", "content": "Python for Data Science"}]

@pytest.fixture
def mock_llm_response():
    mock = MagicMock()
    mock.content = "Mocked Agent Content"
    return mock

# --- Tests ---

@pytest.mark.asyncio
async def test_handler_success_flow(mock_messages):
    """
    Verifies that the handler coordinates initialization and returns 
    the expected final output from the graph.
    """
    mock_result = {"final_output": "# Success\nCurriculum generated."}

    # Patching global state and the graph's ainvoke method
    with patch("ai_teaching_agent.main._initialized", True), \
         patch("ai_teaching_agent.main.graph") as mock_graph:
        
        mock_graph.ainvoke = AsyncMock(return_value=mock_result)
        
        result = await handler(mock_messages)
        
        assert "Success" in result
        mock_graph.ainvoke.assert_called_once_with({"topic": "Python for Data Science"})

@pytest.mark.asyncio
async def test_handler_empty_content_fallback():
    """
    Verifies the defensive logic handles empty or whitespace-only content.
    """
    messages = [{"role": "user", "content": "   "}]
    
    with patch("ai_teaching_agent.main._initialized", True), \
         patch("ai_teaching_agent.main.graph") as mock_graph:
        
        mock_graph.ainvoke = AsyncMock(return_value={"final_output": "Fallback result"})
        
        await handler(messages)
        # Should default to "General Learning" per the logic in run_agent
        mock_graph.ainvoke.assert_called_once_with({"topic": "General Learning"})

@pytest.mark.asyncio
async def test_parallel_team_exception_handling(mock_llm_response):
    """
    Tests the gather(return_exceptions=True) logic.
    Ensures one node failing doesn't crash the entire request.
    """
    state: CourseState = {"professor_content": "Knowledge base summary", "topic": "Test"}
    
    # Simulate: 1 success, 1 failure, 1 success
    side_effects = [
        mock_llm_response,
        Exception("LLM Timeout Error"),
        mock_llm_response
    ]

    with patch("ai_teaching_agent.main.global_llm") as mock_llm, \
         patch("ai_teaching_agent.main.load_skill", return_value="System Prompt"):
        
        mock_llm.ainvoke = AsyncMock(side_effect=side_effects)
        
        result = await parallel_team_node(state)
        
        # Verify specific keys extracted correctly vs error messages
        assert result["advisor_roadmap"] == "Mocked Agent Content"
        assert "⚠️ Error: LLM Timeout Error" in result["librarian_resources"]
        assert result["ta_workbook"] == "Mocked Agent Content"

@pytest.mark.asyncio
async def test_load_skill_regex_resilience():
    """
    Tests the regex logic against different line endings and whitespace.
    """
    mock_content = "## 🎓 Professor Agent\nThis is the prompt content.\n## 🗺️ Academic Advisor Agent"
    
    with patch("pathlib.Path.read_text", return_value=mock_content), \
         patch("pathlib.Path.exists", return_value=True):
        
        result = load_skill("🎓 Professor Agent")
        assert result == "This is the prompt content."

@pytest.mark.asyncio
async def test_initialization_lock_safety():
    """
    Verifies that multiple concurrent calls only trigger initialization once.
    """
    # Force _initialized to False for this test
    with patch("ai_teaching_agent.main._initialized", False), \
         patch("ai_teaching_agent.main.initialize_agent", new_callable=AsyncMock) as mock_init, \
         patch("ai_teaching_agent.main.run_agent", new_callable=AsyncMock) as mock_run:
        
        # Trigger two simultaneous handler calls
        await asyncio.gather(
            handler([{"role": "user", "content": "Topic A"}]),
            handler([{"role": "user", "content": "Topic B"}])
        )
        
        # initialize_agent should only ever be called ONCE
        mock_init.assert_called_once()
        assert mock_run.call_count == 2

@pytest.mark.asyncio
async def test_missing_api_key_runtime_error():
    """
    Ensures system fails fast if the API key is missing.
    """
    with patch("os.getenv", return_value=None), \
         patch("ai_teaching_agent.main._init_lock"):
        
        with pytest.raises(RuntimeError, match="OPENROUTER_API_KEY not found"):
            await initialize_agent()
            
@pytest.mark.asyncio
async def test_handler_llm_timeout_resilience():
    """
    Test 7: Timeout Handling
    Ensures the system handles a total timeout gracefully without 
    leaving the user with a blank screen.
    """
    with patch("ai_teaching_agent.main._initialized", True), \
         patch("ai_teaching_agent.main.graph") as mock_graph:
        
        # Simulate an asyncio timeout
        mock_graph.ainvoke = AsyncMock(side_effect=asyncio.TimeoutError("Request timed out"))
        
        result = await handler([{"role": "user", "content": "Slow Topic"}])
        assert "Error:" in result
        assert "timed out" in result.lower()

@pytest.mark.asyncio
async def test_compiler_handles_malformed_input():
    """
    Test 8: Markdown Integrity
    Ensures the compiler doesn't break if sub-agents provide empty strings 
    or malformed data.
    """
    from ai_teaching_agent.main import compiler_node
    
    # State with missing keys or empty strings
    state = {
        "topic": "Empty Test",
        "professor_content": "",
        "advisor_roadmap": "N/A",
        "librarian_resources": "",
        "ta_workbook": "None"
    }
    
    result = await compiler_node(state)
    output = result["final_output"]
    
    # Compiler should still produce the headers even if content is missing
    assert "# 🎓 AI Teaching Team: Empty Test" in output
    assert "## 🧠 Knowledge Base" in output
    