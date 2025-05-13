import React, { createContext, useState, useEffect, useContext } from "react";
import axios from 'axios';
import config from '../config';

export const AuthContext = createContext();

// Tạo hook useAuth để các component có thể sử dụng
export const useAuth = () => {
    const context = useContext(AuthContext);
    if (!context) {
        throw new Error('useAuth must be used within an AuthProvider');
    }
    return {
        authState: {
            user: context.user,
        },
        ...context
    };
};

export const AuthProvider = ({ children }) => {
    const [user, setUser] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        // Kiểm tra nếu có token trong localStorage thì tự động đăng nhập
        const token = localStorage.getItem("access_token");
        if (token) {
            // Lấy thông tin người dùng từ API
            axios.get(`${config.apiUrl}/user/me/`, {
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            })
            .then(response => {
                setUser(response.data);
            })
            .catch(error => {
                console.error("Error fetching user data:", error);
                localStorage.removeItem("access_token");
                localStorage.removeItem("refresh_token");
            })
            .finally(() => {
                setLoading(false);
            });
        } else {
            setLoading(false);
        }
    }, []);

    const login = (userData) => {
        setUser(userData);
    };

    const logout = () => {
        localStorage.removeItem("access_token");
        localStorage.removeItem("refresh_token");
        setUser(null);
    };

    return (
        <AuthContext.Provider value={{ user, login, logout, loading }}>
            {children}
        </AuthContext.Provider>
    );
};
