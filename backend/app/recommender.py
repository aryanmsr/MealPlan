import re
import pandas as pd
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import StandardScaler
from typing import Dict, List, Optional, Union

class RecipeDataProcessor:
    """A class to process recipe data from given files."""

    def __init__(self, recipe_file: str, ingredient_file: str) -> None:
        """
        Initialize the RecipeDataProcessor with file paths.

        :param recipe_file: Path to the recipe file.
        :param ingredient_file: Path to the ingredient file.
        """
        self.recipe_file = recipe_file
        self.ingredient_file = ingredient_file
        self.df_merged: Optional[pd.DataFrame] = None

    def load_data(self) -> None:
        """Load data from recipe and ingredient files and merge them."""
        df_recipes = pd.read_parquet(self.recipe_file)
        df_ingredients = pd.read_csv(self.ingredient_file)
        self.df_merged = df_ingredients.merge(df_recipes, how="inner", left_on="id", right_on="RecipeId")

    def select_columns(self) -> None:
        """Select relevant columns from the merged DataFrame."""
        selected_columns = [
            'id', 'name', 'ingredients_raw', 'steps', 'servings', 'serving_size', 'CookTime',
            'PrepTime', 'TotalTime', 'RecipeCategory', 'Calories', 'FatContent', 'SaturatedFatContent',
            'CholesterolContent', 'SodiumContent', 'CarbohydrateContent', 'FiberContent', 'SugarContent',
            'ProteinContent'
        ]
        self.df_merged = self.df_merged.loc[:, selected_columns]
        # Note: all nutritional amounts are on a per serving basis

    def rename_columns(self) -> None:
        """Rename columns according to a predefined naming scheme."""
        rename_dict = {
        'id': "id",  
        'name': "name",  
        'ingredients_raw': 'ingredientsRaw',
        'steps': 'steps',  
        'servings': 'servings',
        'serving_size': 'servingSize',
        'CookTime': 'cookTime',
        'PrepTime': 'prepTime',
        'TotalTime': 'totalTime',
        'RecipeCategory': 'recipeCategory',
        'Calories': 'calories',
        'FatContent': 'fatContent',
        'SaturatedFatContent': 'saturatedFatContent',
        'CholesterolContent': 'cholesterolContent',
        'SodiumContent': 'sodiumContent',
        'CarbohydrateContent': 'carbohydrateContent',
        'FiberContent': 'fiberContent',
        'SugarContent': 'sugarContent',
        'ProteinContent': 'proteinContent'}
        self.df_merged.rename(columns=rename_dict, inplace=True)
        # Note: cholesterolContent and sodiumContent are in milligrams, the rest are in grams

    def fill_missing_values(self) -> None:
        """Fill missing values in the DataFrame."""
        self.df_merged["cookTime"] = self.df_merged["cookTime"].fillna(0)
        self.df_merged.dropna(inplace=True)

    def convert_columns_to_string(self) -> None:
        """Convert columns of type 'object' to strings."""
        for col in self.df_merged.columns:
            if self.df_merged[col].dtype == 'object':
                self.df_merged[col] = self.df_merged[col].astype(str)

    @staticmethod
    def convert_iso_duration_to_readable(duration: Union[str, None]) -> str:
        """
        Convert ISO 8601 duration format to a more readable format.

        :param duration: The ISO 8601 duration string.
        :return: A human-readable duration string.
        """
        if not duration:
            return ''

        pattern = re.compile(r'PT(\d+H)?(\d+M)?')
        match = pattern.match(duration)

        hours, minutes = match.groups() if match else (None, None)
        hours_readable = f"{int(hours[:-1])} Hour{'s' if int(hours[:-1]) > 1 else ''}" if hours else ''
        minutes_readable = f"{int(minutes[:-1])} Minute{'s' if int(minutes[:-1]) > 1 else ''}" if minutes else ''

        return ' '.join(filter(None, [hours_readable, minutes_readable]))

    def convert_time_columns(self) -> None:
        """Convert time-related columns to a readable format."""
        time_cols = ['cookTime', 'prepTime', 'totalTime']
        for col in time_cols:
            self.df_merged[col] = self.df_merged[col].apply(self.convert_iso_duration_to_readable)
    
    @staticmethod
    def convert_time_to_minutes(time_str: str) -> int:
        """Convert a time string to minutes."""
        if pd.isna(time_str):
            return 0
        hours_match = re.search(r'(\d+) Hour', time_str)
        minutes_match = re.search(r'(\d+) Minute', time_str)
        hours = int(hours_match.group(1)) if hours_match else 0
        minutes = int(minutes_match.group(1)) if minutes_match else 0
        return hours * 60 + minutes

    def categorize_meal_type(self) -> None:
        """Categorize each recipe as 'Breakfast', 'Snack', or 'Main Dish'."""
        # First, convert totalTime to minutes
        self.df_merged['totalTimeMinutes'] = self.df_merged['totalTime'].apply(self.convert_time_to_minutes)

        # Define categories for Lunch
        lunch_categories = ['Lunch/Snacks', 'One Dish Meal', 'Vegetable']

        # Categorize mealType
        self.df_merged['mealType'] = self.df_merged.apply(
            lambda row: 'Breakfast' if row['recipeCategory'] == 'Breakfast' else 
                        ('Snacks' if row['totalTimeMinutes'] < 20 else 
                        ('Lunch' if row['recipeCategory'] in lunch_categories else 'Dinner')), axis=1)

    def process_data(self) -> pd.DataFrame:
        """Process the recipe data through various cleaning and transforming steps."""
        self.load_data()
        self.select_columns()
        self.rename_columns()
        self.fill_missing_values()
        self.convert_columns_to_string()
        self.convert_time_columns()
        self.categorize_meal_type()  
        return self.df_merged


