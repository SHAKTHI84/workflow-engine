# Simple Workflow Engine

A lightweight, Python-based workflow engine built with FastAPI. This system allows you to define, execute, and monitor stateful processing graphs where nodes are Python functions and edges define the execution flow (including loops and conditionals).

## Features
- **Graph Engine**: Supports `Node` (function) and `Edge` (transition) definitions.
- **State Management**: Shared dictionary state flows between nodes.
- **Branching & Looping**: Supports conditional edges for complex logic.
- **Tool Registry**: Simple decorator-based system (`@registry.register`) to make Python functions available to the engine.
- **REST API**: FastAPI endpoints to create graphs and run workflows.

## Project Structure
```
workflow-engine/
├── app/
│   ├── workflows/
│   │   └── code_review.py  # Sample "Code Review" agent implementation
│   ├── engine.py           # Core graph execution logic
│   ├── main.py             # FastAPI entrypoint and API routes
│   └── registry.py         # Tool registration system
├── requirements.txt
└── test.py                 # Verification script
```

## How to Run

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Start the Server**
   ```bash
   python -m uvicorn app.main:app --reload
   ```
   The API will be available at `http://127.0.0.1:8000`.

3. **Explore the API**
   Open `http://127.0.0.1:8000/docs` to see the Swagger UI.

## Sample Workflow: Code Review Agent
A pre-loaded sample workflow is available (ID: `sample-code-review`). It simulates a code review process:
1. **Extract Functions**: Parses code.
2. **Check Complexity**: Calculates a score.
3. **Detect Issues**: Finds bad practices (e.g., `print` statements).
4. **Suggest Improvements**: Simulates fixing the code.
5. **Loop**: Repeats until quality score >= 80.

**Run it via curl:**
```bash
curl -X POST "http://127.0.0.1:8000/graph/run" \
     -H "Content-Type: application/json" \
     -d '{"graph_id": "sample-code-review", "initial_state": {"code": "def foo(): pass", "target_quality": 90}}'
```

## Future Improvements
- **Persistence**: functionality to save graphs/runs to a database (SQLite/PostgreSQL) instead of in-memory dictionaries.
- **Async Execution**: Support for `async/await` node functions for I/O bound tasks.
- **Visualizer**: A frontend to visualize the graph structure.
