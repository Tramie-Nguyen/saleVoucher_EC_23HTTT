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

The project follows a **Frontend – Backend – Database** architecture (monorepo, deployed as a single service) and includes a Python-based data crawling component for collecting and processing external data.

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
- Online payment (VNPay / PayPal)
- Order history
- Purchased voucher management (with QR code)
- Reviews, feedback, and complaints
- Multi-language interface (Vietnamese / English)

## 🏪 Partner

- Login and logout
- Partner profile management
- Branch/staff management
- Voucher management
- Create and update vouchers
- Manage voucher status
- Manage voucher-related information
- Scan QR codes to verify purchased vouchers
- Partner-level reports

## 👨‍💼 Administrator

- Login and logout
- User account management
- Partner management (approval)
- Voucher management (approval and moderation)
- Order management
- Review management
- Complaint and feedback management
- Advertisement / content management
- Dashboard and analytics (charts)
- Audit log / system activity log

---

# 💳 Online Payment

The system integrates **two real payment gateways**, configured through environment variables:

- **VNPay** — domestic payment gateway (sandbox by default)
- **PayPal** — international payment gateway

General payment workflow:

```
Customer
   ↓
Shopping Cart
   ↓
Create Order
   ↓
Choose Payment Method (VNPay / PayPal)
   ↓
Redirect to Payment Gateway
   ↓
Callback / Return URL / IPN
   ↓
Backend verifies transaction
   ↓
Update Order Status → Issue Voucher Code / QR
```

Payment-related credentials and secrets are stored in environment variables (`VNP_*`, `PAYPAL_*`) and are never exposed to the frontend.

---

# 🔐 Authentication & Security

The system implements:

- JWT-based authentication (Access Token + Refresh Token)
- Password hashing (bcryptjs)
- Role-based access control (Customer / Partner / Admin)
- Middleware-based authentication & authorization
- Protected API endpoints
- OTP-based account verification
- CORS configuration
- Environment variables for all sensitive credentials (never committed to Git)

---

# 📧 OTP Verification

Customer account verification uses **SendGrid** to send OTP codes via email.

```
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

```
crawl data/
```

It is used to collect, filter, and process external data before importing it into the system.

```
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

```
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
                     REST API (/api)
                        │
                        ▼
             ┌──────────────────────┐
             │       Backend        │
             │   Node.js + Express  │
             └──────────┬───────────┘
                        │
       ┌────────────────┼────────────────────┐
       │                │                     │
       ▼                ▼                     ▼
┌────────────┐   ┌─────────────┐      ┌────────────┐
│  Database  │   │   Payment   │      │  External  │
│ PostgreSQL │   │  VNPay /    │      │  Services  │
│ (Supabase) │   │  PayPal     │      │            │
└────────────┘   └─────────────┘      └─────┬──────┘
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

> **Note:** In production, the backend serves the built frontend (`frontend/dist`) directly as static files, so the whole app runs as a **single deployable service** (this is how the Render demo is hosted).

---

# 🛠️ Technologies

| Category              | Technologies                                                                                                                                                                          |
| --------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Frontend**          | React 18, Vite, Tailwind CSS, React Router, i18next / react-i18next, Recharts (dashboard charts), Tiptap (rich text editor), Sonner (toast notifications), html5-qrcode (QR scanning) |
| **Backend**           | Node.js, Express.js, RESTful API, JWT (jsonwebtoken), bcryptjs, dotenv, qrcode (QR generation)                                                                                        |
| **Database**          | PostgreSQL, Supabase (Supabase JS client), SQL                                                                                                                                        |
| **Authentication**    | JWT, bcryptjs, SendGrid (OTP email)                                                                                                                                                   |
| **Payment**           | VNPay, PayPal                                                                                                                                                                         |
| **QR Code**           | `qrcode` (generation, backend) + `html5-qrcode` (scanning, frontend)                                                                                                                  |
| **Data Crawling**     | Python, Requests, BeautifulSoup                                                                                                                                                       |
| **Development Tools** | Git, GitHub, Visual Studio Code, Postman, Figma                                                                                                                                       |
| **Deployment**        | Render (single service: backend serves built frontend)                                                                                                                                |

---

# 📁 Project Structure

```
saleVoucher_EC_23HTTT/
│
├── backend/
│   ├── src/
│   │   ├── app.js
│   │   ├── server.js
│   │   ├── config/            # environment.js, supabase.js, cors.js
│   │   ├── common/            # constants, errors, middleware, utils, cache
│   │   ├── modules/           # core-access, customer-commerce, partner-voucher, content-feedback
│   │   └── routes/
│   │
│   ├── package.json
│   └── package-lock.json
│
├── frontend/
│   ├── src/
│   │   ├── main.jsx
│   │   ├── App.jsx
│   │   ├── app/                # auth-context, query-client, router
│   │   ├── layouts/             # Admin / Customer / Partner / Public layouts
│   │   ├── routes/
│   │   ├── shared/               # api clients, components, hooks, i18n, store, utils
│   │   └── features/            # core-access, customer-commerce, partner-voucher, content-feedback
│   │
│   ├── vite.config.js           # dev proxy: /api → http://localhost:3001
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
│   ├── create_tables.sql        # PostgreSQL/Supabase schema
│   ├── seeds.sql                 # demo seed data
│   └── data.sql                  # additional sample data
│
├── docs/
│
├── .gitignore
├── package.json                  # root scripts: build (frontend+backend), start
└── README.md
```

---

# ⚙️ Installation & Setup

## 1. Clone the Repository

```
git clone https://github.com/Tramie-Nguyen/saleVoucher_EC_23HTTT.git
cd saleVoucher_EC_23HTTT
```

## 2. Database (PostgreSQL / Supabase)

Create a PostgreSQL database (a free [Supabase](https://supabase.com) project works out of the box) and run the SQL scripts in the `database/` folder, in this order, using the Supabase SQL Editor or `psql`:

```
database/create_tables.sql
database/seeds.sql
database/data.sql
```

Keep note of your project's **Supabase URL** and **Service Role Key** — they are required in the next step.

## 3. Backend

Navigate to the backend directory:

```
cd backend
```

Install dependencies:

```
npm install
```

Create a `backend/.env` file with at least the following variables:

```env
# Server
PORT=3001
NODE_ENV=development