class MealRecommender:
    """Class for recommending meals based on user's nutritional needs and meal type."""

    def __init__(self, processed_data: pd.DataFrame, nutritional_columns: List[str]) -> None:
        """
        Initialize the MealRecommender with processed data and nutritional columns.

        :param processed_data: Processed recipe data.
        :param nutritional_columns: List of nutritional columns to be considered for recommendations.
        """
        self.processed_data = processed_data
        self.nutritional_columns = nutritional_columns

    @staticmethod
    def estimate_daily_nutritional_needs(age: int, sex: str, weight: float, height: int,
                                         activity_level: str, goal: str) -> Dict[str, float]:
        """
        Estimate daily nutritional needs, including macronutrients and micronutrients,
        using appropriate medical guidelines. 

        :param age: Age in years.
        :param sex: 'male' or 'female'.
        :param weight: Weight in kilograms.
        :param height: Height in centimeters.
        :param activity_level: Activity level.
        :param goal: User's goal.
        :return: Dictionary of estimated nutritional needs.
        """

        # Mifflin St Jeor Equation for BMR
        bmr = 10 * weight + 6.25 * height - 5 * age + (5 if sex.lower() == 'male' else -161)
        activity_factors = {
            "sedentary": 1.2, "lightly active": 1.375, "moderately active": 1.55, 
            "very active": 1.725, "extra active": 1.9
        }
        maintenance_calories = bmr * activity_factors[activity_level.lower()]

        # Goal adjustment
        goal_adjustments = {
            "light weight loss": 0.9, "moderate weight loss": 0.8, "extreme weight loss": 0.75,
            "light muscle gain": 1.1, "moderate muscle gain": 1.2, "extreme muscle gain": 1.25,
            "maintain weight": 1.0
        }
        calories = maintenance_calories * goal_adjustments[goal.lower()]

        # Macronutrient distribution
        protein_pct = 0.3 if 'muscle gain' in goal else 0.25
        fat_pct = 0.25
        carbs_pct = 1 - protein_pct - fat_pct

        protein = (calories * protein_pct) / 4
        fat = (calories * fat_pct) / 9
        carbs = (calories * carbs_pct) / 4

        # Estimating saturated fat intake (5-6% of total calories)
        saturated_fat_pct = 0.05  # 5% for a conservative estimate
        saturated_fat = (calories * saturated_fat_pct) / 9  # 9 calories per gram

        # Fiber intake based on age and sex
        fiber = 38 if age <= 50 and sex.lower() == 'male' else 25 if age <= 50 else 30 if sex.lower() == 'male' else 21

        # Micronutrient guidelines (general estimates)
        sugar = calories * 0.10 / 4  # 10% of calories as sugar
        cholesterol = 300            # milligrams per day (general guideline)
        sodium = 2300                # milligrams per day (general guideline)

        return {
            "calories": calories,
            "proteinContent": protein,
            "fatContent": fat,
            "saturatedFatContent": saturated_fat,
            "carbohydrateContent": carbs,
            "fiberContent": fiber,
            "sugarContent": sugar,
            "cholesterolContent": cholesterol,
            "sodiumContent": sodium
        }

    def recommend_meals(self, user_nutrients: pd.DataFrame, meal_type: str, k: int = 5) -> pd.DataFrame:
        """
        Recommend meals based on the user's nutritional needs and meal type.
        
        :param user_nutrients: DataFrame of user's nutrional profile.
        :param meal_type: Type of meal to recommend (filter).
        :param k: Number of meals to recommend.
        :return: DataFrame of recommended meals.
        """
        meal_data = self.processed_data[self.processed_data['mealType'] == meal_type]
        meal_features = meal_data[self.nutritional_columns]

        # Fit the scaler on this meal type's features
        scaler = StandardScaler()
        scaled_meal_features = scaler.fit_transform(meal_features)

        # Scale user's nutritional needs using the same scaler
        user_features_scaled = scaler.transform(user_nutrients)

        # k-NN model
        knn = NearestNeighbors(n_neighbors=k, algorithm='brute', metric='euclidean')
        knn.fit(scaled_meal_features)

        # Find nearest neighbors for this meal type
        distances, indices = knn.kneighbors(user_features_scaled)
        return meal_data.iloc[indices[0]]


