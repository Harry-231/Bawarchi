import os
import requests
from typing import List, Dict, Optional
from dotenv import load_dotenv

load_dotenv()
RECIPE_API_KEY = os.getenv("SPOONACULAR_API_KEY")

RECIPE_API_ENDPOINT = "https://api.spoonacular.com/recipes/complexSearch"

def find_recipe_matches(
    query: Optional[str] = None,
    max_fat: Optional[int] = None,
    max_calories: Optional[int] = None,
    number: int = 5
) -> List[Dict]:
    """
    Calls the recipe API to find matching recipes.
    Returns a list of recipe dicts with title, image, and nutrition if available.
    """
    if not query:
        print("Query is required for Spoonacular's complexSearch")
        return []

    params = {
        "apiKey": RECIPE_API_KEY,
        "query": query,
        "number": number,
        "addRecipeNutrition": True  # Important to include nutrition data
    }

    if max_fat:
        params["maxFat"] = max_fat

    if max_calories:
        params["maxCalories"] = max_calories

    response = requests.get(RECIPE_API_ENDPOINT, params=params)
    if response.status_code != 200:
        print("API request failed:", response.status_code, response.text)
        return []

    data = response.json()

    if "results" not in data:
        print("No results found:", data)
        return []

    # Return the whole result block so you get nutrition, title, image, etc.
    return data["results"]

recipes = find_recipe_matches(
    query="beef",
    max_fat=25,
    number=2
)

print("Matching recipes:")
for i, recipe in enumerate(recipes, 1):
    print(f"{i}. {recipe['title']} (Fat: {recipe['nutrition']['nutrients'][0]['amount']}g)")
