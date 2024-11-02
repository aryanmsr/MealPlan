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
        const data = await response.json();
        setRecommendations(data);
    };

    return (
        <div className="container mt-5">
            <h2 className="text-center mb-4" style={{ color: 'black' }}>Personalized Meal Recommendations</h2>
            <div className="card p-4 shadow-sm">
                <form onSubmit={handleSubmit}>
                    <div className="row">
                        {Object.keys(userPreferences).map((key) => (
                            <div className="form-group col-md-6" key={key}>
                                <label className="form-label" style={{ fontWeight: '500', color: 'black' }}>{key.replace('_', ' ').toUpperCase()}</label>
                                <input
                                    className="form-control"
                                    name={key}
                                    value={userPreferences[key]}
                                    onChange={handleChange}
                                    placeholder={`Enter ${key.replace('_', ' ')}`}
                                />
                            </div>
                        ))}
                    </div>
                    <button type="submit" className="btn btn-primary w-100 mt-3">Get Recommendations</button>
                </form>
            </div>

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
