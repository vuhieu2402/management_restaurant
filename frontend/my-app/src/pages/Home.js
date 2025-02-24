import React, { useState, useEffect } from "react";
import OfferSection from "../components/OfferSection";
import MenuSection from "../components/MenuSection";
import Navbar from "../components/Navbar";
import Footer from "../components/Footer";
import "../assets/home/js/bootstrap.js";
import "../assets/home/js/custom.js";
import "../assets/home/js/jquery-3.4.1.min.js";
import "../assets/home/css/bootstrap.css";
import "../assets/home/css/font-awesome.min.css";
import "../assets/home/css/responsive.css";
import "../assets/home/css/style.css";
import "../assets/home/css/style.css.map";


const Home = () => {
  const [dishes, setDishes] = useState([]);
  const [categories, setCategories] = useState([]);
  const [selectedCategory, setSelectedCategory] = useState("all");

  useEffect(() => {
    fetch("http://localhost:8000/api/dishes/")
      .then((res) => res.json())
      .then((data) => setDishes(data));
    
    fetch("http://localhost:8000/api/categories/")
      .then((res) => res.json())
      .then((data) => setCategories(data));
  }, []);

  return (
    <div>
      <Navbar />
      <OfferSection />
      <MenuSection dishes={dishes} categories={categories} selectedCategory={selectedCategory} setSelectedCategory={setSelectedCategory} />
      <Footer />
    </div>
  );
};

export default Home;
