import React from "react";

const AboutSection = () => {
  return (
    <section className="about_section layout_padding">
      <div className="container">
        <div className="row">
          {/* Hình ảnh bên trái */}
          <div className="col-md-6">
            <div className="img-box">
              <img src="images/about-img.png" alt="About Us" />
            </div>
          </div>

          {/* Nội dung bên phải */}
          <div className="col-md-6">
            <div className="detail-box">
              <div className="heading_container">
                <h2>We Are Feane</h2>
              </div>
              <p>
                There are many variations of passages of Lorem Ipsum available,
                but the majority have suffered alteration in some form, by
                injected humour, or randomised words which don't look even
                slightly believable. If you are going to use a passage of Lorem
                Ipsum, you need to be sure there isn't anything embarrassing
                hidden in the middle of text.
              </p>
              <a href="#">Read More</a>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};

export default AboutSection;
