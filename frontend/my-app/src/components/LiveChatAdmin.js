import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import config from '../config';
import { useAuth } from '../context/AuthContext';
import './LiveChatAdmin.css';

const LiveChatAdmin = () => {
  const [chatRooms, setChatRooms] = useState([]);
  const [selectedRoom, setSelectedRoom] = useState(null);
  const [messages, setMessages] = useState([]);
  const [newMessage, setNewMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [socket, setSocket] = useState(null);
  const [socketStatus, setSocketStatus] = useState('disconnected'); // 'connected', 'disconnected', 'error'
  const messagesEndRef = useRef(null);
  const socketRef = useRef(null);
  const { authState, loading } = useAuth();

  // Kiểm tra xem người dùng có phải là quản lý không
  const isManager = authState.user && authState.user.is_staff;

  // Lấy danh sách phòng chat
  useEffect(() => {
    if (!isManager) return;

    const fetchChatRooms = async () => {
      try {
        setIsLoading(true);
        const response = await axios.get(
          `${config.apiUrl}/live_chat/rooms/`,
          {
            headers: {
              Authorization: `Bearer ${localStorage.getItem('access_token')}`
            }
          }
        );
        setChatRooms(response.data);
      } catch (error) {
        console.error('Error fetching chat rooms:', error);
      } finally {
        setIsLoading(false);
      }
    };

    fetchChatRooms();
    // Thiết lập interval để cập nhật danh sách phòng chat mỗi 15 giây
    const interval = setInterval(fetchChatRooms, 15000);
    return () => clearInterval(interval);
  }, [isManager]);

  // Tạo và quản lý WebSocket connection khi chọn phòng chat
  useEffect(() => {
    if (!selectedRoom || !isManager) {
      // Đóng socket hiện tại nếu có
      if (socketRef.current) {
        socketRef.current.close();
        socketRef.current = null;
        setSocketStatus('disconnected');
      }
      return;
    }

    // Lấy tin nhắn của phòng chat
    const fetchMessages = async () => {
      try {
        setIsLoading(true);
        const response = await axios.get(
          `${config.apiUrl}/live_chat/rooms/${selectedRoom.id}/`,
          {
            headers: {
              Authorization: `Bearer ${localStorage.getItem('access_token')}`
            }
          }
        );
        setMessages(response.data.messages);
      } catch (error) {
        console.error('Error fetching messages:', error);
      } finally {
        setIsLoading(false);
      }
    };

    fetchMessages();

    // Hàm thiết lập WebSocket connection
    const connectWebSocket = () => {
      const token = localStorage.getItem('access_token');
      // Sửa lại đường dẫn để đảm bảo kết nối thành công
      const wsUrl = `ws://${window.location.hostname}:8000/ws/chat/${selectedRoom.id}?token=${token}`;
      
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
          room_id: selectedRoom.id
        }));
      };
      
      newSocket.onmessage = (event) => {
        const data = JSON.parse(event.data);
        console.log('Admin WebSocket message received:', data);
        
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
        
        // Cập nhật danh sách phòng chat để hiển thị tin nhắn mới
        fetchChatRooms();
      };
      
      newSocket.onerror = (error) => {
        console.error('WebSocket error:', error);
        setSocketStatus('error');
      };
      
      newSocket.onclose = (event) => {
        console.log('WebSocket disconnected:', event.code, event.reason);
        setSocketStatus('disconnected');
        
        // Thử kết nối lại sau 5 giây nếu phòng vẫn được chọn
        if (selectedRoom) {
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
    
    // Cleanup
    return () => {
      clearInterval(heartbeatInterval);
      if (socketRef.current) {
        socketRef.current.close();
        socketRef.current = null;
      }
    };
  }, [selectedRoom, isManager]);

  // Cuộn xuống tin nhắn mới nhất
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

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
    if (!newMessage.trim() || !selectedRoom) return;

    try {
      // Thêm tin nhắn tạm vào danh sách ngay lập tức
      const tempMessage = {
        id: `temp-${Date.now()}`,
        content: newMessage,
        user: {
          id: authState.user.id,
          email: authState.user.email,
          is_staff: true
        },
        timestamp: new Date().toISOString(),
        is_read: true,
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
          `${config.apiUrl}/live_chat/rooms/${selectedRoom.id}/send_message/`,
          { message: newMessage },
          {
            headers: {
              Authorization: `Bearer ${localStorage.getItem('access_token')}`
            }
          }
        );
        
        // Refresh tin nhắn
        const response = await axios.get(
          `${config.apiUrl}/live_chat/rooms/${selectedRoom.id}/`,
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

  const formatDate = (timestamp) => {
    const date = new Date(timestamp);
    return date.toLocaleDateString();
  };

  // Hiển thị loading trong khi kiểm tra quyền
  if (loading) {
    return <div className="loading-message">Đang tải thông tin người dùng...</div>;
  }

  // Hiển thị thông báo nếu không có quyền
  if (!isManager) {
    return (
      <div className="unauthorized-message">
        <h2>Bạn không có quyền truy cập trang này</h2>
        <p>Tính năng này chỉ dành cho quản lý. Vui lòng đăng nhập với tài khoản quản lý để tiếp tục.</p>
        <button 
          onClick={() => window.location.href = '/'}
          style={{ padding: '8px 16px', background: '#3498db', color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer', marginTop: '20px' }}
        >
          Quay lại trang chủ
        </button>
      </div>
    );
  }

  // Hàm tìm phòng chat cần cập nhật khi nhận tin nhắn mới
  const fetchChatRooms = async () => {
    try {
      const response = await axios.get(
        `${config.apiUrl}/live_chat/rooms/`,
        {
          headers: {
            Authorization: `Bearer ${localStorage.getItem('access_token')}`
          }
        }
      );
      setChatRooms(response.data);
    } catch (error) {
      console.error('Error fetching chat rooms:', error);
    }
  };

  return (
    <div className="live-chat-admin">
      <div className="chat-container">
        <div className="chat-rooms-list">
          <h2>Cuộc trò chuyện</h2>
          {isLoading && chatRooms.length === 0 ? (
            <div className="loading">Đang tải...</div>
          ) : (
            <ul>
              {chatRooms.map(room => (
                <li 
                  key={room.id} 
                  className={selectedRoom && selectedRoom.id === room.id ? 'active' : ''}
                  onClick={() => setSelectedRoom(room)}
                >
                  <div className="room-info">
                    <h4>{room.customer.user_name || room.customer.email}</h4>
                    <span className="timestamp">{formatDate(room.updated_at)}</span>
                  </div>
                  {room.latest_message && (
                    <p className="latest-message">{room.latest_message.content}</p>
                  )}
                  {room.unread_count > 0 && (
                    <span className="unread-badge">{room.unread_count}</span>
                  )}
                </li>
              ))}
              {chatRooms.length === 0 && !isLoading && (
                <li className="no-rooms">Không có cuộc trò chuyện nào.</li>
              )}
            </ul>
          )}
        </div>

        <div className="chat-messages-container">
          {selectedRoom ? (
            <>
              <div className="chat-header">
                <h3>Cuộc trò chuyện với {selectedRoom.customer.user_name || selectedRoom.customer.email}</h3>
                {socketStatus === 'connected' ? (
                  <span className="connection-status connected" title="Kết nối thành công">●</span>
                ) : socketStatus === 'error' ? (
                  <span className="connection-status error" title="Lỗi kết nối">●</span>
                ) : (
                  <span className="connection-status disconnected" title="Mất kết nối">●</span>
                )}
              </div>

              <div className="chat-messages">
                {messages.length === 0 ? (
                  <div className="no-messages">Chưa có tin nhắn nào.</div>
                ) : (
                  messages.map(message => (
                    <div 
                      key={message.id} 
                      className={`message ${message.user.is_staff ? 'staff' : 'customer'} ${message.temp ? 'temp' : ''}`}
                    >
                      <div className="message-content">{message.content}</div>
                      <div className="message-info">
                        <span className="sender">{message.user.is_staff ? 'Quản lý' : 'Khách hàng'}</span>
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
                  placeholder="Nhập tin nhắn..."
                />
                <button 
                  type="submit" 
                  disabled={socketStatus !== 'connected' || !newMessage.trim()}
                >
                  Gửi
                </button>
              </form>
            </>
          ) : (
            <div className="select-room-prompt">
              <h3>Chọn một cuộc trò chuyện để bắt đầu</h3>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default LiveChatAdmin; 