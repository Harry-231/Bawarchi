from typing import Annotated , Optional

from typing_extensions import TypedDict

from langgraph.graph import StateGraph, START , END
from langgraph.graph.message import add_messages

class State(TypedDict):
    """ Tracks the state of the graph throughout the workflow for recipe generation."""

    # Input from the user regarding cuisine , ingredients , dietary_restrictions, calories_requirement , meal_type
    cuisine : Optional[str] = None
    ingredients : Optional[list[str]] = None
    dietary_restrictions : Optional[list[str]] = None
    calores_requirement : Optional[int] = None
    meal_type : Optional[str] = "Lunch"
    
    # Tool Ouputs 
    reicpe_matches : Optional[list[str]] = None
    recipe_details : Optional[dict] = None
    nutrition_info : Optional[dict] = None

    # Final output of the graph
    final_output: Optional[str] = None

    
