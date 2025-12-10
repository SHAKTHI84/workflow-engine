import uuid
from typing import Dict, List, Optional, Any
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from app.engine import Graph, State, NodeFunction
from app.registry import registry
from app.workflows.code_review import create_code_review_graph

app = FastAPI(title="Workflow Engine")

# --- In-Memory Storage ---
graphs: Dict[str, Graph] = {}
runs: Dict[str, Dict[str, Any]] = {}

# --- Pydantic Models ---
class NodeModel(BaseModel):
    name: str
    tool: str # Function name in registry
    is_start: bool = False

class EdgeModel(BaseModel):
    from_node: str
    to_node: str
    condition: Optional[str] = None # Name of condition function (optional simple support)

class GraphCreateRequest(BaseModel):
    nodes: List[NodeModel]
    edges: List[EdgeModel]

class RunRequest(BaseModel):
    graph_id: str
    initial_state: Dict[str, Any]

# --- Pre-load Sample Graph ---
sample_graph_id = "sample-code-review"
graphs[sample_graph_id] = create_code_review_graph()

# --- Endpoints ---

@app.get("/")
def read_root():
    return {"message": "Workflow Engine is running. Use /docs for API."}

@app.post("/graph/create")
def create_graph(request: GraphCreateRequest):
    graph = Graph()
    graph_id = str(uuid.uuid4())
    
    try:
        # Add Nodes
        for node_data in request.nodes:
            tool_func = registry.get_tool(node_data.tool)
            if not tool_func:
                raise HTTPException(status_code=400, detail=f"Tool '{node_data.tool}' not found in registry.")
            graph.add_node(node_data.name, tool_func, is_start=node_data.is_start)
            
        # Add Edges
        for edge_data in request.edges:
            # Condition support is basic: registry lookup currently only stores tools (state->state).
            # We could extend registry to store conditions (state->bool), but for MVP we might skip custom conditions via JSON
            # unless we add them to registry too.
            # For this simple assignment, we assume JSON edges are unconditional OR use a special conditional logic string if needed.
            # Given spec "Simple mapping like {'extract': 'analyze'} is enough", we'll stick to unconditional for user-created graphs.
            # (The sample graph handles its own conditional logic in python code).
            
            graph.add_edge(edge_data.from_node, edge_data.to_node)
            
        graphs[graph_id] = graph
        return {"graph_id": graph_id, "message": "Graph created successfully"}
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/graph/run")
def run_graph(request: RunRequest):
    graph_id = request.graph_id
    if graph_id not in graphs:
        raise HTTPException(status_code=404, detail="Graph not found")
    
    run_id = str(uuid.uuid4())
    graph = graphs[graph_id]
    
    try:
        result = graph.run(request.initial_state)
        runs[run_id] = {
            "status": "completed",
            "final_state": result["final_state"],
            "execution_log": result["steps"]
        }
        return {
            "run_id": run_id, 
            "final_state": result["final_state"], 
            "execution_log": [step["node"] for step in result["steps"]] # simplified log
        }
    except Exception as e:
        runs[run_id] = {"status": "failed", "error": str(e)}
        raise HTTPException(status_code=500, detail=f"Execution failed: {str(e)}")

@app.get("/graph/state/{run_id}")
def get_run_state(run_id: str):
    if run_id not in runs:
        raise HTTPException(status_code=404, detail="Run not found")
    return runs[run_id]

@app.get("/tools")
def list_available_tools():
    return registry.list_tools()
