import os
import requests
from typing import List, Dict, Optional
from dotenv import load_dotenv
import getpass
from langchain_tavily import TavilySearch
import json


load_dotenv()

if not os.environ.get("TAVILY_API_KEY"):
    os.environ["TAVILY_API_KEY"] = getpass.getpass("Tavily API key:\n")

RECIPE_API_KEY = os.getenv("SPOONACULAR_API_KEY")
RECIPE_API_ENDPOINT = "https://api.spoonacular.com/recipes/complexSearch"
NUTRITION_API_ENDPOINT = "https://trackapi.nutritionix.com/v2/natural/nutrients"
NUTRITION_APP_ID = os.getenv("NUTRITIONIX_APP_ID")
NUTRITION_APP_KEY = os.getenv("NUTRITIONIX_APP_KEY")


def find_recipe_matches(
    query: Optional[str] = None,
    ingredients: Optional[List[str]] = None,
    cuisine: Optional[str] = None,
    dietary_restrictions: Optional[List[str]] = None,
    meal_type: Optional[str] = None,
    number: Optional[int] = None
) -> List[str]:
    """
    Calls the recipe API to find matching recipes based on user inputs.
    Returns a list of recipe titles.
    """
    if not ingredients:
        return []

    params = {
        "apiKey": RECIPE_API_KEY,
        "query": query or "",
        "includeIngredients": ",".join(ingredients),
        "cuisine": cuisine or "",
        "type": meal_type or "",
        "diet": ",".join(dietary_restrictions or []),
        "number": number
    }

    

    response = requests.get(RECIPE_API_ENDPOINT, params=params)
    data = response.json()

    if "results" not in data:
        print("API Error or no results:", data)
        return []

    recipes = data["results"]
    print("Found recipes:", len(recipes))
    for i, recipe in enumerate(recipes):
        print(f"{i+1}. {recipe['title']}")

    return [recipe["title"] for recipe in recipes]

def get_recipe_details(recipe_title: str) -> None:
    """
    Calls the Tavily Search API to get detailed information about a specific recipe.
    Returns a dictionary with recipe
    """
    query = f"Find detailed instruction for the recipe: {recipe_title}"
    tool = TavilySearch()
    tool_model_call = {
        "args" : {
            "query": query},
        "id" : "1",
        "max_results" : "1",
        "topic":"general",
        
         "type":"tool_call",
        
    }
    tool_msg = tool.invoke(tool_model_call).content
    data = json.loads(tool_msg)
    best_recipe = max(data["results"], key=lambda x: x["score"])
    title = best_recipe["title"]
    instructions = best_recipe["content"]
    print(f"Recipe Title: {title}")
    print(f"Instructions: {instructions}")
    return ""

def analyze_nutrition(recipe_details: str) -> Dict:
    """
    Calls the Nutritionix API to get nutrition analysis for natural language ingredients.
    """
    headers = {
        "Content-Type": "application/json",
        "x-app-id": NUTRITION_APP_ID,
        "x-app-key": NUTRITION_APP_KEY
    }

    payload = {
        "query": recipe_details,
    }

    response = requests.post(NUTRITION_API_ENDPOINT, json=payload, headers=headers)
    response.raise_for_status()  # raise an error if API fails
    data = response.json()
    

    # Grab first food item (for single ingredient queries)
    foods = data.get("foods", [{}])[:2]

    for i, food in enumerate(foods, 1):
        print(f"Food Name: {food.get('food_name')}")
        print(f"Serving Quantity: {food.get('serving_qty')} {food.get('serving_unit')}")
        print(f"Serving Weight: {food.get('serving_weight_grams')} g")
        print(f"Calories: {food.get('nf_calories')} kcal")
        print(f"Total Fat: {food.get('nf_total_fat')} g")
        print(f"Saturated Fat: {food.get('nf_saturated_fat')} g")
        print(f"Cholesterol: {food.get('nf_cholesterol')} mg")
        print(f"Sodium: {food.get('nf_sodium')} mg")
        print(f"Total Carbohydrate: {food.get('nf_total_carbohydrate')} g")
        print(f"Dietary Fiber: {food.get('nf_dietary_fiber')} g")


    return {
        "food": food.get("food_name"),
        "calories": food.get("nf_calories"),
        "fat": food.get("nf_total_fat"),
        "protein": food.get("nf_protein"),
        "carbs": food.get("nf_total_carbohydrate")
    }


