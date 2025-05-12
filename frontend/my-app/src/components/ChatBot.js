import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import config from '../config';
import { useNavigate } from 'react-router-dom';
import './ChatBot.css';

const ChatBot = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState([]);
  const [newMessage, setNewMessage] = useState('');
  const [sessionId, setSessionId] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [recommendations, setRecommendations] = useState([]);
  const messagesEndRef = useRef(null);
  const navigate = useNavigate();

  // Lấy session ID từ localStorage nếu có
  useEffect(() => {
    const savedSessionId = localStorage.getItem('chatbot_session_id');
    if (savedSessionId) {
      setSessionId(savedSessionId);
      
      // Tải lịch sử chat nếu đã đăng nhập
      const token = localStorage.getItem('access_token');
      if (token) {
        fetchChatHistory(savedSessionId);
      } else {
        // Thêm tin nhắn chào mừng nếu là phiên mới
        setMessages([
          { 
            id: 'welcome', 
            content: 'Xin chào! Tôi là trợ lý ảo của nhà hàng. Tôi có thể giúp gì cho bạn hôm nay? Tôi có thể đề xuất món ăn dựa trên sở thích của bạn.', 
            sender: 'bot' 
          }
        ]);
      }
    } else {
      // Thêm tin nhắn chào mừng cho người dùng mới
      setMessages([
        { 
          id: 'welcome', 
          content: 'Xin chào! Tôi là trợ lý ảo của nhà hàng. Tôi có thể giúp gì cho bạn hôm nay? Tôi có thể đề xuất món ăn dựa trên sở thích của bạn.', 
          sender: 'bot' 
        }
      ]);
    }
  }, []);

  // Cuộn xuống tin nhắn mới nhất
  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const fetchChatHistory = async (sid) => {
    try {
      const token = localStorage.getItem('access_token');
      if (!token) return;

      const response = await axios.get(
        `${config.apiUrl}/chatbot/conversations/${sid}/`,
        { headers: { Authorization: `Bearer ${token}` } }
      );

      if (response.data && response.data.messages) {
        setMessages(response.data.messages.map(msg => ({
          id: msg.id,
          content: msg.content,
          sender: msg.sender
        })));

        // Lấy đề xuất gần đây nhất nếu có
        if (response.data.recommendations && response.data.recommendations.length > 0) {
          setRecommendations(response.data.recommendations);
        }
      }
    } catch (error) {
      console.error('Error fetching chat history:', error);
    }
  };

  const toggleChat = () => {
    setIsOpen(!isOpen);
  };

  const handleSendMessage = async (e) => {
    e.preventDefault();
    if (!newMessage.trim()) return;

    // Thêm tin nhắn của người dùng vào giao diện
    const userMessage = {
      id: Date.now(),
      content: newMessage,
      sender: 'user'
    };
    setMessages(prevMessages => [...prevMessages, userMessage]);
    setNewMessage('');
    setIsLoading(true);

    try {
      // Gọi API chatbot
      const response = await axios.post(`${config.apiUrl}/chatbot/chat/`, {
        message: newMessage,
        session_id: sessionId
      });

      // Lưu session ID
      if (response.data.session_id) {
        setSessionId(response.data.session_id);
        localStorage.setItem('chatbot_session_id', response.data.session_id);
      }

      // Thêm phản hồi từ bot
      const botMessage = {
        id: Date.now() + 1,
        content: response.data.message,
        sender: 'bot'
      };
      setMessages(prevMessages => [...prevMessages, botMessage]);

      // Cập nhật đề xuất món ăn nếu có
      if (response.data.recommendations && response.data.recommendations.length > 0) {
        setRecommendations(response.data.recommendations);
      }
    } catch (error) {
      console.error('Error sending message to chatbot:', error);
      // Thêm thông báo lỗi
      setMessages(prevMessages => [
        ...prevMessages,
        {
          id: Date.now() + 1,
          content: 'Xin lỗi, tôi đang gặp vấn đề kỹ thuật. Vui lòng thử lại sau.',
          sender: 'bot'
        }
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleAddToCart = async (dishId) => {
    try {
      const token = localStorage.getItem('access_token');
      if (!token) {
        // Chuyển hướng đến trang đăng nhập nếu không có token
        navigate('/login');
        return;
      }

      // Thêm thông báo đang xử lý
      const processingMessage = {
        id: Date.now(),
        content: 'Đang thêm món ăn vào giỏ hàng...',
        sender: 'bot'
      };
      setMessages(prevMessages => [...prevMessages, processingMessage]);

      try {
        // Thử gửi yêu cầu với token hiện tại
        await axios.post(
          `${config.apiUrl}/cart/add_to_cart/`,
          { dish_id: dishId, quantity: 1 },
          { headers: { Authorization: `Bearer ${token}` } }
        );
      } catch (error) {
        // Nếu lỗi 401, thử refresh token
        if (error.response && error.response.status === 401) {
          const refreshToken = localStorage.getItem('refresh_token');
          
          if (refreshToken) {
            try {
              // Gọi API refresh token
              const refreshResponse = await axios.post(
                `${config.apiUrl}/token/refresh/`,
                { refresh: refreshToken }
              );
              
              // Lưu token mới
              const newToken = refreshResponse.data.access;
              localStorage.setItem('access_token', newToken);
              
              // Thử lại request với token mới
              await axios.post(
                `${config.apiUrl}/cart/add_to_cart/`,
                { dish_id: dishId, quantity: 1 },
                { headers: { Authorization: `Bearer ${newToken}` } }
              );
            } catch (refreshError) {
              // Nếu refresh token cũng hết hạn, chuyển hướng về trang đăng nhập
              console.error('Token refresh failed:', refreshError);
              localStorage.removeItem('access_token');
              localStorage.removeItem('refresh_token');
              navigate('/login');
              throw new Error('Phiên đăng nhập hết hạn. Vui lòng đăng nhập lại.');
            }
          } else {
            // Không có refresh token, chuyển hướng về trang đăng nhập
            localStorage.removeItem('access_token');
            navigate('/login');
            throw new Error('Bạn cần đăng nhập để thêm món ăn vào giỏ hàng.');
          }
        } else {
          // Lỗi khác, ném lại để xử lý ở catch bên ngoài
          throw error;
        }
      }

      // Cập nhật phản hồi về đề xuất
      const recommendationId = recommendations.find(rec => rec.dish.id === dishId)?.id;
      if (recommendationId) {
        await axios.post(
          `${config.apiUrl}/chatbot/recommendations/${recommendationId}/feedback/`,
          { accepted: true }
        );
      }

      // Xóa thông báo đang xử lý và thêm thông báo thành công
      setMessages(prevMessages => 
        prevMessages.filter(msg => msg.id !== processingMessage.id).concat({
          id: Date.now(),
          content: 'Món ăn đã được thêm vào giỏ hàng của bạn.',
          sender: 'bot'
        })
      );

    } catch (error) {
      console.error('Error adding to cart:', error);
      // Hiển thị thông báo lỗi cụ thể hơn
      const errorMessage = {
        id: Date.now(),
        content: error.message || 'Không thể thêm món ăn vào giỏ hàng. Vui lòng thử lại hoặc đăng nhập lại.',
        sender: 'bot'
      };
      // Xóa thông báo đang xử lý nếu có
      setMessages(prevMessages => 
        prevMessages.filter(msg => !msg.content.includes('Đang thêm món ăn')).concat(errorMessage)
      );
    }
  };

  const handleReject = async (dishId) => {
    try {
      // Cập nhật phản hồi về đề xuất
      const recommendationId = recommendations.find(rec => rec.dish.id === dishId)?.id;
      if (recommendationId) {
        await axios.post(
          `${config.apiUrl}/chatbot/recommendations/${recommendationId}/feedback/`,
          { accepted: false }
        );
      }

      // Thông báo từ chối
      const rejectMessage = {
        id: Date.now(),
        content: 'Không vấn đề! Hãy cho tôi biết nếu bạn muốn đề xuất món khác.',
        sender: 'bot'
      };
      setMessages(prevMessages => [...prevMessages, rejectMessage]);

      // Xóa món này khỏi danh sách đề xuất
      setRecommendations(prev => prev.filter(rec => rec.dish.id !== dishId));

    } catch (error) {
      console.error('Error rejecting recommendation:', error);
    }
  };

  return (
    <div className="chatbot-container">
      {/* Nút mở chatbot */}
      <button className="chat-toggle-button" onClick={toggleChat}>
        {isOpen ? 'Đóng chat' : 'Trợ lý AI'}
      </button>

      {/* Cửa sổ chatbot */}
      {isOpen && (
        <div className="chat-window">
          <div className="chat-header">
            <h3>Trợ lý nhà hàng</h3>
            <button onClick={toggleChat}>×</button>
          </div>

          <div className="chat-messages">
            {messages.map(message => (
              <div key={message.id} className={`message ${message.sender}`}>
                {message.content}
              </div>
            ))}
            {isLoading && (
              <div className="message bot loading">
                <div className="typing-indicator">
                  <span></span>
                  <span></span>
                  <span></span>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          {/* Hiển thị đề xuất món ăn */}
          {recommendations.length > 0 && (
            <div className="recommendations-container">
              <h4>Món ăn đề xuất cho bạn:</h4>
              <div className="recommendations-list">
                {recommendations.map(rec => (
                  <div key={rec.id} className="recommendation-item">
                    <div className="recommendation-details">
                      <h5>{rec.dish.name}</h5>
                      <p>{rec.dish.description.substring(0, 100)}...</p>
                      <p className="price">{rec.dish.price}đ</p>
                      {rec.reasoning && <p className="reasoning">{rec.reasoning}</p>}
                    </div>
                    <div className="recommendation-actions">
                      <button onClick={() => handleAddToCart(rec.dish.id)}>
                        Thêm vào giỏ
                      </button>
                      <button onClick={() => handleReject(rec.dish.id)} className="reject-btn">
                        Không, cảm ơn
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          <form className="chat-input" onSubmit={handleSendMessage}>
            <input
              type="text"
              value={newMessage}
              onChange={(e) => setNewMessage(e.target.value)}
              placeholder="Nhập tin nhắn..."
              disabled={isLoading}
            />
            <button type="submit" disabled={isLoading}>Gửi</button>
          </form>
        </div>
      )}
    </div>
  );
};

export default ChatBot; 