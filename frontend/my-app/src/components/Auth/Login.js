import React, { useState } from "react";
import AuthForm from "./AuthForm";

const Login = () => {
    const [isLogin, setIsLogin] = useState(true);

    const toggleForm = () => {
        setIsLogin(!isLogin);
    };

    return (
        <div className={`container ${!isLogin ? "right-panel-active" : ""}`}>
            <AuthForm isLogin={isLogin} toggleForm={toggleForm} />
        </div>
    );
};

export default Login;
