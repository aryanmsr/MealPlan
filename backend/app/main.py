"""
main.py - MealPlan Meal Recommendation API

This module sets up the FastAPI application for the MealPlan app, providing an endpoint
to generate personalized meal recommendations based on user preferences.

Key functionalities:

- **UserPreferences Model**: Defines a Pydantic model for validating incoming user data,
  ensuring the API receives the necessary information in the correct format.

- **Recipe Data Processing**:
  - Loads recipe data from `recipes.parquet` and ingredient data from `recipes_ingredients.csv`.
  - Processes the data using `RecipeDataProcessor` to prepare it for recommendation.

- **Meal Recommendation Logic**:
  - Calculates the user's daily nutritional needs using the Mifflin-St Jeor equation, adjusted
    for activity level and personal goals (e.g., weight loss, muscle gain).
  - Determines per-meal nutritional requirements by dividing daily needs by the number of meals.
  - Dynamically selects meal types (e.g., Breakfast, Lunch, Dinner) based on the user's specified
    number of meals per day.
  - Generates meal recommendations for each meal type using `MealRecommender`, which employs
    a k-NN algorithm to find meals closest to the user's nutritional needs.

- **API Endpoint**:
  - **POST `/recommend-meals/`**: Accepts user preferences in JSON format and returns a dictionary
    of meal recommendations categorized by meal type.

- **Error Handling**:
  - Provides HTTP exceptions with appropriate status codes and messages for issues such as
    missing data files (`FileNotFoundError`) or invalid input data (`ValueError`).

Usage:

The API expects a JSON payload with the following structure when calling the `/recommend-meals/` endpoint:

```json
{
    "age": 30,
    "sex": "female",
    "weight": 65.0,
    "height": 165,
    "activity_level": "moderately active",
    "goal": "light weight loss",
    "meals_per_day": 3
}

"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Literal
from .recommender import RecipeDataProcessor, MealRecommender
import pandas as pd
import os

app = FastAPI()

# Caching the processed data and recommender at startup
processed_data = None
recommender = None

def initialize_data():
    """Function to initialize and cache processed data and recommender."""
    global processed_data, recommender
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
    recipe_file = os.path.join(base_dir, "data", "recipes.parquet")
    ingredient_file = os.path.join(base_dir, "data", "recipes_ingredients.csv")

    processor = RecipeDataProcessor(recipe_file, ingredient_file)
    processed_data = processor.process_data()

    recommender = MealRecommender(processed_data, [
        'calories', 'proteinContent', 'fatContent', 'saturatedFatContent', 
        'carbohydrateContent', 'fiberContent', 'sugarContent', 
        'cholesterolContent', 'sodiumContent'
    ])

@app.on_event("startup")
def startup_event():
    """Initialize data when FastAPI app starts."""
    initialize_data()

# Defining Pydantic model for data validation with enums for predefined options
class UserPreferences(BaseModel):
    age: int
    sex: Literal['male', 'female']
    weight: float
    height: int
    activity_level: Literal["sedentary", "lightly active", "moderately active", "very active", "extra active"]
    goal: Literal["light weight loss", "moderate weight loss", "extreme weight loss", 
                  "light muscle gain", "moderate muscle gain", "extreme muscle gain", "maintain weight"]
    meals_per_day: int

@app.post("/recommend-meals/")
async def recommend_meals(preferences: UserPreferences):
    try:
        # Calculating daily nutritional needs based on user preferences
        nutrients = recommender.estimate_daily_nutritional_needs(
            age=preferences.age, 
            sex=preferences.sex, 
            weight=preferences.weight, 
            height=preferences.height,
            activity_level=preferences.activity_level, 
            goal=preferences.goal
        )

        # Calculating per-meal nutritional needs
        user_per_meal_needs = {k: v / preferences.meals_per_day for k, v in nutrients.items()}
        user_per_meal_needs_df = pd.DataFrame([user_per_meal_needs])

        # Defining meal types based on the number of meals per day
        possible_meal_types = ["Breakfast", "Lunch", "Dinner", "Snack"]
        meal_types = possible_meal_types[:preferences.meals_per_day]

        # Generating meal recommendations
        meal_recommendations = {}
        for meal in meal_types:
            meal_recommendations[meal] = recommender.recommend_meals(user_per_meal_needs_df, meal).to_dict(orient='records')

        return meal_recommendations

    except FileNotFoundError as e:
        raise HTTPException(status_code=500, detail=f"Data file not found: {str(e)}")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid data or input: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")


