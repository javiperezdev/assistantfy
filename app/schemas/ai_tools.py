from abc import ABC, abstractmethod
from typing import Any, Dict, Type, Optional
from pydantic import BaseModel

class BaseTool(ABC):
    """
    Defines the schema for every single tool.
    To make sure every tool has name, description and pydantic args_schema
    """
    name: str
    description: str
    args_schema: Type[BaseModel]

    @abstractmethod
    async def run(self, context: Any, **kwargs) -> Any:
        """
        Runs the tool, with the injected context and AI context in the kwargs.
        """
        pass

    def get_tool_definition(self) -> Dict[str, Any]:
        """
        Gives the LLM the structure it needs"
        """
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.args_schema.model_json_schema(),
            },
        }

# In memory tool registry
_TOOL_REGISTRY: Dict[str, BaseTool] = {}

def register_tool(tool_instance: BaseTool):
    """Register a tool in the in memory tool registry"""
    _TOOL_REGISTRY[tool_instance.name] = tool_instance

def get_tool(name: str) -> Optional[BaseTool]:
    """Get a tool by it name"""
    return _TOOL_REGISTRY.get(name)

def get_all_tool_definitions() -> list[Dict[str, Any]]:
    """Returns the definitio of every tool"""
    return [tool.get_tool_definition() for tool in _TOOL_REGISTRY.values()]
