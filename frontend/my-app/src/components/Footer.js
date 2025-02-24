import React from "react";

const Footer = () => {
  return (
    <footer className="footer_section">
      <div className="container">
        <div className="row">
          {/* Cột 1: Thông tin liên hệ */}
          <div className="col-md-4 footer-col">
            <div className="footer_contact">
              <h4>Contact Us</h4>
              <div className="contact_link_box">
                <a href="#">
                  <i className="fa fa-map-marker" aria-hidden="true"></i>
                  <span>Location</span>
                </a>
                <a href="tel:+011234567890">
                  <i className="fa fa-phone" aria-hidden="true"></i>
                  <span>Call +01 1234567890</span>
                </a>
                <a href="mailto:demo@gmail.com">
                  <i className="fa fa-envelope" aria-hidden="true"></i>
                  <span>demo@gmail.com</span>
                </a>
              </div>
            </div>
          </div>

          {/* Cột 2: Logo & Social */}
          <div className="col-md-4 footer-col">
            <div className="footer_detail">
              <a href="#" className="footer-logo">
                Feane
              </a>
              <p>
                Necessary, making this the first true generator on the Internet. It uses a dictionary of over 200 Latin words, combined with.
              </p>
              <div className="footer_social">
                <a href="#">
                  <i className="fa fa-facebook" aria-hidden="true"></i>
                </a>
                <a href="#">
                  <i className="fa fa-twitter" aria-hidden="true"></i>
                </a>
                <a href="#">
                  <i className="fa fa-linkedin" aria-hidden="true"></i>
                </a>
                <a href="#">
                  <i className="fa fa-instagram" aria-hidden="true"></i>
                </a>
                <a href="#">
                  <i className="fa fa-pinterest" aria-hidden="true"></i>
                </a>
              </div>
            </div>
          </div>

          {/* Cột 3: Giờ mở cửa */}
          <div className="col-md-4 footer-col">
            <h4>Opening Hours</h4>
            <p>Everyday</p>
            <p>10.00 AM - 10.00 PM</p>
          </div>
        </div>

        {/* Thông tin bản quyền */}
        <div className="footer-info">
          <p>
            &copy; {new Date().getFullYear()} All Rights Reserved By
            <a href="https://html.design/" target="_blank" rel="noopener noreferrer"> Free Html Templates</a>
            <br /><br />
            &copy; {new Date().getFullYear()} Distributed By
            <a href="https://themewagon.com/" target="_blank" rel="noopener noreferrer"> ThemeWagon</a>
          </p>
        </div>
      </div>
    </footer>
  );
};

export default Footer;
