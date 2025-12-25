<div align="center">

# Dormitory Management System (QLKTX)

### Full-stack Student Dormitory Management Platform

<p align="center">
  <strong>Flask REST API • JWT Authentication • Room Management • Student Registration • Billing System</strong>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.9+-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python" />
  <img src="https://img.shields.io/badge/Flask-3.0+-000000?style=for-the-badge&logo=flask&logoColor=white" alt="Flask" />
  <img src="https://img.shields.io/badge/MySQL-8.0+-4479A1?style=for-the-badge&logo=mysql&logoColor=white" alt="MySQL" />
  <img src="https://img.shields.io/badge/JWT-Auth-000000?style=for-the-badge&logo=jsonwebtokens&logoColor=white" alt="JWT" />
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Status-Production-success?style=flat-square" alt="Status" />
  <img src="https://img.shields.io/badge/License-MIT-blue?style=flat-square" alt="License" />
  <img src="https://img.shields.io/badge/Architecture-Client%2FServer-orange?style=flat-square" alt="Architecture" />
</p>

---

</div>

## Table of Contents

- [Quick Start](#quick-start)
- [System Overview](#system-overview)
- [Features](#features)
- [System Architecture](#system-architecture)
- [Technology Stack](#technology-stack)
- [Installation](#installation)
- [API Documentation](#api-documentation)
- [Database Schema](#database-schema)
- [User Roles](#user-roles)
- [Configuration](#configuration)
- [Troubleshooting](#troubleshooting)

---

## Quick Start

Get up and running in 5 minutes:

```bash
# 1. Clone the repository
git clone https://github.com/minhleeee123/QLKTX.git
cd QLKTX

# 2. Setup Database
mysql -u root -p < server/schema.sql
mysql -u root -p qlktx < server/seed_db.py

# 3. Setup Server (Backend API)
cd server
pip install -r requirements.txt
# Create .env file with database credentials
python application.py  # Runs on http://localhost:5000

# 4. Setup Client (Frontend/Admin Panel)
cd ../client
pip install -r requirements.txt
# Create .env file with API URL
python application.py  # Runs on http://localhost:5001

# 5. Access the system
# Admin Panel: http://localhost:5001
# API Docs: http://localhost:5000/api
```

---

## System Overview

A comprehensive dormitory management system designed for universities and educational institutions to efficiently manage student housing, room assignments, billing, maintenance requests, and administrative tasks.

### Key Capabilities

The system provides end-to-end management of:
- **Student Registration**: Online registration and approval workflow
- **Room Management**: Room allocation, transfers, and availability tracking
- **Billing System**: Monthly fees, payment tracking, and invoicing
- **Maintenance Requests**: Issue reporting and resolution tracking
- **Administrative Dashboard**: Analytics and reporting for management
- **Access Control**: Role-based permissions for different user types

---

## Features

### 1. Student Management

#### Student Registration
- Online self-registration portal for new students
- Document upload (ID, enrollment certificate)
- Email verification with disposable email blocking
- Approval workflow for management review
- Automated notification system

#### Student Profiles
- Personal information management
- Contact details and emergency contacts
- Academic information (student ID, major, year)
- Housing history and status tracking

### 2. Room & Building Management

#### Building Administration
- Multiple building support with gender segregation
- Building-specific rules and regulations
- Facility management per building
- Access control and security settings

#### Room Operations
- Room types with different capacities (4-bed, 6-bed, service rooms)
- Real-time availability tracking
- Room status management (Available, Full, Maintenance, Reserved)
- Automated capacity calculations
- Room transfer and swap functionality

#### Room Assignments
- Intelligent room allocation based on gender and availability
- Batch assignment for multiple students
- Roommate matching preferences
- Contract generation and management

### 3. Financial Management

#### Billing System
- Automated monthly invoice generation
- Multiple fee types (rent, utilities, services)
- Payment tracking and reconciliation
- Overdue payment alerts
- Receipt generation

#### Payment Processing
- Multiple payment method support
- Payment history and reports
- Refund management
- Financial analytics and dashboards

### 4. Maintenance & Services

#### Request Management
- Issue reporting by students
- Categorized maintenance types (electrical, plumbing, furniture, etc.)
- Priority levels (Low, Medium, High, Urgent)
- Status tracking (Pending, In Progress, Resolved, Closed)
- Assignment to maintenance staff

#### Service Tracking
- Response time monitoring
- Resolution tracking
- Maintenance history per room
- Performance metrics and reporting

### 5. User Management & Security

#### Authentication
- JWT-based secure authentication
- Email verification
- Password hashing with bcrypt
- Session management
- Token refresh mechanism

#### Role-Based Access Control
- Four-tier permission system (Admin, Management, Staff, Student)
- Fine-grained permission management
- Activity logging and audit trails
- Secure API endpoints

### 6. Analytics & Reporting

#### Dashboard Metrics
- Occupancy rates per building/room type
- Revenue tracking and forecasting
- Maintenance request statistics
- Student demographics and trends

#### Export & Reports
- Excel export functionality
- Custom date range filtering
- Financial reports
- Occupancy reports
- Maintenance reports

---

## System Architecture

<div align="center">

### High-Level Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                    CLIENT APPLICATION                        │
│                    (Flask - Port 5001)                       │
│                                                              │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐   │
│  │   Admin UI   │    │  Login/Auth  │    │  Dashboard   │   │
│  │   Interface  │    │   Interface  │    │   Graphs     │   │
│  └──────┬───────┘    └──────┬───────┘    └──────┬───────┘   │
│         │                   │                   │           │
│         └───────────────────┴───────────────────┘           │
│                             │                               │
└─────────────────────────────┼───────────────────────────────┘
                              │ HTTP REST API
                              │ (JWT Authentication)
                              ▼
┌──────────────────────────────────────────────────────────────┐
│                    SERVER API                                │
│                 (Flask REST - Port 5000)                     │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐    │
│  │             API ENDPOINTS                            │    │
│  │                                                      │    │
│  │  /api/auth/*        /api/users/*                     │    │
│  │  /api/rooms/*       /api/buildings/*                 │    │
│  │  /api/registrations/* /api/contracts/*               │    │
│  │  /api/bills/*       /api/payments/*                  │    │
│  │  /api/maintenance/* /api/dashboard/*                 │    │
│  └──────────────────────┬───────────────────────────────┘    │
│                         │                                    │
│  ┌──────────────────────┴───────────────────────────────┐    │
│  │            BUSINESS LOGIC LAYER                      │    │
│  │                                                      │    │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────────┐       │    │
│  │  │   Auth   │  │  Room    │  │   Billing    │       │    │
│  │  │ Service  │  │ Service  │  │   Service    │       │    │
│  │  └──────────┘  └──────────┘  └──────────────┘       │    │
│  │                                                      │    │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────────┐       │    │
│  │  │  User    │  │Maintenance│  │Registration  │       │    │
│  │  │ Service  │  │ Service  │  │   Service    │       │    │
│  │  └──────────┘  └──────────┘  └──────────────┘       │    │
│  └──────────────────────┬───────────────────────────────┘    │
│                         │                                    │
└─────────────────────────┼────────────────────────────────────┘
                          │
                          │ SQL Queries
                          ▼
┌──────────────────────────────────────────────────────────────┐
│                    DATABASE LAYER                            │
│                    (MySQL 8.0+)                              │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐    │
│  │                  TABLES                              │    │
│  │                                                      │    │
│  │  • users           • roles          • students       │    │
│  │  • buildings       • rooms          • room_types     │    │
│  │  • registrations   • contracts      • room_assignments│  │
│  │  • bills           • payments       • payment_methods│  │
│  │  • maintenance_requests             • notifications  │    │
│  │  • activity_logs                                     │    │
│  └──────────────────────────────────────────────────────┘    │
└──────────────────────────────────────────────────────────────┘
```

</div>

### Component Details

#### Client Application (Port 5001)
- **Web Interface**: HTML/CSS/JavaScript frontend
- **Admin Dashboard**: Management portal for administrators
- **Student Portal**: Self-service interface for students
- **Reporting Tools**: Analytics and data visualization
- **Session Management**: Flask-Session for user sessions

#### Server API (Port 5000)
- **RESTful Architecture**: JSON-based API endpoints
- **JWT Authentication**: Secure token-based auth
- **Request Validation**: Input sanitization and validation
- **Error Handling**: Structured error responses
- **CORS Support**: Cross-origin request handling

#### Database Layer
- **MySQL 8.0+**: Relational database management
- **Normalized Schema**: Third normal form design
- **Indexed Queries**: Optimized for performance
- **Foreign Key Constraints**: Data integrity enforcement
- **Triggers & Procedures**: Business logic automation

---

## Technology Stack

### Backend

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Web Framework** | Flask 3.1+ | REST API and web application |
| **Authentication** | Flask-JWT-Extended | JWT token management |
| **Session Management** | Flask-Session | Server-side session storage |
| **Form Validation** | Flask-WTF, WTForms | Form handling and CSRF protection |
| **Database** | MySQL 8.0+ | Relational data storage |
| **Password Hashing** | Werkzeug | Secure password storage |
| **Email Validation** | email-validator | Email format verification |

### Frontend

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Template Engine** | Jinja2 | Server-side HTML rendering |
| **UI Framework** | Bootstrap 5 | Responsive design |
| **Charts** | Chart.js | Data visualization |
| **HTTP Client** | Requests | API communication |

### Development Tools

- **Python 3.9+**: Programming language
- **pip**: Package manager
- **Make**: Build automation
- **Git**: Version control

---

## Installation

### Prerequisites

- Python 3.9 or higher
- MySQL 8.0 or higher
- pip package manager
- Git

### Step-by-Step Setup

#### 1. Clone Repository

```bash
git clone https://github.com/minhleeee123/QLKTX.git
cd QLKTX
```

#### 2. Database Setup

Create the database and import schema:

```bash
# Login to MySQL
mysql -u root -p

# Create database and tables
source server/schema.sql

# Insert sample data (optional)
python server/seed_db.py
```

#### 3. Server Setup

```bash
cd server

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env
# Edit .env with your database credentials
```

**Server .env Configuration**:
```env
# Database
DB_HOST=localhost
DB_PORT=3306
DB_NAME=qlktx
DB_USER=root
DB_PASSWORD=your_password

# JWT
JWT_SECRET_KEY=your-super-secret-key-change-in-production
JWT_ACCESS_TOKEN_EXPIRES=3600

# Flask
FLASK_ENV=development
SECRET_KEY=your-flask-secret-key
```

Start the server:
```bash
python application.py
```

Server will run on `http://localhost:5000`

#### 4. Client Setup

```bash
cd ../client

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env
```

**Client .env Configuration**:
```env
# API Configuration
API_BASE_URL=http://localhost:5000/api

# Flask
FLASK_ENV=development
SECRET_KEY=your-client-secret-key
SESSION_TYPE=filesystem
```

Start the client:
```bash
python application.py
```

Client will run on `http://localhost:5001`

---

## API Documentation

### Base URL

```
http://localhost:5000/api
```

### Authentication

All endpoints (except login/register) require JWT token in header:

```http
Authorization: Bearer <your_jwt_token>
```

### API Endpoints Overview

#### Authentication Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/api/auth/login` | User login | No |
| POST | `/api/auth/register` | Student registration | No |
| GET | `/api/auth/me` | Get current user | Yes |
| POST | `/api/auth/logout` | Logout user | Yes |

#### User Management

| Method | Endpoint | Description | Role Required |
|--------|----------|-------------|---------------|
| GET | `/api/users` | List all users | Admin, Management |
| GET | `/api/users/{id}` | Get user details | Admin, Management |
| POST | `/api/users` | Create new user | Admin, Management |
| PUT | `/api/users/{id}` | Update user | Admin, Management |
| DELETE | `/api/users/{id}` | Delete user | Admin |

#### Room Management

| Method | Endpoint | Description | Role Required |
|--------|----------|-------------|---------------|
| GET | `/api/rooms` | List all rooms | All authenticated |
| GET | `/api/rooms/{id}` | Get room details | All authenticated |
| POST | `/api/rooms` | Create room | Admin, Management |
| PUT | `/api/rooms/{id}` | Update room | Admin, Management |
| DELETE | `/api/rooms/{id}` | Delete room | Admin |
| GET | `/api/rooms/available` | Get available rooms | All authenticated |

#### Registration & Contracts

| Method | Endpoint | Description | Role Required |
|--------|----------|-------------|---------------|
| GET | `/api/registrations` | List registrations | Admin, Management |
| POST | `/api/registrations` | Submit registration | Student |
| PUT | `/api/registrations/{id}/approve` | Approve registration | Admin, Management |
| GET | `/api/contracts` | List contracts | Admin, Management |
| POST | `/api/contracts` | Create contract | Admin, Management |

#### Billing & Payments

| Method | Endpoint | Description | Role Required |
|--------|----------|-------------|---------------|
| GET | `/api/bills` | List bills | All authenticated |
| POST | `/api/bills/generate` | Generate monthly bills | Admin, Management |
| POST | `/api/payments` | Record payment | Admin, Management, Student |
| GET | `/api/payments/{id}/receipt` | Download receipt | All authenticated |

#### Maintenance

| Method | Endpoint | Description | Role Required |
|--------|----------|-------------|---------------|
| GET | `/api/maintenance` | List requests | All authenticated |
| POST | `/api/maintenance` | Create request | Student |
| PUT | `/api/maintenance/{id}` | Update status | Admin, Staff |

#### Dashboard & Analytics

| Method | Endpoint | Description | Role Required |
|--------|----------|-------------|---------------|
| GET | `/api/dashboard/stats` | Get statistics | Admin, Management |
| GET | `/api/dashboard/occupancy` | Occupancy rates | Admin, Management |
| GET | `/api/dashboard/revenue` | Revenue report | Admin |

### Example API Request

**Login Request**:
```bash
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@qlktx.edu.vn",
    "password": "admin123"
  }'
```

**Response**:
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user": {
    "user_id": 1,
    "full_name": "Nguyen Van Admin",
    "email": "admin@qlktx.edu.vn",
    "role": "Admin"
  }
}
```

**Authenticated Request Example**:
```bash
curl -X GET http://localhost:5000/api/rooms \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc..."
```

---

## Database Schema

### Core Tables

#### Users & Authentication
- **users**: User accounts and profiles
- **roles**: User role definitions (Admin, Management, Staff, Student)

#### Room Management
- **buildings**: Dormitory buildings
- **room_types**: Room capacity and pricing
- **rooms**: Individual room information
- **room_assignments**: Student-room mappings

#### Registration & Contracts
- **registrations**: Student registration applications
- **contracts**: Housing contracts
- **contract_rooms**: Contract-room relationships

#### Financial
- **bills**: Monthly invoices
- **payments**: Payment records
- **payment_methods**: Payment types

#### Maintenance
- **maintenance_requests**: Issue reports and tracking
- **maintenance_types**: Request categorization

#### System
- **notifications**: User notifications
- **activity_logs**: Audit trail

### Entity Relationships

```
users (1) ──→ (N) registrations
users (1) ──→ (N) contracts
users (1) ──→ (N) maintenance_requests
users (N) ──→ (1) roles

buildings (1) ──→ (N) rooms
room_types (1) ──→ (N) rooms
rooms (1) ──→ (N) room_assignments
rooms (1) ──→ (N) contracts
rooms (1) ──→ (N) maintenance_requests

contracts (1) ──→ (N) bills
bills (1) ──→ (N) payments
```

---

## User Roles

### 1. Admin
- Full system access
- User management (create, update, delete)
- System configuration
- Financial reports and analytics
- Database backup and restore

### 2. Management
- Room and building management
- Registration approval
- Contract management
- Billing operations
- Reports and analytics (limited)

### 3. Staff
- Maintenance request handling
- Room inspections
- Service provision
- Issue resolution

### 4. Student
- Self-registration
- View personal information
- Submit maintenance requests
- View bills and make payments
- Room information access

---

## Configuration

### Server Configuration

Edit `server/config.py`:

```python
class Config:
    # Database
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_PORT = int(os.getenv('DB_PORT', 3306))
    DB_NAME = os.getenv('DB_NAME', 'qlktx')
    
    # JWT
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    
    # Flask
    SECRET_KEY = os.getenv('SECRET_KEY')
```

### Client Configuration

Edit `client/config.py`:

```python
class Config:
    # API
    API_BASE_URL = os.getenv('API_BASE_URL', 'http://localhost:5000/api')
    
    # Session
    SESSION_TYPE = 'filesystem'
    SESSION_PERMANENT = False
    SESSION_USE_SIGNER = True
```

---

## Project Structure

```
QLKTX/
├── server/                         # Backend API
│   ├── application.py              # API entry point
│   ├── config.py                   # Server configuration
│   ├── requirements.txt            # Python dependencies
│   ├── schema.sql                  # Database schema
│   ├── seed_db.py                  # Sample data seeder
│   ├── API_DOCUMENTATION.md        # Detailed API docs
│   ├── app/                        # Application package
│   │   ├── __init__.py
│   │   ├── models/                 # Database models
│   │   ├── routes/                 # API endpoints
│   │   ├── services/               # Business logic
│   │   └── utils/                  # Helper functions
│   └── tests/                      # API tests
├── client/                         # Frontend application
│   ├── application.py              # Client entry point
│   ├── config.py                   # Client configuration
│   ├── requirements.txt            # Python dependencies
│   ├── app/                        # Application package
│   │   ├── __init__.py
│   │   ├── routes/                 # Page routes
│   │   ├── templates/              # HTML templates
│   │   ├── static/                 # CSS, JS, images
│   │   └── services/               # API client services
│   └── tests/                      # Integration tests
└── README.md                       # This file
```

---

## Development

### Running Tests

```bash
# Server tests
cd server
python -m pytest tests/

# Client tests
cd client
python -m pytest tests/
```

### Database Migrations

```bash
# Create migration
python manage.py db migrate -m "Description"

# Apply migration
python manage.py db upgrade
```

### Code Style

Follow PEP 8 guidelines:

```bash
# Format code
black app/

# Check style
flake8 app/
```

---

## Deployment

### Production Checklist

- [ ] Change SECRET_KEY and JWT_SECRET_KEY
- [ ] Set FLASK_ENV=production
- [ ] Use production database
- [ ] Enable HTTPS
- [ ] Configure reverse proxy (Nginx)
- [ ] Set up SSL certificates
- [ ] Enable database backups
- [ ] Configure logging
- [ ] Set up monitoring

### Docker Deployment

```bash
# Build images
docker-compose build

# Start services
docker-compose up -d

# View logs
docker-compose logs -f
```

---

## Troubleshooting

### Common Issues

**Database Connection Error**:
```
Error: Can't connect to MySQL server
```
**Solution**: Check database credentials in .env file

**JWT Token Expired**:
```
Error: Token has expired
```
**Solution**: Login again to get new token

**Port Already in Use**:
```
Error: Address already in use
```
**Solution**: Kill process or use different port

**Import Module Error**:
```
ModuleNotFoundError: No module named 'flask'
```
**Solution**: Activate virtual environment and install requirements

---

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open Pull Request

---

## License

This project is licensed under the MIT License.

---

## Support

For issues or questions:
- Open an issue on GitHub
- Check API documentation in `/server/API_DOCUMENTATION.md`
- Review database schema in `/server/schema.sql`

---

<div align="center">

## Contact

**Developed for University Dormitory Management**

Built with Flask, MySQL, and JWT Authentication

---

**Efficient Dormitory Management Made Simple**

</div>
