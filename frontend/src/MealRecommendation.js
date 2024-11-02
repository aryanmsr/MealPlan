import React, { useState } from 'react';

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
        const data = await response.json();
        console.log('Backend Response:', data); // Log response for debugging
        setRecommendations(data);
    };

    return (
        <div>
            <h2>Meal Recommendations</h2>
            <form onSubmit={handleSubmit}>
                {Object.keys(userPreferences).map((key) => (
                    <div className="form-group" key={key}>
                        <input
                            className="form-control"
                            name={key}
                            value={userPreferences[key]}
                            onChange={handleChange}
                            placeholder={key.replace('_', ' ')}
                        />
                    </div>
                ))}
                <button type="submit" className="btn btn-primary">Get Recommendations</button>
            </form>
            {Object.entries(recommendations).map(([mealType, meals]) => (
                <div key={mealType}>
                    <h3>{mealType}</h3>
                    {Array.isArray(meals) && meals.length > 0 ? (
                        meals.map((meal, index) => (
                            <div className="card" key={index} style={{ width: '18rem', marginBottom: '1rem' }}>
                                <div className="card-body">
                                    <h5 className="card-title">{meal.name}</h5>
                                    <p className="card-text">{meal.calories} calories</p>
                                    {/* Additional meal details if needed */}
                                </div>
                            </div>
                        ))
                    ) : (
                        <p>No meal recommendations available.</p>
                    )}
                </div>
            ))}
        </div>
    );
}

export default MealRecommendation;
