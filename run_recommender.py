import pandas as pd
from backend.app.recommender import RecipeDataProcessor, MealRecommender

def main():
    #Main Entry Point for Meal Recommendation Engine

    recipe_file = "./data/recipes.parquet"
    ingredient_file = "./data/recipes_ingredients.csv"

    processor = RecipeDataProcessor(recipe_file, ingredient_file)
    processed_data = processor.process_data()
    nutritional_columns = ['calories', 'proteinContent', 'fatContent', 'saturatedFatContent', 'carbohydrateContent', 
                           'fiberContent', 'sugarContent', 'cholesterolContent', 'sodiumContent']

    recommender = MealRecommender(processed_data, nutritional_columns)

    nutrients = recommender.estimate_daily_nutritional_needs(age=57, sex='male', weight=86, height=173,
                                                             activity_level='moderately active', goal='moderate weight loss')

    meals_per_day = 3
    user_per_meal_needs = [value / meals_per_day for key, value in nutrients.items()]
    user_per_meal_needs_df = pd.DataFrame([user_per_meal_needs], columns=nutritional_columns)

    meal_types = ['Breakfast', 'Lunch', 'Dinner'] if meals_per_day == 3 else \
                 ['Breakfast', 'Snack', 'Lunch', 'Dinner'] if meals_per_day == 4 else \
                 ['Breakfast', 'Snack', 'Lunch', 'Snack', 'Dinner']

    meal_recommendations = {}
    for meal in meal_types:
        meal_recommendations[meal] = recommender.recommend_meals(user_per_meal_needs_df, meal)

    for meal, recommendations in meal_recommendations.items():
        print(f"Recommendations for {meal}:")
        print(recommendations[['name', 'mealType']])
        print()

if __name__ == "__main__":
    main()