# 🏷️ SnowVoucher – Online Discount Voucher E-commerce Platform

> An e-commerce platform for discovering, purchasing, and managing discount vouchers from multiple partners and locations.

## 🌐 Demo

- **Live Website:** https://ec07-snowvoucher.onrender.com
- **GitHub Repository:** https://github.com/Tramie-Nguyen/saleVoucher_EC_23HTTT
- **Demo Video:** `[Insert demo video link]`

---

# 📖 Project Overview

**SnowVoucher** is an online e-commerce platform designed to provide customers with convenient access to discount vouchers from various partners and locations.

The system supports three main roles:

- **Customers:** Search, browse, purchase, and manage discount vouchers.
- **Partners:** Manage partner information and vouchers, and verify purchased vouchers using QR codes.
- **Administrators:** Manage users, partners, vouchers, reviews, advertisements, and other system activities.

The project follows a **Frontend – Backend – Database** architecture and includes a Python-based data crawling component for collecting and processing external data.

---

# ✨ Main Features

## 👤 Customer

- Account registration
- Login and logout
- OTP-based account verification
- Profile management
- Password change
- Voucher search and filtering
- Voucher detail viewing
- Partner and location information
- Shopping cart management
- Order creation
- Online payment
- Order history
- Purchased voucher management
- Reviews, feedback, and complaints

## 🏪 Partner

- Login and logout
- Partner profile management
- Voucher management
- Create and update vouchers
- Manage voucher status
- Manage voucher-related information
- Scan QR codes to verify purchased vouchers

## 👨‍💼 Administrator

- Login and logout
- User account management
- Partner management
- Voucher management
- Voucher approval and moderation
- Review management
- Complaint and feedback management
- Advertisement content management
- System data management

---

# 💳 Online Payment

The system supports an online payment workflow:

```text
Customer
   ↓
Shopping Cart
   ↓
Create Order
   ↓
Payment
   ↓
Payment Gateway
   ↓
Callback / IPN
   ↓
Backend verifies transaction
   ↓
Update Order Status
```

Payment-related credentials and secrets are stored in environment variables and are not exposed to the frontend.

---

# 🔐 Authentication & Security

The system implements:

- Authentication and authorization
- JWT-based authentication
- Password hashing
- Role-based access control
- Middleware-based access control
- Protected API endpoints
- OTP-based account verification
- Environment variables for sensitive credentials

---

# 📧 OTP Verification

Customer account verification uses **SendGrid** to send OTP codes via email.

```text
Customer
   ↓
Request OTP
   ↓
Backend generates OTP
   ↓
SendGrid sends OTP
   ↓
Customer enters OTP
   ↓
Backend validates OTP
   ↓
Account verification completed
```

---

# 🕷️ Data Crawling

The project includes a Python-based data crawling component located in:

```text
crawl data/
```

It is used to collect, filter, and process external data before importing it into the system.

```text
crawl data/
├── chinhanh.py
├── data.py
├── filter.py
├── hsdn.py
├── nguoidung.py
├── tai_khoan.py
├── voucher_cn.py
├── start.py
├── text.txt
└── requirements.txt
```

The crawling process includes:

- Collecting voucher information
- Collecting branch/location information
- Collecting partner-related information
- Filtering raw data
- Processing data for system use

### Technologies

- Python
- Requests
- BeautifulSoup
- Python Virtual Environment

---

# 🏗️ System Architecture

The project follows a separated frontend, backend, and database architecture:

```text
                         ┌───────────────┐
                         │   Customers   │
                         └───────┬───────┘
                                 │
                                 ▼
                    ┌──────────────────────┐
                    │      Frontend        │
                    │   React + Vite       │
                    │    Tailwind CSS      │
                    └──────────┬───────────┘
                               │
                            REST API
                               │
                               ▼
                    ┌──────────────────────┐
                    │       Backend        │
                    │   Node.js + Express  │
                    └──────────┬───────────┘
                               │
              ┌────────────────┼────────────────┐
              │                │                │
              ▼                ▼                ▼
       ┌────────────┐   ┌─────────────┐   ┌────────────┐
       │  Database  │   │   Payment   │   │  External  │
       │ PostgreSQL │   │   Gateway   │   │  Services  │
       └────────────┘   └─────────────┘   └────────────┘
                                                │
                                                ▼
                                        ┌──────────────┐
                                        │   SendGrid   │
                                        └──────────────┘

                         ▲
                         │
                  ┌──────┴───────┐
                  │ Data Crawling│
                  │    Python    │
                  └──────────────┘
```

---

# 🛠️ Technologies

| Category              | Technologies                                            |
| --------------------- | ------------------------------------------------------- |
| **Frontend**          | React.js, Vite, Tailwind CSS, JavaScript, React Router  |
| **Backend**           | Node.js, Express.js, RESTful API, JWT, bcryptjs, dotenv |
| **Database**          | PostgreSQL, Supabase, SQL                               |
| **Authentication**    | JWT, bcryptjs, SendGrid                                 |
| **Payment**           | Online Payment Gateway                                  |
| **QR Code**           | QR Code generation and scanning                         |
| **Data Crawling**     | Python, Requests, BeautifulSoup                         |
| **Development Tools** | Git, GitHub, Visual Studio Code, Postman, Figma         |
| **Deployment**        | Render                                                  |

