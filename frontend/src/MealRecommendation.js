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

    const handleChange = (event) => {
        const { name, value } = event.target;
        setUserPreferences(prevState => ({
            ...prevState,
            [name]: value
        }));
    };

    const handleSubmit = async (event) => {
        event.preventDefault();
        const response = await fetch('/recommend-meals/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(userPreferences),
        });
    
        if (response.ok) {
            const data = await response.json();
            console.log("Backend Response:", data);  // For debugging
            setRecommendations(data);  // Update state with response data
        } else {
            console.error("Failed to fetch recommendations");
        }
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
                            <input
                                className="form-control"
                                name="meals_per_day"
                                type="number"
                                value={userPreferences.meals_per_day}
                                onChange={handleChange}
                                placeholder="Enter meals per day"
                            />
                        </div>
                    </div>
                    <button type="submit" className="btn btn-primary w-100 mt-3">Get Recommendations</button>
                </form>
            </div>

            {/* Display recommendations */}
            {Object.keys(recommendations).length > 0 && (
                <div className="mt-5">
                    <h3 style={{ fontWeight: '600', color: 'black' }}>Meal Recommendations</h3>
                    <Accordion defaultActiveKey="0" className="mt-3">
                        {Object.entries(recommendations).map(([mealType, meals], index) => (
                            <Accordion.Item eventKey={index.toString()} key={mealType}>
                                <Accordion.Header>{mealType}</Accordion.Header>
                                <Accordion.Body>
                                    {Array.isArray(meals) && meals.length > 0 ? (
                                        meals.map((meal, idx) => (
                                            <Card className="mb-3" key={idx} style={{ border: '1px solid #ddd' }}>
                                                <Card.Body>
                                                    <Card.Title>{meal.name}</Card.Title>
                                                    <Card.Text>{meal.calories} calories</Card.Text>
                                                </Card.Body>
                                            </Card>
                                        ))
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
