import React from "react";
import { Link } from "react-router-dom";
import BookTable from "./BookTable";

const BookSection = () => {
  return (
    <section className="book_section layout_padding">
      <div className="container">
        {/* Tiêu đề */}
        <div className="heading_container">
          <h2>Book A Table</h2>
        </div>

        <div className="row">
          {/* Form đặt bàn */}
          <div className="col-md-6">
            <BookTable isHomePage={true} />
          </div>

          {/* Bản đồ */}
          <div className="col-md-6">
            <div className="map_container">
              <div id="googleMap">
                {/* Bạn có thể nhúng Google Map API tại đây */}
                <iframe
                  title="Google Map"
                  width="100%"
                  height="300"
                  frameBorder="0"
                  style={{ border: 0 }}
                  src="https://www.google.com/maps/embed/v1/place?key=YOUR_GOOGLE_MAPS_API_KEY&q=New+York"
                  allowFullScreen
                ></iframe>
              </div>
            </div>
            <div className="text-center mt-4">
              <Link to="/book-table" className="btn btn-primary">
                Đặt Bàn Chi Tiết
              </Link>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};

export default BookSection;
