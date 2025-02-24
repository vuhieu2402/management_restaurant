import React, { useEffect, useState, useContext } from "react";
import axios from "axios";
import { CartContext } from "../context/CartContext";

const CLOUDINARY_BASE_URL = "https://res.cloudinary.com/dtubffjwu/";

const FoodItem = ({ id, image, name, description, price, category }) => {
  const { addToCart } = useContext(CartContext);
  const imageUrl = image.startsWith("http") ? image : CLOUDINARY_BASE_URL + image;

  return (
    <div className={`col-sm-6 col-lg-4 all ${category}`}>
      <div className="box">
        <div>
          <div className="img-box">
            <img src={imageUrl} alt={name} />
          </div>
          <div className="detail-box">
            <h5>{name}</h5>
            <p>{description}</p>
            <div className="options">
              <h6>${price}</h6>
              <button onClick={() => addToCart(id)} className="cart-button">
                <svg
                  version="1.1"
                  id="Capa_1"
                  xmlns="http://www.w3.org/2000/svg"
                  viewBox="0 0 456.029 456.029"
                  style={{ width: 24, height: 24 }}
                >
                  <g>
                    <g>
                      <path d="M345.6,338.862c-29.184,0-53.248,23.552-53.248,53.248c0,29.184,23.552,53.248,53.248,53.248
                 c29.184,0,53.248-23.552,53.248-53.248C398.336,362.926,374.784,338.862,345.6,338.862z" />
                    </g>
                  </g>
                </svg>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

const FoodSection = () => {
  const [foodItems, setFoodItems] = useState([]);

  useEffect(() => {
    axios.get("http://127.0.0.1:8000/api/dishes/")
      .then(response => setFoodItems(response.data))
      .catch(error => console.error("Error fetching data:", error));
  }, []);

  return (
    <section className="food_section layout_padding-bottom">
      <div className="container">
        <div className="heading_container heading_center">
          <h2>Our Menu</h2>
        </div>

        <div className="filters-content">
          <div className="row grid">
            {foodItems.map((item) => (
              <FoodItem
                key={item.id}
                id={item.id}
                image={item.url_img}
                name={item.name}
                description={item.description}
                price={item.price}
                category={item.category}
              />
            ))}
          </div>
        </div>
      </div>
    </section>
  );
};

export default FoodSection;
