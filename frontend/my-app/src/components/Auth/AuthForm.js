import React, { useState, useContext } from "react";
import axios from "axios";
import { useNavigate } from "react-router-dom"; // Import useNavigate
import { AuthContext } from "../../context/AuthContext"; // Import AuthContext
import "./auth.css";

const AuthForm = ({ isLogin, toggleForm }) => {
    const { login } = useContext(AuthContext); // Dùng context để cập nhật trạng thái đăng nhập
    const navigate = useNavigate(); // Hook để điều hướng
    const [formData, setFormData] = useState({
        email: "",
        password: "",
        user_name: "",
    });
    const [error, setError] = useState("");

    const handleChange = (e) => {
        setFormData({ ...formData, [e.target.name]: e.target.value });
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError("");

        const url = isLogin
            ? "http://127.0.0.1:8000/api/token/" // API login
            : "http://127.0.0.1:8000/api/user/register/"; // API register

        try {
            const response = await axios.post(url, formData);

            if (isLogin) {
                localStorage.setItem("access_token", response.data.access);
                localStorage.setItem("refresh_token", response.data.refresh);

                // Gọi API lấy thông tin user chi tiết
                const userInfoRes = await axios.get("http://127.0.0.1:8000/api/user/me/", {
                    headers: { Authorization: `Bearer ${response.data.access}` }
                });
                const userData = userInfoRes.data;
                login(userData);

                alert("Login successful!");

                // Chuyển hướng theo quyền
                if (userData.is_superuser) {
                    window.location.href = "/admin";
                } else if (userData.is_staff) {
                    navigate("/manager");
                } else if (userData.is_active) {
                    navigate("/");
                } else {
                    alert("Tài khoản không hợp lệ!");
                }
            } else {
                alert("Register successful! You can now log in.");
                toggleForm(); // Chuyển sang form đăng nhập
            }
        } catch (error) {
            setError("Something went wrong. Please try again.");
        }
    };

    return (
        <div className="auth-container">
            <form onSubmit={handleSubmit}>
                <h1>{isLogin ? "Sign In" : "Sign Up"}</h1>
                {!isLogin && (
                    <input
                        type="text"
                        name="user_name"
                        placeholder="Username"
                        value={formData.user_name}
                        onChange={handleChange}
                        required
                    />
                )}
                <input
                    type="email"
                    name="email"
                    placeholder="Email"
                    value={formData.email}
                    onChange={handleChange}
                    required
                />
                <input
                    type="password"
                    name="password"
                    placeholder="Password"
                    value={formData.password}
                    onChange={handleChange}
                    required
                />
                {error && <p className="error">{error}</p>}
                <button type="submit">{isLogin ? "Sign In" : "Sign Up"}</button>

                {isLogin && (
                    <p>
                        <button 
                            type="button" 
                            className="forgot-password-btn" 
                            onClick={() => navigate("/forgot-password")}
                        >
                            Forgot Password?
                        </button>
                    </p>
                )}

                <p>
                    {isLogin ? "Don't have an account?" : "Already have an account?"}
                    <button type="button" className="toggle-btn" onClick={toggleForm}>
                        {isLogin ? "Sign Up" : "Sign In"}
                    </button>
                </p>
            </form>
        </div>
    );
};

export default AuthForm;
