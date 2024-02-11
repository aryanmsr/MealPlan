from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from .meal_planning_utils import RecipeDataProcessor, MealRecommender
import pandas as pd
from typing import List




app = FastAPI()


# Define Pydantic model for data validation
class UserPreferences(BaseModel):
    age: int
    sex: str
    weight: float
    height: int
    activity_level: str
    goal: str
    meals_per_day: int

@app.post("/recommend-meals/")
async def recommend_meals(preferences: UserPreferences):
    # Assuming your data files are accessible here
    recipe_file = "../data/recipes.parquet"
    ingredient_file = "../data/recipes_ingredients.csv"
    
    try:
        processor = RecipeDataProcessor(recipe_file, ingredient_file)
        processed_data = processor.process_data()
        
        recommender = MealRecommender(processed_data, [
            'calories', 'proteinContent', 'fatContent', 'saturatedFatContent', 
            'carbohydrateContent', 'fiberContent', 'sugarContent', 
            'cholesterolContent', 'sodiumContent'
        ])
        
        nutrients = recommender.estimate_daily_nutritional_needs(
            age=preferences.age, 
            sex=preferences.sex, 
            weight=preferences.weight, 
            height=preferences.height,
            activity_level=preferences.activity_level, 
            goal=preferences.goal
        )
        
        user_per_meal_needs = {k: v / preferences.meals_per_day for k, v in nutrients.items()}
        user_per_meal_needs_df = pd.DataFrame([user_per_meal_needs])
        
        meal_types = ['Breakfast', 'Lunch', 'Dinner'] if preferences.meals_per_day == 3 else \
                    ['Breakfast', 'Snack', 'Lunch', 'Dinner'] if preferences.meals_per_day == 4 else \
                    ['Breakfast', 'Snack', 'Lunch', 'Snack', 'Dinner']
        
        meal_recommendations = {}
        for meal in meal_types:
            meal_recommendations[meal] = recommender.recommend_meals(user_per_meal_needs_df, meal).to_dict(orient='records')
        
        return meal_recommendations
    
    except Exception as e:
         raise HTTPException(status_code=500, detail=str(e))
