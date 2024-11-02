# MealPlan - Recipe Recommender

![MealPlan Banner](assets/banner.jpg) 


**MealPlan** is a personalized meal recommendation application designed to help you meet my dietary goals. I built this tool to assis me in planning my meals effectively and meet my dietary goals using a combination of nutritional science and machine learning.

## Features

- **Personalized Meal Recommendations**: Generates meal suggestions based on user-inputted criteria such as age, weight, height, activity level, and dietary goals.
- **Data-Driven Insights**: Utilizes a rich dataset to offer recommendations that are both nutritious and tailored to user preferences.
- **Interactive Web Interface**: Easy-to-use web interface, allowing for a seamless user experience.

## Technologies Used

- **Back-End**: FastAPI
- **Front-End**: React, Bootstrap, CSS
- **Containerization**: Docker (TODO)
- **Data Processing & Recommendations**: Python, Pandas, SciKit-Learn

### Prerequisites

- [Python 3.10+](https://www.python.org/downloads/)
- [Node.js and npm](https://nodejs.org/)

### Running the App Locally

1. **Start the Backend**:
   - Open a terminal, navigate to the `backend` directory, and start the FastAPI server with:
     ```bash
     uvicorn app.main:app --reload --port 8000
     ```

2. **Start the Frontend**:
   - In a new terminal window, navigate to the `frontend` directory and start the React development server:
     ```bash
     npm start
     ```

   The frontend will be available at `http://localhost:3000`.

### Usage

- Go to `http://localhost:3000` in your browser to access the app.

## Future Goals

- **Enhanced Recommendations**:  The current recommendation model is quite basic, and future updates aim to incorporate language models and advanced recommendation techniques to provide more nuanced and personalized meal reccomendations.
- **Detailed Nutritional Breakdown**: Show additional information like macros, vitamins, and minerals for each recommended meal along with the recipe.