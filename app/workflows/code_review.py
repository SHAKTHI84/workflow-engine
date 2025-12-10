import random
from app.engine import Graph, State
from app.registry import registry

# --- Tool/Node Functions ---

@registry.register()
def extract_functions(state: State) -> State:
    """Simulate extracting functions from code."""
    code = state.get("code", "")
    # Mock extraction
    functions = [line for line in code.split("\n") if line.strip().startswith("def ")]
    return {"functions": functions}

@registry.register()
def check_complexity(state: State) -> State:
    """Simulate complexity check."""
    functions = state.get("functions", [])
    # Mock complexity score: len of functions * random factor
    complexity_score = len(functions) * random.randint(1, 10)
    return {"complexity_score": complexity_score}

@registry.register()
def detect_issues(state: State) -> State:
    """Simulate issue detection."""
    code = state.get("code", "")
    issues = []
    if "print(" in code:
        issues.append("Avoid using print() in production.")
    if "import *" in code:
        issues.append("Avoid wildcard imports.")
    return {"issues": issues}

@registry.register()
def suggest_improvements(state: State) -> State:
    """Simulate suggestion generation and improvement."""
    current_quality = state.get("quality_score", 0)
    # Simulate improvement
    new_quality = current_quality + random.randint(10, 30)
    
    # Simulate modifying code (mock)
    code = state.get("code", "")
    state["iteration"] = state.get("iteration", 0) + 1
    
    return {"quality_score": new_quality, "review_summary": f"Improved code quality to {new_quality}"}

# --- Condition ---

def is_quality_sufficient(state: State) -> bool:
    target = state.get("target_quality", 80)
    current = state.get("quality_score", 0)
    iteration = state.get("iteration", 0)
    max_retries = state.get("max_retries", 3)
    
    if current >= target:
        return True # Go to end
    if iteration >= max_retries:
        return True # Stop anyway to prevent infinite loops in sample
    
    return False # Loop back

# --- Graph Construction ---

def create_code_review_graph() -> Graph:
    graph = Graph()
    
    # Add nodes
    graph.add_node("extract_functions", extract_functions, is_start=True)
    graph.add_node("check_complexity", check_complexity)
    graph.add_node("detect_issues", detect_issues)
    graph.add_node("suggest_improvements", suggest_improvements)
    
    # Define linear flow
    graph.add_edge("extract_functions", "check_complexity")
    graph.add_edge("check_complexity", "detect_issues")
    graph.add_edge("detect_issues", "suggest_improvements")
    
    # Define loop/branch
    # If quality is sufficient (or max retries), we stop (no edge = stop).
    # If not, we loop back to suggest_improvements (or could go back to check_complexity, let's say suggest_improvements refines and we check again?)
    # Let's make it: suggest_improvements -> (check if good) -> STOP or LOOP back to suggest_improvements
    
    # Actually, usually: Refine -> Check -> Decision.
    # Let's adjust slightly: suggest_improvements -> check_complexity (to re-evaluate).
    # But for simplicity of this specific sample request:
    # "5. Loop until “quality_score >= threshold”"
    
    # Let's say suggest_improvements updates the score directly (as implemented).
    # So from suggest_improvements, we check condition.
    # We need a dummy "end" or just stop. logic:
    # If !is_quality_sufficient -> suggest_improvements (Self loop? or simply loop).
    # My engine supports conditional edges.
    
    # Edge from suggest_improvements:
    # If NOT sufficient -> suggest_improvements (Loop)
    # If sufficient -> END (No edge)
    
    # Condition: Loop if quality < target AND iters < max
    def should_loop(state: State) -> bool:
        return not is_quality_sufficient(state)

    graph.add_edge("suggest_improvements", "suggest_improvements", condition=should_loop)
    
    return graph
