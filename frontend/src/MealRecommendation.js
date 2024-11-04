import React, { useState } from 'react';
import Accordion from 'react-bootstrap/Accordion';
import { Card } from 'react-bootstrap';

function MealRecommendation() {
    const [userPreferences, setUserPreferences] = useState({
        age: '',
        sex: '',
        weight: '',
        height: '',
        activity_level: '',
        goal: '',
        meals_per_day: ''
    });
    const [recommendations, setRecommendations] = useState({});
    const [summary, setSummary] = useState('');  // State for streaming summary

    const handleChange = (event) => {
        const { name, value } = event.target;
        setUserPreferences(prevState => ({
            ...prevState,
            [name]: value
        }));
    };
    const handleSubmit = async (event) => {
        event.preventDefault();
        try {
            // Fetch and stream summary
            const response = await fetch('http://localhost:8000/recommend-summary/', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(userPreferences),
            });
    
            if (response.ok) {
                const reader = response.body.getReader();
                const decoder = new TextDecoder();
                let summaryText = '';
                while (true) {
                    const { done, value } = await reader.read();
                    if (done) break;
                    summaryText += decoder.decode(value, { stream: true });
                    setSummary(summaryText);  // Update summary as it streams
                }
            }
    
            // Fetch recommendations separately after summary is complete
            const recommendationsResponse = await fetch('http://localhost:8000/recommend-meals/', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(userPreferences),
            });
    
            if (recommendationsResponse.ok) {
                const data = await recommendationsResponse.json();
                console.log("Recommendations Data:", data); // Log to verify
                setRecommendations(data);  // Set the data directly as recommendations
            } else {
                console.error("Failed to fetch recommendations");
            }
        } catch (error) {
            console.error("An error occurred:", error);
        }
    };
    
    // Function to format nutrition with units
    const formatNutrition = (key, value) => {
        const gramUnits = ["Protein", "Fat", "Saturated Fat", "Carbohydrates", "Fiber", "Sugar"];
        const mgUnits = ["Cholesterol", "Sodium"];
        
        if (gramUnits.includes(key)) {
            return `${value} g`;
        } else if (mgUnits.includes(key)) {
            return `${value} mg`;
        }
        return value;
    };

    return (
        <div className="container mt-5">
            <h2 className="text-center mb-4" style={{ color: 'black' }}>Personalized Meal Recommendations</h2>
            <div className="card p-4 shadow-sm">
                <form onSubmit={handleSubmit}>
                    <div className="row">
                        {/* Input fields for user preferences */}
                        <div className="form-group col-md-6">
                            <label className="form-label" style={{ fontWeight: '500', color: 'black' }}>Age</label>
                            <input
                                className="form-control"
                                name="age"
                                type="number"
                                value={userPreferences.age}
                                onChange={handleChange}
                                placeholder="Enter age"
                            />
                        </div>
                        <div className="form-group col-md-6">
                            <label className="form-label" style={{ fontWeight: '500', color: 'black' }}>Sex</label>
                            <select
                                className="form-control"
                                name="sex"
                                value={userPreferences.sex}
                                onChange={handleChange}
                            >
                                <option value="">Select sex</option>
                                <option value="male">Male</option>
                                <option value="female">Female</option>
                            </select>
                        </div>
                        <div className="form-group col-md-6">
                            <label className="form-label" style={{ fontWeight: '500', color: 'black' }}>Weight (kg)</label>
                            <input
                                className="form-control"
                                name="weight"
                                type="number"
                                value={userPreferences.weight}
                                onChange={handleChange}
                                placeholder="Enter weight"
                            />
                        </div>
                        <div className="form-group col-md-6">
                            <label className="form-label" style={{ fontWeight: '500', color: 'black' }}>Height (cm)</label>
                            <input
                                className="form-control"
                                name="height"
                                type="number"
                                value={userPreferences.height}
                                onChange={handleChange}
                                placeholder="Enter height"
                            />
                        </div>
                        <div className="form-group col-md-6">
                            <label className="form-label" style={{ fontWeight: '500', color: 'black' }}>Activity Level</label>
                            <select
                                className="form-control"
                                name="activity_level"
                                value={userPreferences.activity_level}
                                onChange={handleChange}
                            >
                                <option value="">Select activity level</option>
                                <option value="sedentary">Sedentary</option>
                                <option value="lightly active">Lightly Active</option>
                                <option value="moderately active">Moderately Active</option>
                                <option value="very active">Very Active</option>
                                <option value="extra active">Extra Active</option>
                            </select>
                        </div>
                        <div className="form-group col-md-6">
                            <label className="form-label" style={{ fontWeight: '500', color: 'black' }}>Goal</label>
                            <select
                                className="form-control"
                                name="goal"
                                value={userPreferences.goal}
                                onChange={handleChange}
                            >
                                <option value="">Select goal</option>
                                <option value="light weight loss">Light Weight Loss</option>
                                <option value="moderate weight loss">Moderate Weight Loss</option>
                                <option value="extreme weight loss">Extreme Weight Loss</option>
                                <option value="light muscle gain">Light Muscle Gain</option>
                                <option value="moderate muscle gain">Moderate Muscle Gain</option>
                                <option value="extreme muscle gain">Extreme Muscle Gain</option>
                                <option value="maintain weight">Maintain Weight</option>
                            </select>
                        </div>
                        <div className="form-group col-md-6">
                            <label className="form-label" style={{ fontWeight: '500', color: 'black' }}>Meals per Day</label>
                            <select
                                className="form-control"
                                name="meals_per_day"
                                value={userPreferences.meals_per_day}
                                onChange={handleChange}
                            >
                                <option value="">Select meals per day</option>
                                <option value="2">2</option>
                                <option value="3">3</option>
                                <option value="4">4</option>
                                <option value="5">5</option>
                            </select>
                        </div>
                    </div>
                    <button type="submit" className="btn btn-primary w-100 mt-3">Get Recommendations</button>
                </form>
            </div>

            {/* Render the streaming summary first */}
            {summary && (
                <div className="alert alert-info mt-4">
                    <strong>AI Summary:</strong> {summary}
                </div>
            )}
    {/* Display recommendations */}
{recommendations && Object.keys(recommendations).length > 0 && (
    <div className="mt-5">
        <h3 style={{ fontWeight: '600', color: 'black' }}>Meal Recommendations</h3>
        <Accordion defaultActiveKey="0" className="mt-3">
            {Object.entries(recommendations).map(([mealType, meals], index) => (
                <Accordion.Item eventKey={index.toString()} key={mealType}>
                    <Accordion.Header>{mealType}</Accordion.Header>
                    <Accordion.Body>
                        {Array.isArray(meals) && meals.length > 0 ? (
                            meals.map((meal, idx) => {
                                return (
                                    <Card className="mb-3" key={idx} style={{ border: '1px solid #ddd' }}>
                                        <Card.Body>
                                            <Card.Title>{meal.name}</Card.Title>
                                            <Card.Text><strong>Calories:</strong> {meal.calories} kcal</Card.Text>
                                            <Accordion>
                                                <Accordion.Item eventKey={`details-${idx}`}>
                                                    <Accordion.Header>Show Recipe</Accordion.Header>
                                                    <Accordion.Body>
                                                        <div><strong>Ingredients:</strong>
                                                            <ul>
                                                                {Array.isArray(meal.ingredients) ? (
                                                                    meal.ingredients.map((ingredient, i) => (
                                                                        <li key={i}>{ingredient}</li>
                                                                    ))
                                                                ) : (
                                                                    <li>{meal.ingredients}</li>
                                                                )}
                                                            </ul>
                                                        </div>
                                                        <div><strong>Steps:</strong>
                                                            <ol>
                                                                {Array.isArray(meal.steps) ? (
                                                                    meal.steps.map((step, i) => (
                                                                        <li key={i}>{step}</li>
                                                                    ))
                                                                ) : (
                                                                    <li>{meal.steps}</li>
                                                                )}
                                                            </ol>
                                                        </div>
                                                        <Card.Text><strong>Servings:</strong> {meal.servings}</Card.Text>
                                                        <Card.Text><strong>Serving Size:</strong> {meal.serving_size}</Card.Text>
                                                        <Card.Text><strong>Prep Time:</strong> {meal.prep_time}</Card.Text>
                                                        <Card.Text><strong>Cook Time:</strong> {meal.cook_time}</Card.Text>
                                                        
                                                    </Accordion.Body>
                                                </Accordion.Item>
                                                <Accordion.Item eventKey={`nutrition-${idx}`}>
                                                    <Accordion.Header>Nutrition Information</Accordion.Header>
                                                    <Accordion.Body>
                                                        <ul>
                                                            <li><strong>Protein:</strong> {meal.proteinContent} g</li>
                                                            <li><strong>Fat:</strong> {meal.fatContent} g</li>
                                                            <li><strong>Saturated Fat:</strong> {meal.saturatedFatContent} g</li>
                                                            <li><strong>Carbohydrates:</strong> {meal.carbohydrateContent} g</li>
                                                            <li><strong>Fiber:</strong> {meal.fiberContent} g</li>
                                                            <li><strong>Sugar:</strong> {meal.sugarContent} g</li>
                                                            <li><strong>Cholesterol:</strong> {meal.cholesterolContent} mg</li>
                                                            <li><strong>Sodium:</strong> {meal.sodiumContent} mg</li>
                                                        </ul>
                                                    </Accordion.Body>
                                                </Accordion.Item>
                                            </Accordion>
                                        </Card.Body>
                                    </Card>
                                );
                            })
                        ) : (
                            <p>No meal recommendations available.</p>
                        )}
                    </Accordion.Body>
                </Accordion.Item>
            ))}
        </Accordion>
    </div>
)}
        </div>
    );
}

export default MealRecommendation;
