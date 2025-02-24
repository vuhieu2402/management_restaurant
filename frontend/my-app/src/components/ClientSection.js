import React from "react";
import Slider from "react-slick";
import "slick-carousel/slick/slick.css"; 
import "slick-carousel/slick/slick-theme.css";

const ClientSection = () => {
  const testimonials = [
    {
      id: 1,
      name: "Moana Michell",
      feedback:
        "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam.",
      position: "magna aliqua",
      image: "images/client1.jpg",
    },
    {
      id: 2,
      name: "Mike Hamell",
      feedback:
        "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam.",
      position: "magna aliqua",
      image: "images/client2.jpg",
    },
  ];

  const settings = {
    dots: true,
    infinite: true,
    speed: 500,
    slidesToShow: 1,
    slidesToScroll: 1,
    autoplay: true,
    autoplaySpeed: 3000,
  };

  return (
    <section className="client_section layout_padding-bottom">
      <div className="container">
        <div className="heading_container heading_center psudo_white_primary mb_45">
          <h2>What Says Our Customers</h2>
        </div>

        <div className="carousel-wrap row">
          <Slider {...settings} className="client_owl-carousel">
            {testimonials.map((testimonial) => (
              <div key={testimonial.id} className="item">
                <div className="box">
                  <div className="detail-box">
                    <p>{testimonial.feedback}</p>
                    <h6>{testimonial.name}</h6>
                    <p>{testimonial.position}</p>
                  </div>
                  <div className="img-box">
                    <img src={testimonial.image} alt={testimonial.name} className="box-img" />
                  </div>
                </div>
              </div>
            ))}
          </Slider>
        </div>
      </div>
    </section>
  );
};

export default ClientSection;
