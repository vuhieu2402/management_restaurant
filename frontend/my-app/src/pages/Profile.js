import React, { useContext, useState } from "react";
import { AuthContext } from "../context/AuthContext";

const Profile = () => {
  const { user, updateUser } = useContext(AuthContext);
  const [formData, setFormData] = useState({
    name: user?.name || "",
    email: user?.email || "",
    // Thêm các trường khác nếu cần
  });
  const [editing, setEditing] = useState(false);
  const [message, setMessage] = useState("");

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    // Gọi API backend để cập nhật thông tin người dùng nếu có
    try {
      await updateUser(formData); // updateUser nên được định nghĩa trong AuthContext
      setMessage("Cập nhật thành công!");
      setEditing(false);
    } catch (error) {
      setMessage("Có lỗi xảy ra khi cập nhật.");
    }
  };

  if (!user) return <div>Bạn cần đăng nhập để xem thông tin cá nhân.</div>;

  return (
    <div className="container mt-5">
      <h2>Thông tin cá nhân</h2>
      {message && <div className="alert alert-info">{message}</div>}
      {!editing ? (
        <div>
          <p><strong>Tên:</strong> {user.name}</p>
          <p><strong>Email:</strong> {user.email}</p>
          {/* Thêm các trường khác nếu cần */}
          <button className="btn btn-primary" onClick={() => setEditing(true)}>
            Chỉnh sửa thông tin
          </button>
        </div>
      ) : (
        <form onSubmit={handleSubmit} style={{ maxWidth: 400 }}>
          <div className="form-group">
            <label>Tên</label>
            <input type="text" className="form-control" name="name" value={formData.name} onChange={handleChange} required />
          </div>
          <div className="form-group">
            <label>Email</label>
            <input type="email" className="form-control" name="email" value={formData.email} onChange={handleChange} required />
          </div>
          {/* Thêm các trường khác nếu cần */}
          <button className="btn btn-success mt-2" type="submit">Lưu</button>
          <button className="btn btn-secondary mt-2 ml-2" type="button" onClick={() => setEditing(false)}>Hủy</button>
        </form>
      )}
    </div>
  );
};

export default Profile;
