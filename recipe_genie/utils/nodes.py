# nodes.py

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from .state import State
from .tools import find_recipe_matches, get_recipe_details, analyze_nutrition

llm = ChatOpenAI(model="gpt-4o", temperature=0)

### 1. GREETING Node

def greet_user(state: State) -> dict:
    message = AIMessage(content=(
        "👋 Hi! I'm your smart kitchen assistant.\n\n"
        "Here's what I can help you with:\n"
        "1. 🍽️ Find a recipe based on ingredients, cuisine, or dietary needs\n"
        "2. 📋 Get detailed instructions for a recipe\n"
        "3. 🧪 Analyze the nutrition info of a dish or ingredients\n\n"
        "How can I assist you today?"
    ))
    return {"messages": [message]}


### 2. ROUTER Node: Let LLM choose which tool to invoke

def decide_action(state: State) -> dict:
    recent_msgs = state["messages"][-5:]

    system_prompt = SystemMessage(content="""
You are a smart assistant. Based on the latest message in the conversation, decide which of these actions to take:

- 'find_recipe' if the user wants to find recipes
- 'recipe_details' if the user wants instructions for a specific recipe
- 'analyze_nutrition' if the user wants to get nutritional info

Respond ONLY with the action name and extract any required fields (like ingredients, recipe title, etc.).
    """)

    action_response = llm.invoke([system_prompt] + recent_msgs)

    content = action_response.content.lower()

    # Routing
    if "find_recipe" in content:
        return {"next_action": "find_recipe"}
    elif "recipe_details" in content:
        return {"next_action": "recipe_details"}
    elif "analyze_nutrition" in content:
        return {"next_action": "analyze_nutrition"}
    else:
        fallback = AIMessage(content="Sorry, I couldn't figure out your intent. Could you please rephrase?")
        return {"messages": [fallback]}


### 3. ACTION Nodes

def run_find_recipe(state: State) -> dict:
    query = state.get("query")
    ingredients = state.get("ingredients")
    cuisine = state.get("cuisine")
    dietary = state.get("dietary_restrictions")
    meal_type = state.get("meal_type")

    recipes = find_recipe_matches(query=query, ingredients=ingredients,
                                  cuisine=cuisine, dietary_restrictions=dietary,
                                  meal_type=meal_type, number=5)

    if not recipes:
        reply = "😕 I couldn't find any recipes based on the given inputs. Could you try different ingredients?"
    else:
        reply = "👨‍🍳 Here are some recipes you might like:\n" + "\n".join(f"- {r}" for r in recipes)

    return {
        "messages": [AIMessage(content=reply)],
        "recipe_matches": recipes
    }


def run_recipe_details(state: State) -> dict:
    query = state.get("query")
    if not query:
        return {"messages": [AIMessage(content="❗Please specify the recipe title you'd like instructions for.")]}

    details = get_recipe_details(query)

    return {
        "messages": [AIMessage(content="📋 Got the recipe details. Check your console (or UI) for the full instructions.")],
        "recipe_details": {"title": query, "instructions": "Printed to console (mock return)"}
    }


def run_nutrition_analysis(state: State) -> dict:
    query = state.get("query")
    if not query:
        return {"messages": [AIMessage(content="❗Please describe the ingredients or dish for nutrition analysis.")]}

    nutrition = analyze_nutrition(query)
    reply = (
        f"🧪 Nutrition Breakdown:\n"
        f"- Calories: {nutrition.get('calories')} kcal\n"
        f"- Protein: {nutrition.get('protein')} g\n"
        f"- Fat: {nutrition.get('fat')} g\n"
        f"- Carbs: {nutrition.get('carbs')} g"
    )

    return {
        "messages": [AIMessage(content=reply)],
        "nutrition_info": nutrition
    }


### 4. Truncate Messages

def truncate_messages(state: State) -> dict:
    messages = state.get("messages", [])
    return {"messages": messages[-5:]}  # Keep only last 5
