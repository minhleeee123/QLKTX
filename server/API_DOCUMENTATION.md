# API Documentation - Hệ thống Quản lý Ký túc xá (QLKTX)

## Tổng quan
REST API cho hệ thống quản lý ký túc xá với authentication JWT.

Base URL: `http://localhost:5000/api`

## Authentication
Tất cả endpoints (trừ login, register) đều yêu cầu JWT token trong header:
```
Authorization: Bearer <token>
```

---

## 🔐 Authentication Endpoints

### POST /api/auth/login
Đăng nhập và nhận JWT token

**Request:**
```json
{
  "email": "admin@qlktx.edu.vn",
  "password": "admin123"
}
```

**Response:**
```json
{
  "access_token": "eyJ0eXAi...",
  "user": {
    "user_id": 1,
    "full_name": "Nguyễn Văn Admin",
    "email": "admin@qlktx.edu.vn",
    "role": "Admin",
    "student_id": null
  }
}
```

### POST /api/auth/register
Đăng ký tài khoản sinh viên mới

**Request:**
```json
{
  "full_name": "Nguyễn Văn A",
  "email": "student@student.edu.vn",
  "password": "password123",
  "student_id": "SV006",
  "phone_number": "0901234567"
}
```

### GET /api/auth/me
Lấy thông tin user hiện tại

---

## 👥 Users Endpoints

### GET /api/users
Lấy danh sách users (Admin/Management only)

**Query Parameters:**
- `page`: Trang (default: 1)
- `per_page`: Số items/trang (default: 10)
- `role`: Filter theo role
- `search`: Tìm kiếm theo tên/email/mã SV

### GET /api/users/{user_id}
Lấy thông tin chi tiết user

### POST /api/users
Tạo user mới (Admin/Management only)

### PUT /api/users/{user_id}
Cập nhật thông tin user

### DELETE /api/users/{user_id}
Xóa user (Admin only)

---

## 🏠 Rooms Endpoints

### GET /api/rooms
Lấy danh sách phòng

**Query Parameters:**
- `page`, `per_page`: Phân trang
- `building_id`: Filter theo tòa nhà
- `room_type_id`: Filter theo loại phòng
- `status`: Filter theo trạng thái
- `search`: Tìm kiếm theo số phòng

### GET /api/rooms/{room_id}
Lấy thông tin chi tiết phòng

### POST /api/rooms
Tạo phòng mới (Admin/Management only)

### PUT /api/rooms/{room_id}
Cập nhật thông tin phòng (Admin/Management only)

### DELETE /api/rooms/{room_id}
Xóa phòng (Admin only)

**Response Success:**
```json
{
  "success": true,
  "message": "Xóa phòng thành công",
  "data": null,
  "status_code": 200
}
```

**Response Error (Room in use):**
```json
{
  "success": false,
  "message": "Không thể xóa phòng đang được sử dụng",
  "data": null,
  "status_code": 400
}
```

### GET /api/rooms/buildings
Lấy danh sách tòa nhà

### GET /api/rooms/room-types
Lấy danh sách loại phòng

---

## 📝 Registrations Endpoints

### GET /api/registrations
Lấy danh sách đơn đăng ký
- Student: Chỉ xem đơn của mình
- Admin/Management: Xem tất cả

### POST /api/registrations
Tạo đơn đăng ký mới (Student only)

**Request:**
```json
{
  "room_id": 1
}
```

### POST /api/registrations/{registration_id}/approve
Duyệt đơn đăng ký (Admin/Management only)

### POST /api/registrations/{registration_id}/reject
Từ chối đơn đăng ký (Admin/Management only)

### DELETE /api/registrations/{registration_id}
Hủy đơn đăng ký

---

## 📋 Contracts Endpoints

### GET /api/contracts
Lấy danh sách hợp đồng

### GET /api/contracts/{contract_id}
Lấy thông tin chi tiết hợp đồng

### PUT /api/contracts/{contract_id}
Cập nhật hợp đồng (Admin/Management only)

### GET /api/contracts/statistics
Thống kê hợp đồng (Admin/Management only)

---

## 💰 Payments Endpoints

### GET /api/payments
Lấy danh sách thanh toán

### POST /api/payments
Tạo thanh toán mới (Student only)

**Request:**
```json
{
  "contract_id": 1,
  "amount": 1200000,
  "payment_method": "bank_transfer",
  "proof_image_url": "https://example.com/proof.jpg"
}
```

### POST /api/payments/{payment_id}/confirm
Xác nhận thanh toán (Admin/Management only)

### POST /api/payments/{payment_id}/reject
Từ chối thanh toán (Admin/Management only)

### PUT /api/payments/{payment_id}
Cập nhật thanh toán

### GET /api/payments/statistics
Thống kê thanh toán (Admin/Management only)

---

## 🔧 Maintenance Endpoints

### GET /api/maintenance
Lấy danh sách yêu cầu bảo trì
- Student: Chỉ xem yêu cầu của mình
- staff: Xem yêu cầu được giao
- Admin/Management: Xem tất cả

### POST /api/maintenance
Tạo yêu cầu bảo trì mới (Student only)

**Request:**
```json
{
  "room_id": 1,
  "title": "Điều hòa không hoạt động",
  "description": "Điều hòa trong phòng không thể bật được",
  "image_url": "https://example.com/photo.jpg"
}
```

### POST /api/maintenance/{request_id}/assign
Phân công yêu cầu cho nhân viên (Admin/Management only)

**Request:**
```json
{
  "assigned_to_user_id": 5
}
```

### POST /api/maintenance/{request_id}/start
Bắt đầu xử lý (staff only)

### POST /api/maintenance/{request_id}/complete
Hoàn thành xử lý (staff only)

### POST /api/maintenance/{request_id}/cancel
Hủy yêu cầu

### GET /api/maintenance/statistics
Thống kê bảo trì (Admin/Management only)

---

## 🔒 Phân quyền (Roles)

1. **Admin**: Toàn quyền hệ thống
2. **Management**: Quản lý operations, không xóa users
3. **Student**: Chỉ xem/tạo/cập nhật dữ liệu của mình
4. **staff**: Xử lý yêu cầu bảo trì được giao

---

## 📊 Response Format

### Success Response
```json
{
  "data": {...},
  "message": "Success message",
  "pagination": {...} // Nếu có
}
```

### Error Response
```json
{
  "error": "Error message"
}
```

### HTTP Status Codes
- `200`: OK
- `201`: Created
- `400`: Bad Request
- `401`: Unauthorized
- `403`: Forbidden
- `404`: Not Found
- `500`: Internal Server Error

---

## 🚀 Cách sử dụng

1. **Cài đặt dependencies:**
```bash
pip install -r requirements.txt
```

2. **Chạy migrations:**
```bash
flask db upgrade
```

3. **Seed dữ liệu mẫu:**
```bash
python seed_db.py
```

4. **Chạy server:**
```bash
python application.py
```

5. **Test API với Postman/curl:**
```bash
# Login
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@qlktx.edu.vn","password":"admin123"}'

# Sử dụng token để truy cập API khác
curl -X GET http://localhost:5000/api/rooms \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```