# Database (Supabase)
SUPABASE_URL=your_supabase_project_url
SUPABASE_SERVICE_ROLE_KEY=your_supabase_service_role_key

# JWT
JWT_SECRET=your_jwt_secret
JWT_REFRESH_SECRET=your_jwt_refresh_secret
ACCESS_TOKEN_EXPIRY=1440m
REFRESH_TOKEN_EXPIRY=7d

# SendGrid (OTP email)
SENDGRID_API_KEY=your_sendgrid_api_key
SENDGRID_FROM=your_verified_sender_email

# VNPay
VNP_TMN_CODE=your_vnpay_tmn_code
VNP_HASH_SECRET=your_vnpay_hash_secret
VNP_URL=https://sandbox.vnpayment.vn/paymentv2/vpcpay.html
VNP_PAYMENT_RETURN_URL=http://localhost:5173/payment/vnpay-return

# PayPal
PAYPAL_CLIENT_ID=your_paypal_client_id
PAYPAL_CLIENT_SECRET=your_paypal_client_secret
PAYPAL_API_BASE=https://api-m.sandbox.paypal.com
PAYPAL_RETURN_URL=http://localhost:5173/payment/paypal-return
PAYPAL_CANCEL_URL=http://localhost:5173/payment/paypal-cancel
```

Run the development server:

```
npm run dev
```

Or run in production mode:

```
npm start
```

Backend:

```
http://localhost:3001
```

---

## 4. Frontend

Open another terminal and navigate to:

```
cd frontend
```

Install dependencies:

```
npm install
```

Run the development server:

```
npm run dev
```

Frontend:

```
http://localhost:5173
```

> In development, Vite automatically proxies all `/api` requests to `http://localhost:3001` (see `frontend/vite.config.js`), so no extra frontend `.env` is required by default. If you need to point the frontend at a different backend URL, set `VITE_API_BASE_URL` in a `frontend/.env` file.

---

## 5. Crawl Data (optional)

Navigate to:

```
cd "crawl data"
```

Create a Python virtual environment:

```
python -m venv venv
```

Activate it on Windows:

**Command Prompt**

```
venv\Scripts\activate
```

**PowerShell**

```
.\venv\Scripts\Activate.ps1
```

Install dependencies:

```
pip install -r requirements.txt
```

Run the crawler:

```
python start.py
```

> The `requirements.txt` file contains the dependencies required by the crawling component. The `venv/` and `__pycache__/` directories should not be committed to Git.

---

## 6. Run Everything from the Root (alternative)

The root `package.json` provides convenience scripts that mirror the production build/run flow (frontend build is served statically by the backend):

```
npm run build   # installs & builds frontend, installs backend deps
npm start       # starts the backend, which serves the built frontend in production
```

---

# 🔄 Backend Request Flow

The backend follows a layered and modular structure:

```
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

```
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

The project is deployed on **Render** as a single web service: the backend (Express) builds and serves the compiled frontend (`frontend/dist`) directly, so only one URL is needed in production.

**Live Website:** https://ec07-snowvoucher.onrender.com

For production deployment, configure all environment variables listed in the [Backend setup](#3-backend) section (database, JWT, SendGrid, VNPay, PayPal) directly on the hosting platform — never commit them to the repository.

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
