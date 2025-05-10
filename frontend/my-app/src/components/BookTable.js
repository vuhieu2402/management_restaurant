import React, { useState, useContext } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';
import { AuthContext } from '../context/AuthContext';
import './BookTable.css';

const BookTable = ({ isHomePage = false }) => {
    const navigate = useNavigate();
    const { user, token } = useContext(AuthContext);
    const [formData, setFormData] = useState({
        name: '',
        phone_number: '',
        table_number: '',
        reservation_date: '',
        time: ''
    });
    const [error, setError] = useState('');
    const [success, setSuccess] = useState('');

    const handleChange = (e) => {
        setFormData({
            ...formData,
            [e.target.name]: e.target.value
        });
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');
        setSuccess('');

        try {
            await axios.post(
                'http://localhost:8000/api/reserve/',
                formData,
                {
                    headers: {
                        'Authorization': `Bearer ${token}`,
                        'Content-Type': 'application/json'
                    }
                }
            );
            setSuccess('Đặt bàn thành công!');
            setFormData({
                name: '',
                phone_number: '',
                table_number: '',
                reservation_date: '',
                time: ''
            });
            
            if (!isHomePage) {
                setTimeout(() => {
                    navigate('/');
                }, 2000);
            }
        } catch (err) {
            setError(err.response?.data?.message || 'Có lỗi xảy ra khi đặt bàn');
        }
    };

    if (!user) {
        return (
            <div className="book-table-container">
                <p>Vui lòng đăng nhập để đặt bàn</p>
                <button onClick={() => navigate('/auth')}>Đăng nhập</button>
            </div>
        );
    }

    return (
        <div className={`book-table-container ${isHomePage ? 'home-page' : ''}`}>
            <h2>{isHomePage ? 'Đặt Bàn Ngay' : 'Đặt Bàn'}</h2>
            <form onSubmit={handleSubmit} className="book-table-form">
                <div className="form-group">
                    <input
                        type="text"
                        name="name"
                        value={formData.name}
                        onChange={handleChange}
                        placeholder="Họ và tên"
                        required
                    />
                </div>
                <div className="form-group">
                    <input
                        type="tel"
                        name="phone_number"
                        value={formData.phone_number}
                        onChange={handleChange}
                        placeholder="Số điện thoại"
                        required
                    />
                </div>
                <div className="form-group">
                    <input
                        type="number"
                        name="table_number"
                        value={formData.table_number}
                        onChange={handleChange}
                        placeholder="Số bàn"
                        required
                    />
                </div>
                <div className="form-group">
                    <input
                        type="date"
                        name="reservation_date"
                        value={formData.reservation_date}
                        onChange={handleChange}
                        required
                    />
                </div>
                <div className="form-group">
                    <input
                        type="time"
                        name="time"
                        value={formData.time}
                        onChange={handleChange}
                        required
                    />
                </div>
                <button type="submit" className="submit-btn">Đặt Bàn</button>
            </form>
            {error && <p className="error-message">{error}</p>}
            {success && <p className="success-message">{success}</p>}
        </div>
    );
};

export default BookTable; 