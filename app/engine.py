import logging
from typing import Any, Callable, Dict, List, Optional, Union

# Simple state type
State = Dict[str, Any]

# Node function signature: takes State, returns partial update to State
NodeFunction = Callable[[State], State]

# Edge condition: takes State, returns True if this edge should be followed
ConditionFunction = Callable[[State], bool]

class Node:
    def __init__(self, name: str, func: NodeFunction):
        self.name = name
        self.func = func

class Graph:
    def __init__(self):
        self.nodes: Dict[str, Node] = {}
        self.edges: Dict[str, List[tuple[str, Optional[ConditionFunction]]]] = {}
        self.start_node: Optional[str] = None

    def add_node(self, name: str, func: NodeFunction, is_start: bool = False):
        self.nodes[name] = Node(name, func)
        if is_start:
            self.start_node = name
        # Initialize edges list for this node
        if name not in self.edges:
            self.edges[name] = []

    def add_edge(self, from_node: str, to_node: str, condition: Optional[ConditionFunction] = None):
        if from_node not in self.nodes:
            raise ValueError(f"Node {from_node} not found")
        if to_node not in self.nodes:
            raise ValueError(f"Node {to_node} not found")
        
        self.edges[from_node].append((to_node, condition))

    def run(self, initial_state: State) -> Dict[str, Any]:
        if not self.start_node:
            raise ValueError("Graph has no start node")

        current_node_name = self.start_node
        state = initial_state.copy()
        steps = []
        
        # Safety limit for loops
        max_steps = 100
        step_count = 0

        while current_node_name and step_count < max_steps:
            node = self.nodes[current_node_name]
            
            # Execute node
            try:
                update = node.func(state)
                if update:
                    state.update(update)
                steps.append({"node": current_node_name, "state_snapshot": state.copy()})
            except Exception as e:
                logging.error(f"Error in node {current_node_name}: {e}")
                raise e

            step_count += 1
            
            # Find next node
            next_node_name = None
            possible_edges = self.edges.get(current_node_name, [])
            
            for target, condition in possible_edges:
                if condition is None:
                    # Unconditional edge matches
                    next_node_name = target
                    break
                elif condition(state):
                    # Conditional edge matches
                    next_node_name = target
                    break
            
            current_node_name = next_node_name

        return {"final_state": state, "steps": steps}
