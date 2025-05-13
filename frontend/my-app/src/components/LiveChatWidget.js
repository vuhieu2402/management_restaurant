import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import config from '../config';
import { useAuth } from '../context/AuthContext';
import { useNavigate } from 'react-router-dom';
import './LiveChatWidget.css';

const LiveChatWidget = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [chatRoom, setChatRoom] = useState(null);
  const [messages, setMessages] = useState([]);
  const [newMessage, setNewMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [socket, setSocket] = useState(null);
  const [unreadCount, setUnreadCount] = useState(0);
  const [socketStatus, setSocketStatus] = useState('disconnected'); // 'connected', 'disconnected', 'error'
  const messagesEndRef = useRef(null);
  const socketRef = useRef(null);
  const { authState } = useAuth();
  const navigate = useNavigate();

  // Kiểm tra xem người dùng đã đăng nhập chưa
  const isLoggedIn = !!authState.user;

  // Lấy thông tin phòng chat của người dùng
  useEffect(() => {
    if (!isLoggedIn || !isOpen) return;

    const fetchChatRoom = async () => {
      try {
        setIsLoading(true);
        // Tạo phòng chat mới hoặc lấy phòng hiện có
        const response = await axios.post(
          `${config.apiUrl}/live_chat/rooms/`,
          {}, // Không cần body
          {
            headers: {
              Authorization: `Bearer ${localStorage.getItem('access_token')}`
            }
          }
        );
        setChatRoom(response.data);

        // Lấy tin nhắn
        if (response.data.id) {
          const messagesResponse = await axios.get(
            `${config.apiUrl}/live_chat/rooms/${response.data.id}/`,
            {
              headers: {
                Authorization: `Bearer ${localStorage.getItem('access_token')}`
              }
            }
          );
          setMessages(messagesResponse.data.messages);
        }
      } catch (error) {
        console.error('Error fetching chat room:', error);
      } finally {
        setIsLoading(false);
      }
    };

    fetchChatRoom();
  }, [isLoggedIn, isOpen]);

  // Tạo và quản lý WebSocket connection
  useEffect(() => {
    // Chỉ tạo WebSocket khi cửa sổ chat đang mở và có chatRoom
    if (!isOpen || !chatRoom || !isLoggedIn) {
      if (socketRef.current) {
        socketRef.current.close();
        socketRef.current = null;
        setSocketStatus('disconnected');
      }
      return;
    }

    const connectWebSocket = () => {
      const token = localStorage.getItem('access_token');
      // Sửa lại đường dẫn để thử nhiều định dạng khác nhau (bỏ dấu / cuối)
      const wsUrl = `ws://${window.location.hostname}:8000/ws/chat/${chatRoom.id}?token=${token}`;
      
      if (socketRef.current && socketRef.current.readyState === WebSocket.OPEN) {
        console.log('WebSocket already connected');
        return;
      }
      
      console.log('Connecting to WebSocket:', wsUrl);
      const newSocket = new WebSocket(wsUrl);
      
      newSocket.onopen = () => {
        console.log('WebSocket connected successfully');
        setSocketStatus('connected');
        
        // Gửi heartbeat để giữ kết nối
        newSocket.send(JSON.stringify({
          type: 'connect',
          room_id: chatRoom.id
        }));
      };
      
      newSocket.onmessage = (event) => {
        const data = JSON.parse(event.data);
        console.log('WebSocket message received:', data);
        
        // Nếu là tin nhắn hệ thống, không hiển thị
        if (data.type === 'system') return;
        
        // Thêm tin nhắn mới vào danh sách tin nhắn
        setMessages(prevMessages => {
          // Kiểm tra trùng lặp
          const messageExists = prevMessages.some(msg => 
            msg.id === data.id || 
            (msg.content === data.message && 
             msg.user?.id === data.user_id &&
             msg.timestamp === data.timestamp)
          );
          
          if (messageExists) return prevMessages;
          
          // Thêm tin nhắn mới
          const newMsg = {
            id: data.id || Date.now(),
            content: data.message,
            user: {
              id: data.user_id,
              email: data.user_email,
              is_staff: data.is_staff
            },
            timestamp: data.timestamp,
            is_read: false
          };
          
          return [...prevMessages, newMsg];
        });
      };
      
      newSocket.onerror = (error) => {
        console.error('WebSocket error:', error);
        setSocketStatus('error');
      };
      
      newSocket.onclose = (event) => {
        console.log('WebSocket disconnected:', event.code, event.reason);
        setSocketStatus('disconnected');
        
        // Thử kết nối lại sau 5 giây nếu cửa sổ chat vẫn mở
        if (isOpen && chatRoom) {
          setTimeout(() => {
            connectWebSocket();
          }, 5000);
        }
      };
      
      socketRef.current = newSocket;
      setSocket(newSocket);
    };
    
    connectWebSocket();
    
    // Thiết lập heartbeat interval để giữ kết nối
    const heartbeatInterval = setInterval(() => {
      if (socketRef.current && socketRef.current.readyState === WebSocket.OPEN) {
        socketRef.current.send(JSON.stringify({ type: 'heartbeat' }));
      }
    }, 30000); // 30 giây
    
    return () => {
      clearInterval(heartbeatInterval);
      if (socketRef.current) {
        socketRef.current.close();
      }
    };
  }, [isOpen, chatRoom, isLoggedIn]);

  // Lấy số tin nhắn chưa đọc định kỳ
  useEffect(() => {
    if (!isLoggedIn) return;

    const fetchUnreadCount = async () => {
      try {
        const response = await axios.get(
          `${config.apiUrl}/live_chat/rooms/unread_count/`,
          {
            headers: {
              Authorization: `Bearer ${localStorage.getItem('access_token')}`
            }
          }
        );
        setUnreadCount(response.data.unread_count);
      } catch (error) {
        console.error('Error fetching unread count:', error);
      }
    };

    fetchUnreadCount();
    const interval = setInterval(fetchUnreadCount, 15000);
    return () => clearInterval(interval);
  }, [isLoggedIn]);

  // Cuộn xuống tin nhắn mới nhất
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const toggleChat = () => {
    if (!isLoggedIn) {
      navigate('/login');
      return;
    }
    setIsOpen(!isOpen);
    if (!isOpen) {
      // Reset unread count khi mở chat
      setUnreadCount(0);
    }
  };

  // Hàm gửi tin nhắn qua WebSocket
  const sendWebSocketMessage = (message) => {
    if (!socketRef.current || socketRef.current.readyState !== WebSocket.OPEN) {
      console.error('WebSocket not connected');
      return false;
    }
    
    try {
      socketRef.current.send(JSON.stringify({ message }));
      return true;
    } catch (error) {
      console.error('Error sending WebSocket message:', error);
      return false;
    }
  };

  const handleSendMessage = async (e) => {
    e.preventDefault();
    if (!newMessage.trim() || !chatRoom) return;

    try {
      // Thêm tin nhắn tạm vào danh sách ngay lập tức
      const tempMessage = {
        id: `temp-${Date.now()}`,
        content: newMessage,
        user: {
          id: authState.user.id,
          email: authState.user.email,
          is_staff: authState.user.is_staff || false
        },
        timestamp: new Date().toISOString(),
        is_read: false,
        temp: true
      };
      
      setMessages(prev => [...prev, tempMessage]);
      setNewMessage('');
      
      // Gửi tin nhắn qua WebSocket
      const sentViaWebSocket = sendWebSocketMessage(newMessage);
      
      // Nếu không gửi được qua WebSocket, dùng API
      if (!sentViaWebSocket) {
        // Fallback nếu WebSocket không hoạt động
        await axios.post(
          `${config.apiUrl}/live_chat/rooms/${chatRoom.id}/send_message/`,
          { message: newMessage },
          {
            headers: {
              Authorization: `Bearer ${localStorage.getItem('access_token')}`
            }
          }
        );
        
        // Refresh tin nhắn
        const response = await axios.get(
          `${config.apiUrl}/live_chat/rooms/${chatRoom.id}/`,
          {
            headers: {
              Authorization: `Bearer ${localStorage.getItem('access_token')}`
            }
          }
        );
        
        // Cập nhật danh sách tin nhắn, loại bỏ tin nhắn tạm
        setMessages(response.data.messages.filter(msg => !msg.temp));
      }
    } catch (error) {
      console.error('Error sending message:', error);
    }
  };

  // Xử lý phím Enter để gửi tin nhắn
  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage(e);
    }
  };

  const formatTime = (timestamp) => {
    const date = new Date(timestamp);
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  return (
    <div className="live-chat-widget">
      {/* Nút mở chat */}
      <button 
        className="chat-toggle-button livechat-toggle-button" 
        onClick={toggleChat}
      >
        {isOpen ? 'Đóng hỗ trợ' : 'Hỗ trợ'}
        {!isOpen && unreadCount > 0 && (
          <span className="unread-badge">{unreadCount}</span>
        )}
      </button>

      {/* Cửa sổ chat */}
      {isOpen && (
        <div className="chat-window">
          <div className="chat-header">
            <h3>Hỗ trợ trực tuyến</h3>
            {socketStatus === 'connected' ? (
              <span className="connection-status connected">●</span>
            ) : socketStatus === 'error' ? (
              <span className="connection-status error">●</span>
            ) : (
              <span className="connection-status disconnected">●</span>
            )}
            <button onClick={toggleChat}>×</button>
          </div>

          <div className="chat-messages">
            {isLoading ? (
              <div className="loading">Đang tải...</div>
            ) : messages.length === 0 ? (
              <div className="welcome-message">
                <p>Chào mừng bạn đến với hỗ trợ trực tuyến!</p>
                <p>Hãy đặt câu hỏi, chúng tôi sẽ phản hồi trong thời gian sớm nhất.</p>
              </div>
            ) : (
              messages.map(message => (
                <div 
                  key={message.id} 
                  className={`message ${message.user && message.user.is_staff ? 'staff' : 'customer'} ${message.temp ? 'temp' : ''}`}
                >
                  <div className="message-content">{message.content}</div>
                  <div className="message-info">
                    <span className="sender">{message.user && message.user.is_staff ? 'Nhân viên' : 'Bạn'}</span>
                    <span className="time">{formatTime(message.timestamp)}</span>
                  </div>
                </div>
              ))
            )}
            <div ref={messagesEndRef} />
          </div>

          <form className="chat-input" onSubmit={handleSendMessage}>
            <input
              type="text"
              value={newMessage}
              onChange={(e) => setNewMessage(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Nhập câu hỏi của bạn..."
              disabled={isLoading}
            />
            <button 
              type="submit" 
              disabled={isLoading || socketStatus !== 'connected' || !newMessage.trim()}
            >
              Gửi
            </button>
          </form>
        </div>
      )}
    </div>
  );
};

export default LiveChatWidget; 