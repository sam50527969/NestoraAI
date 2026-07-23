from app.core.tools import tool_registry

print("Registered tools:", tool_registry.count())
print(tool_registry.list_tools())