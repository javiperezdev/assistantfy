from pydantic import BaseModel, Field
from typing import Callable, Dict, List, Type, Any
from datetime import date
import asyncio

class AsyncToolRegistry:
    def __init__(self):
        self._schemas: Dict[str, dict] = {}
        self._callables: Dict[str, Callable] = {}

    def register(self, name: str, schema_model: Type[BaseModel]):
        def decorator(func: Callable):
            description = (schema_model.__doc__ or func.__doc__ or "").strip()
            
            self._schemas[name] = {
                "type": "function",
                "function": {
                    "name": name,
                    "description": description,
                    "parameters": schema_model.model_json_schema()
                }
            }
            self._callables[name] = func
            return func
        return decorator

    @property
    def tools(self) -> List[dict]:
        return list(self._schemas.values())
    
    async def execute(self, name: str, **kwargs) -> Any:
        if name not in self._callables:
            raise ValueError(f"La herramienta {name} no está registrada.")
        
        func = self._callables[name]
        
        # This block of code is compulsory to work with async and not async functions
        if asyncio.iscoroutinefunction(func):
            return await func(**kwargs)
        else:
            return func(**kwargs)

ai_tools = AsyncToolRegistry()