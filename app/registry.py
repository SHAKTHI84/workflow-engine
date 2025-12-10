from typing import Callable, Dict, Any

class ToolRegistry:
    def __init__(self):
        self._tools: Dict[str, Callable] = {}

    def register(self, name: str = None):
        def decorator(func):
            tool_name = name or func.__name__
            self._tools[tool_name] = func
            return func
        return decorator

    def get_tool(self, name: str) -> Callable:
        return self._tools.get(name)

    def list_tools(self) -> Dict[str, str]:
        return {name: func.__doc__ or "No description" for name, func in self._tools.items()}

# Global registry instance
registry = ToolRegistry()
