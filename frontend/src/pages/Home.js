import React from 'react';
import { Carousel } from 'react-bootstrap';
import {
    image1,
    image2,
    image3,
    image4,
    image5,
    image6,
    image7
} from '../assets';

function Home() {
    const images = [image1, image2, image3, image4, image5, image6, image7];

    return (
        <div>
            <Carousel className="full-width-carousel" interval={5000}>
                {images.map((image, index) => (
                    <Carousel.Item key={index}>
                        <img
                            className="d-block w-100"
                            src={image}
                            alt={`Slide ${index + 1}`}
                        />
                    </Carousel.Item>
                ))}
            </Carousel>
            <div className="container my-5">
                <h2 className="text-center mb-4" style={{ fontSize: '2.55rem' }}>About MealPlan</h2>
                <p className="text-center" style={{ fontSize: '1.25rem' }}>
                    Welcome to the MealPlan! I created this tool to provide personalized meal recommendations based on my dietary needs and goals.
                    Feel free to use the Plan Your Meal tool to receive nutritious, tailored meal suggestions.
                </p>
            </div>
        </div>
    );
}

export default Home;
