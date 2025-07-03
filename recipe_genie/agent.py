from langgraph.graph import StateGraph, START, END
from .utils.state import State
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

from .utils.nodes import greet_user, decide_action, run_find_recipe, run_recipe_details, run_nutrition_analysis, truncate_messages

def route_tool(state: State) -> str:
    # Your logic to decide the next tool node
    if state.get("ingredients"):
        return "find_recipe"
    elif state.get("query", "").lower().startswith("how to make"):
        return "recipe_details"
    elif state.get("query", "").lower().startswith("analyze") or "nutrition" in state.get("query", "").lower():
        return "analyze_nutrition"
    return END  # or a fallback


graph = StateGraph(State)

# Nodes
graph.add_node("greet", greet_user)
graph.add_node("truncate", truncate_messages)
graph.add_node("decide_action", decide_action)
graph.add_node("find_recipe", run_find_recipe)
graph.add_node("recipe_details", run_recipe_details)
graph.add_node("analyze_nutrition", run_nutrition_analysis)

# Edges
graph.add_edge(START, "greet")
graph.add_edge("greet", "truncate")
graph.add_edge("truncate", "decide_action")
graph.add_conditional_edges("decide_action", route_tool)  # This is now correct

# Final compilation
graph = graph.compile()

initial_state = {
    "query": "Can you find me a vegan curry recipe?",
    "messages": [
        {"role": "system", "content": "Hi! I can help you find recipes, nutrition info, or cooking instructions."},
        {"role": "user", "content": "Can you find me a vegan curry recipe?"}
    ]
}

output = graph.invoke(initial_state)
print(output)