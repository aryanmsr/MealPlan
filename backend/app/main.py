from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Literal, Dict, Any, AsyncGenerator
from .recommender import RecipeDataProcessor, MealRecommender
import pandas as pd
import os
import re
import json
import logging
from langchain_ollama import ChatOllama
from langchain.callbacks.base import BaseCallbackHandler
from fastapi.responses import StreamingResponse
import asyncio
from fastapi.middleware.cors import CORSMiddleware

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

app = FastAPI()

# Configure CORS for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize global variables
processed_data = None
recommender = None

class StreamingCallbackHandler(BaseCallbackHandler):
    """Handler for streaming tokens from LLM to FastAPI response."""
    
    def __init__(self):
        self.queue = asyncio.Queue()

    async def on_llm_new_token(self, token: str, **kwargs: Any) -> None:
        await self.queue.put(token)

    async def get_token(self) -> str:
        return await self.queue.get()

class UserPreferences(BaseModel):
    """Model to represent user dietary preferences and goals."""
    
    age: int
    sex: Literal['male', 'female']
    weight: float
    height: int
    activity_level: Literal[
        "sedentary", "lightly active", "moderately active", "very active", "extra active"
    ]
    goal: Literal[
        "light weight loss", "moderate weight loss", "extreme weight loss",
        "light muscle gain", "moderate muscle gain", "extreme muscle gain", "maintain weight"
    ]
    meals_per_day: int

def initialize_data():
    """Initialize and cache processed data and recommender."""
    global processed_data, recommender
    logging.info("Initializing data and recommender...")
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../"))
    print(base_dir)
    recipe_file = os.path.join(base_dir, "data", "recipes.parquet")
    ingredient_file = os.path.join(base_dir, "data", "recipes_ingredients.csv")

    processor = RecipeDataProcessor(recipe_file, ingredient_file)
    processed_data = processor.process_data()
    recommender = MealRecommender(
        processed_data,
        ['calories', 'proteinContent', 'fatContent', 'saturatedFatContent', 
         'carbohydrateContent', 'fiberContent', 'sugarContent', 
         'cholesterolContent', 'sodiumContent']
    )
    logging.info("Data and recommender initialized successfully.")

def clean_and_validate_json_string(json_string: str) -> str:
    """
    Clean and validate JSON string by ensuring correct format.
    
    Args:
        json_string (str): Raw JSON string to clean and validate.

    Returns:
        str: Cleaned JSON string or '[]' if invalid.
    """
    if not json_string or not isinstance(json_string, str):
        logging.warning("Received an empty or non-string JSON input.")
        return '[]'
    
    json_string = json_string.strip()
    if json_string.startswith("[") and json_string.endswith("]"):
        json_string = re.sub(r',\s*]', ']', json_string)
        json_string = re.sub(r',\s*}', '}', json_string)
        return json_string
    else:
        logging.warning(f"Invalid JSON format: {json_string}")
        return '[]'

@app.on_event("startup")
def startup_event():
    """Initialize data when the application starts."""
    initialize_data()

async def async_generator_wrapper(generator):
    """Convert a generator to an asynchronous iterator."""
    for item in generator:
        yield item
        await asyncio.sleep(0.05)

async def generate_summary_stream(preferences, nutrients) -> AsyncGenerator[str, None]:
    """
    Generate and stream summary based on user preferences and nutrient profile using LLM.
    
    Args:
        preferences (UserPreferences): User's dietary preferences.
        nutrients (dict): Nutritional profile based on preferences.

    Yields:
        str: Streaming chunks of generated summary.
    """
    logging.info("Generating summary stream with LLM.")
    prompt = (
        f"User details: {preferences.age} years old, {preferences.sex}, weighing {preferences.weight} kg, "
        f"height {preferences.height} cm, activity level: {preferences.activity_level}, "
        f"goal: {preferences.goal}. Nutritional needs: approximately {int(nutrients['calories'])} calories, "
        f"{int(nutrients['proteinContent'])}g protein, {int(nutrients['carbohydrateContent'])}g carbs, "
        f"and {int(nutrients['fatContent'])}g fat daily."
    )
    
    llm = ChatOllama(
        model="llama3.2:1b",
        temperature=0.2,
        num_predict=256,
        base_url="http://ollama:11434",
        callbacks=[StreamingCallbackHandler()]
    )
    
    messages = [
        (
            "system",
            """ You are a nutrition assistant within a user-facing web application whole sole purpose is to provide a user-friendly summary of the user’s daily nutritional profile based on their input parameters, including age, weight, height, activity level, and dietary goals. 
            The user's nutritional needs have already been calculated for you using nutritional science and best practices. It will be part of the user input after 'Nutrional needs:'. 

            Structure your response similar to:
            “Based on your input parameters and goals, I have estimated that your daily nutritional intake should be approximately [calories] calories, with [protein] grams of protein, [carbohydrates] grams of carbohydrates, and [fat] grams of fat. 
            Here are some delicious recipe suggestions to help you reach your [goal] goal!”

            Please adhere to these guidelines:
            - Keep the response concise, clear, and accessible. DO NOT provide any recommendations.
            - DO NOT use markdown syntax.
            - DO NOT add or recommend anything outside of the scope of the user details. 
            - DO NOT provide any actual recipes. 
            """
        ),
        ("user", prompt)
    ]
    print(messages)
    
    token_generator = llm.stream(messages)
    async for chunk in async_generator_wrapper(token_generator):
        yield chunk.content if hasattr(chunk, "content") else str(chunk)