---

# 📁 Project Structure

```text
saleVoucher_EC_23HTTT/
│
├── backend/
│   ├── src/
│   │   ├── app.js
│   │   ├── server.js
│   │   ├── config/
│   │   ├── common/
│   │   ├── modules/
│   │   └── routes/
│   │
│   ├── package.json
│   └── package-lock.json
│
├── frontend/
│   ├── src/
│   │   ├── main.jsx
│   │   ├── App.jsx
│   │   ├── app/
│   │   ├── layouts/
│   │   ├── routes/
│   │   ├── shared/
│   │   └── features/
│   │
│   ├── package.json
│   └── package-lock.json
│
├── crawl data/
│   ├── start.py
│   ├── data.py
│   ├── filter.py
│   ├── chinhanh.py
│   ├── hsdn.py
│   ├── nguoidung.py
│   ├── tai_khoan.py
│   ├── voucher_cn.py
│   └── requirements.txt
│
├── database/
│
├── docs/
│
├── .gitignore
├── package.json
└── README.md
```

---

# ⚙️ Installation & Setup

## 1. Clone the Repository

```bash
git clone https://github.com/Tramie-Nguyen/saleVoucher_EC_23HTTT.git
cd saleVoucher_EC_23HTTT
```

## 2. Backend

Navigate to the backend directory:

```bash
cd backend
```

Install dependencies:

```bash
npm install
```

Create:

```text
backend/.env
```

Configure the required environment variables for:

- Database connection
- JWT
- Frontend URL
- Payment services
- SendGrid
- Other external services

Run the development server:

```bash
npm run dev
```

Or run in production mode:

```bash
npm start
```

Backend:

```text
http://localhost:3001
```

---

## 3. Frontend

Open another terminal and navigate to:

```bash
cd frontend
```

Install dependencies:

```bash
npm install
```

Run the development server:

```bash
npm run dev
```

Frontend:

```text
http://localhost:5173
```

---

## 4. Crawl Data

Navigate to:

```bash
cd "crawl data"
```

Create a Python virtual environment:

```bash
python -m venv venv
```

Activate it on Windows:

**Command Prompt**

```bash
venv\Scripts\activate
```

**PowerShell**

```powershell
.\venv\Scripts\Activate.ps1
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the crawler:

```bash
python start.py
```

> The `requirements.txt` file contains the dependencies required by the crawling component. The `venv/` and `__pycache__/` directories should not be committed to Git.

---

# 🔄 Backend Request Flow

The backend follows a layered and modular structure:

```text
Client Request
      ↓
Route
      ↓
Middleware
      ↓
Controller
      ↓
Service
      ↓
Repository / Model
      ↓
Database
      ↓
Response
```

This structure separates routing, authentication, business logic, data access, and database operations.

---

# 🧪 Testing & Documentation

All four team members participated in the overall development process, including:

- Database design
- System analysis and design
- Business requirements and system specifications
- API and system documentation
- Functional testing
- API testing
- User flow testing
- Authentication and authorization testing
- Integration and debugging

Project documentation is maintained in:

```text
docs/
```

It includes materials such as:

- System analysis and design
- Database design
- API documentation
- Test cases
- Screenshots
- Other project documentation

---

# 👥 Team Contributions

| No. | Member                   | Main Responsibilities                                                                                    |
| --- | ------------------------ | -------------------------------------------------------------------------------------------------------- |
| 1   | **Nguyễn Ngọc Mai Xuân** | **Team Leader**; Admin module; Middleware; QR voucher scanning for Partner module                        |
| 2   | **Nguyễn Thị Trà My**    | Customer module; OTP verification using SendGrid; Data crawling                                          |
| 3   | **Nguyễn Kim Ngân**      | Partner module; Part of Admin module; English/Vietnamese language support                                |
| 4   | **Vũ Ngọc Minh Quang**   | Customer feedback, reviews and complaints; Review management; Advertisement content management for Admin |

> All team members also contributed to database design, documentation, business and system specifications, testing, integration, and debugging.

---

# 🌍 Deployment

The project has been deployed using Render.

**Live Website:** https://ec07-snowvoucher.onrender.com

For production deployment, environment variables such as database credentials, JWT secrets, API keys, payment credentials, and service URLs must be configured separately.

---

# 📄 Academic Project

**Project Title:**

> Building an E-commerce System for Selling Discount Vouchers Online

**Course:** E-commerce

**University:** Ho Chi Minh City University of Science – Vietnam National University Ho Chi Minh City

**Team Size:** 4 members

---

## ⭐ Acknowledgement

This project was developed as an academic project to apply knowledge and practical skills in:

- E-commerce
- System Analysis and Design
- Web Development
- RESTful API
- Database Design
- Authentication and Authorization
- Online Payment
- Web Scraping
- Software Testing
- Deployment
