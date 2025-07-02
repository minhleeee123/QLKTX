CREATE DATABASE IF NOT EXISTS qlktx;
USE qlktx;

-- =================================================================
-- 1. BẢNG QUẢN LÝ NGƯỜI DÙNG VÀ PHÂN QUYỀN
-- =================================================================

-- Bảng lưu các vai trò trong hệ thống
CREATE TABLE roles (
    role_id INT PRIMARY KEY AUTO_INCREMENT,
    role_name VARCHAR(50) NOT NULL UNIQUE -- 'Admin', 'Management', 'Student', 'MaintenanceStaff'
);

-- Bảng lưu thông tin người dùng
CREATE TABLE users (
    user_id INT PRIMARY KEY AUTO_INCREMENT,
    role_id INT NOT NULL,
    full_name VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    phone_number VARCHAR(15),
    student_code VARCHAR(20) UNIQUE, -- Mã số sinh viên
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    FOREIGN KEY (role_id) REFERENCES roles(role_id)
);


-- =================================================================
-- 2. BẢNG QUẢN LÝ PHÒNG ỐC VÀ CƠ SỞ VẬT CHẤT
-- =================================================================

-- Bảng lưu thông tin các tòa nhà/khu
CREATE TABLE buildings (
    building_id INT PRIMARY KEY AUTO_INCREMENT,
    building_name VARCHAR(100) NOT NULL
);

-- Bảng lưu các loại phòng
CREATE TABLE room_types (
    room_type_id INT PRIMARY KEY AUTO_INCREMENT,
    type_name VARCHAR(100) NOT NULL, -- 'Phòng 4 người', 'Phòng 6 người', 'Phòng dịch vụ'
    capacity INT NOT NULL,
    price DECIMAL(10, 2) NOT NULL
);

-- Bảng lưu thông tin chi tiết từng phòng
CREATE TABLE rooms (
    room_id INT PRIMARY KEY AUTO_INCREMENT,
    room_number VARCHAR(10) NOT NULL,
    building_id INT NOT NULL,
    room_type_id INT NOT NULL,
    status VARCHAR(50) DEFAULT 'available', -- 'available', 'occupied', 'pending_approval', 'maintenance'
    current_occupancy INT DEFAULT 0,
    FOREIGN KEY (building_id) REFERENCES buildings(building_id),
    FOREIGN KEY (room_type_id) REFERENCES room_types(room_type_id)
);


-- =================================================================
-- 3. BẢNG XỬ LÝ NGHIỆP VỤ CHÍNH
-- =================================================================

-- Bảng lưu đơn đăng ký của sinh viên
CREATE TABLE registrations (
    registration_id INT PRIMARY KEY AUTO_INCREMENT,
    student_id INT NOT NULL,
    room_id INT NOT NULL,
    status VARCHAR(50) DEFAULT 'pending', -- 'pending', 'approved', 'rejected'
    registration_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES users(user_id),
    FOREIGN KEY (room_id) REFERENCES rooms(room_id),
);

-- Bảng lưu hợp đồng
CREATE TABLE contracts (
    contract_id INT PRIMARY KEY AUTO_INCREMENT,
    registration_id INT NOT NULL UNIQUE,
    contract_code VARCHAR(50) UNIQUE,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (registration_id) REFERENCES registrations(registration_id)
);

-- Bảng lưu thông tin thanh toán
CREATE TABLE payments (
    payment_id INT PRIMARY KEY AUTO_INCREMENT,
    contract_id INT NOT NULL,
    amount DECIMAL(10, 2) NOT NULL,
    payment_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    payment_method VARCHAR(50), -- 'bank_transfer', 'cash'
    status VARCHAR(50) DEFAULT 'pending', -- 'pending', 'confirmed', 'failed'
    proof_image_url VARCHAR(255), -- URL ảnh chụp màn hình giao dịch
    confirmed_by_user_id INT, -- ID người xác nhận
    FOREIGN KEY (contract_id) REFERENCES contracts(contract_id),
    FOREIGN KEY (confirmed_by_user_id) REFERENCES users(user_id)
);


-- =================================================================
-- 4. BẢNG NGHIỆP VỤ BẢO TRÌ
-- =================================================================

CREATE TABLE maintenance_requests (
    request_id INT PRIMARY KEY AUTO_INCREMENT,
    student_id INT NOT NULL,
    room_id INT NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    image_url VARCHAR(255),
    status VARCHAR(50) DEFAULT 'pending', -- 'pending', 'assigned', 'in_progress', 'completed', 'cancelled'
    request_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    assigned_to_user_id INT, -- ID nhân viên bảo trì được phân công
    completed_date TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES users(user_id),
    FOREIGN KEY (room_id) REFERENCES rooms(room_id),
    FOREIGN KEY (assigned_to_user_id) REFERENCES users(user_id)
);