@app.post("/recommend-summary/")
async def recommend_summary(preferences: UserPreferences):
    """
    Generate and stream summary for user preferences using LLM.

    Args:
        preferences (UserPreferences): User preferences for summary generation.

    Returns:
        StreamingResponse: Streamed response with summary.
    """
    logging.info(f"Received user preferences: {preferences}")
    try:
        nutrients = recommender.estimate_daily_nutritional_needs(
            age=preferences.age, 
            sex=preferences.sex, 
            weight=preferences.weight, 
            height=preferences.height,
            activity_level=preferences.activity_level, 
            goal=preferences.goal
        )
        logging.info("Nutritional needs calculated successfully.")
        return StreamingResponse(generate_summary_stream(preferences, nutrients), media_type="text/plain")
    except Exception as e:
        logging.error(f"Error generating summary: {e}")
        raise HTTPException(status_code=500, detail="An error occurred while generating the summary.")

@app.post("/recommend-meals/")
async def recommend_meals(preferences: UserPreferences):
    """
    Generate meal recommendations based on user preferences.

    Args:
        preferences (UserPreferences): User preferences for meal recommendations.

    Returns:
        dict: Meal recommendations based on user preferences.
    """
    logging.info(f"Received preferences for meal recommendation: {preferences}")
    try:
        nutrients = recommender.estimate_daily_nutritional_needs(
            age=preferences.age, 
            sex=preferences.sex, 
            weight=preferences.weight, 
            height=preferences.height,
            activity_level=preferences.activity_level, 
            goal=preferences.goal
        )
        logging.info(f"User nutritional needs calculated for meal recommendations: {nutrients}")
        
        user_per_meal_needs = {k: v / preferences.meals_per_day for k, v in nutrients.items()}
        user_per_meal_needs_df = pd.DataFrame([user_per_meal_needs])
        
        possible_meal_types = ["Breakfast", "Lunch", "Dinner", "Snacks"]
        meal_types = possible_meal_types[:preferences.meals_per_day]
        
        meal_recommendations = {}
        for meal in meal_types:
            meals = recommender.recommend_meals(user_per_meal_needs_df, meal).to_dict(orient='records')
            for m in meals:
                try:
                    ingredients_raw = clean_and_validate_json_string(m.get("ingredientsRaw", "[]"))
                    steps_raw = clean_and_validate_json_string(m.get("steps", "[]"))
                    m["ingredients"] = json.loads(ingredients_raw) if ingredients_raw != '[]' else ["Data unavailable due to formatting issues"]
                    m["steps"] = json.loads(steps_raw) if steps_raw != '[]' else ["Data unavailable due to formatting issues"]
                except json.JSONDecodeError as e:
                    logging.error(f"JSON decoding error for meal '{m['name']}': {e}")
                    m["ingredients"], m["steps"] = ["Data unavailable"], ["Data unavailable"]

                m["nutrition"] = {
                    "Protein": f"{m.get('proteinContent', 'N/A')}g",
                    "Fat": f"{m.get('fatContent', 'N/A')}g",
                    "Saturated Fat": f"{m.get('saturatedFatContent', 'N/A')}g",
                    "Carbohydrates": f"{m.get('carbohydrateContent', 'N/A')}g",
                    "Fiber": f"{m.get('fiberContent', 'N/A')}g",
                    "Sugar": f"{m.get('sugarContent', 'N/A')}g",
                    "Cholesterol": f"{m.get('cholesterolContent', 'N/A')}mg",
                    "Sodium": f"{m.get('sodiumContent', 'N/A')}mg"
                }

                m["servings"] = m.get("servings", "N/A")
                m["serving_size"] = m.get("servingSize", "N/A")
                m["prep_time"] = m.get("prepTime", "N/A")
                m["cook_time"] = m.get("cookTime", "N/A")
            meal_recommendations[meal] = meals
        logging.info("Meal recommendations generated successfully.")
        return meal_recommendations

    except FileNotFoundError as e:
        logging.error(f"File not found: {str(e)}")
        raise HTTPException(status_code=500, detail="Data file not found")
    except ValueError as e:
        logging.error(f"Invalid input: {str(e)}")
        raise HTTPException(status_code=400, detail="Invalid data or input")
    except Exception as e:
        logging.error(f"An error occurred: {str(e)}")
        raise HTTPException(status_code=500, detail="An error occurred")