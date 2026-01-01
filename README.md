# 🏢 Enterprise Knowledge Assistant

<div align="center">

![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Docker](https://img.shields.io/badge/docker-ready-brightgreen.svg)
![Python](https://img.shields.io/badge/python-3.10+-blue.svg)
![TypeScript](https://img.shields.io/badge/typescript-5.0+-blue.svg)

**An AI-powered enterprise knowledge management system with department-based access control, RAG pipeline, and modern glassmorphism UI.**

[Features](#-features) • [Architecture](#-architecture) • [Quick Start](#-quick-start) • [API Reference](#-api-reference) • [Screenshots](#-screenshots)

</div>

---

## 📋 Table of Contents

- [Features](#-features)
- [Architecture](#-architecture)
- [Tech Stack](#-tech-stack)
- [Quick Start](#-quick-start)
- [Configuration](#-configuration)
- [User Guide](#-user-guide)
- [Admin Guide](#-admin-guide)
- [API Reference](#-api-reference)
- [Database Schema](#-database-schema)
- [Security](#-security)
- [Project Structure](#-project-structure)
- [Development](#-development)
- [Troubleshooting](#-troubleshooting)
- [Contributing](#-contributing)
- [License](#-license)

---

## ✨ Features

### 🤖 AI-Powered Knowledge Assistant
- **Retrieval-Augmented Generation (RAG)** - Answers questions based on your organization's documents
- **Department-Aware Responses** - AI only uses documents relevant to the user's department + common documents
- **Context-Aware Chat** - Maintains conversation history for natural interactions
- **Policy Verification** - Ensures responses align with company policies

### 🔐 Enterprise Security
- **Google OAuth Integration** - Single Sign-On with Google accounts
- **Standard Authentication** - Email/password login with bcrypt hashing
- **JWT Token Management** - Secure session handling
- **Role-Based Access Control** - Admin and User roles
- **Department-Based Document Access** - Users only see relevant documents

### 📚 Knowledge Management
- **Document Categories**:
  - 🌐 **Common** - Visible to ALL users across all departments
  - 🏢 **Department-Specific** - Only visible to users in that department
- **Version Control** - Track document versions
- **Bulk Operations** - Select and delete multiple documents (Admin)
- **Full-Text Search** - Vector-based semantic search

### 👥 User Management (Admin)
- **Admin-Only User Creation** - No self-registration for security
- **Secure Password Generation** - Auto-generated strong passwords
- **Department Assignment** - 10 departments supported
- **Role Management** - Assign admin or user roles
- **User Editing & Deletion** - Full user lifecycle management

### 🎨 Modern UI/UX
- **Glassmorphism Design** - Modern iPhone-inspired aesthetics
- **Animated Landing Page** - Engaging blob animations
- **Responsive Layout** - Works on desktop and mobile
- **Dark/Light Themes** - Gradient color palette
- **Intuitive Navigation** - Clean dashboard layout

---

## 🏗 Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                              FRONTEND                                    │
│                    React + TypeScript + Glassmorphism                   │
│                         (Port 3000)                                      │
└─────────────────────────────────┬───────────────────────────────────────┘
                                  │ REST API / JWT
                                  ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                              BACKEND                                     │
│                         FastAPI (Port 8000)                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌─────────────┐ │
│  │    Routes    │  │    Agents    │  │   Services   │  │    Auth     │ │
│  │  - /auth     │  │  - Retrieval │  │  - Document  │  │  - JWT      │ │
│  │  - /admin    │  │  - Answer    │  │    Ingestion │  │  - OAuth    │ │
│  │  - /documents│  │  - Policy    │  │              │  │  - Password │ │
│  │  - /question │  │  - Escalation│  │              │  │             │ │
│  └──────────────┘  └──────────────┘  └──────────────┘  └─────────────┘ │
└─────────────────────────┬───────────────────┬───────────────────────────┘
                          │                   │
              ┌───────────▼───────┐   ┌───────▼───────┐
              │    PostgreSQL     │   │   ChromaDB    │
              │   (Port 5432)     │   │  (Port 8001)  │
              │                   │   │               │
              │  - Users          │   │  - Documents  │
              │  - Sessions       │   │  - Embeddings │
              │  - Audit Logs     │   │  - Metadata   │
              └───────────────────┘   └───────────────┘
```

### RAG Pipeline Flow

```
User Question
      │
      ▼
┌─────────────────┐
│ Embed Question  │  ← SentenceTransformers (all-MiniLM-L6-v2)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Retrieve Docs   │  ← ChromaDB query with department filter
│ (Dept + Common) │     + common documents (category='common')
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Verify Policy   │  ← Check against company policies
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Generate Answer │  ← Ollama LLM (local) or fallback
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Escalate if     │  ← If context insufficient
│ Needed          │
└─────────────────┘
```

---

## 🛠 Tech Stack

| Layer | Technology | Purpose |
|-------|------------|---------|
| **Frontend** | React 18, TypeScript 5 | UI Framework |
| **Styling** | CSS3, Glassmorphism | Modern Design |
| **Routing** | React Router DOM | SPA Navigation |
| **Backend** | FastAPI, Python 3.10+ | REST API |
| **Database** | PostgreSQL 15 | User Data, Audit Logs |
| **Vector DB** | ChromaDB | Document Embeddings |
| **Embeddings** | SentenceTransformers | Text to Vectors |
| **LLM** | Ollama (Local) | Answer Generation |
| **Auth** | Google OAuth 2.0, JWT | Authentication |
| **Passwords** | bcrypt | Secure Hashing |
| **Container** | Docker, Docker Compose | Deployment |
| **Web Server** | Nginx (Production) | Frontend Serving |
| **Proxy** | Uvicorn | ASGI Server |

### Why These Choices?

- **All Open Source** - No vendor lock-in, no API costs
- **Privacy First** - Local LLM keeps data on-premises
- **Industry Standard** - Skills transfer to real-world jobs
- **Student Friendly** - Free tools, extensive documentation

---

## 🚀 Quick Start

### Prerequisites

- Docker Desktop (Windows/Mac) or Docker Engine (Linux)
- Docker Compose v2.0+
- Git
- (Optional) Ollama for local LLM

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/yourusername/enterprise-assistant.git
cd enterprise-assistant

# 2. Create environment file
cp backend/app/.env.example backend/app/.env

# 3. Configure environment variables (see Configuration section)
# Edit backend/app/.env with your settings

# 4. Start all services
docker-compose up --build -d

# 5. Wait for services to initialize (first run may take 2-3 minutes)
docker-compose logs -f backend

# 6. Access the application
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000/docs
```

### First-Time Setup

1. **Create Admin User**: The first user must be created via API or database
2. **Login**: Use the admin credentials
3. **Add Users**: Use Admin → Users to create department users
4. **Upload Documents**: Use Admin → Upload to add knowledge base content
5. **Start Chatting**: Users can now ask questions!

---

## ⚙️ Configuration

### Environment Variables

Create `backend/app/.env`:

```env
# Database
DATABASE_URL=postgresql://postgres:postgres@db:5432/enterprise_assistant

# ChromaDB
CHROMA_HOST=chromadb
CHROMA_PORT=8000

# JWT Configuration
JWT_SECRET=your-super-secret-key-change-in-production
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24

# Google OAuth (Optional)
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
GOOGLE_REDIRECT_URI=http://localhost:8000/auth/callback

# Ollama LLM (Optional)
OLLAMA_HOST=http://host.docker.internal:11434
OLLAMA_MODEL=llama2

# Embeddings
EMBEDDING_MODEL=all-MiniLM-L6-v2
```

### Supported Departments

The system supports 10 departments:
- HR
- Finance
- Engineering
- Sales
- Marketing
- IT
- Operations
- Legal
- Support
- Admin

---

## 📖 User Guide

### Login Options

1. **Google OAuth**: Click "Continue with Google" for SSO
2. **Email/Password**: Use credentials provided by admin

### Dashboard Features

| Feature | Description |
|---------|-------------|
| **💬 Chat** | Ask questions, get AI-powered answers |
| **📚 Knowledge Base** | View available documents |
| **👤 Profile** | View your account details |

### Asking Questions

1. Type your question in the chat input
2. The AI searches relevant documents (your department + common)
3. Receive an answer based on company knowledge
4. If insufficient context, the query may be escalated

### What You Can Access

- **Common Documents**: Company handbook, security policies, etc.
- **Department Documents**: Only documents assigned to your department
- **Chat History**: Your conversation is maintained during the session

---

## 🔧 Admin Guide

### Accessing Admin Features

Admins see additional navigation options:
- **📤 Upload** - Add documents to the knowledge base
- **👥 Users** - Manage user accounts

### Managing Users

#### Create New User
1. Go to Admin → Users
2. Fill in: Email, Name, Department, Role
3. Click "Add User"
4. **Copy the generated password** (shown only once!)
5. Share credentials securely with the new user

#### Edit User
1. Click "Edit" on a user row
2. Modify department or role
3. Click "Save"

#### Delete User
1. Click "Delete" on a user row
2. Confirm deletion

### Uploading Documents

#### Document Categories

| Category | Visibility | Use Case |
|----------|------------|----------|
| 🌐 Common | All users | Company policies, handbooks |
| 🏢 Department | Specific dept only | Department guides, procedures |

#### Upload Process
1. Go to Admin → Upload
2. Select a file (.txt, .md, .pdf)
3. Enter document name
4. Choose category (Common or Department)
5. If Department, select the target department
6. Set version (e.g., "1.0")
7. Click "Upload Document"

### Managing Knowledge Base

1. Go to Knowledge Base
2. View all accessible documents
3. Use "Select All" for bulk operations
4. Delete outdated documents as needed

---

## 📡 API Reference

### Authentication

#### Google OAuth Login
```http
GET /auth/login
```
Redirects to Google OAuth consent screen.

#### Google OAuth Callback
```http
GET /auth/callback?code={authorization_code}
```
Handles OAuth callback, returns JWT token.

#### Standard Login
```http
POST /auth/token
Content-Type: application/x-www-form-urlencoded

username={email}&password={password}
```

### User Management (Admin)

#### List Users
```http
GET /admin/users/list
Authorization: Bearer {token}
```

#### Add User
```http
POST /admin/users/add
Authorization: Bearer {token}
Content-Type: application/json

{
  "email": "user@example.com",
  "name": "John Doe",
  "department": "Engineering",
  "role": "user"
}
```

#### Edit User
```http
PUT /admin/users/edit/{user_id}
Authorization: Bearer {token}
Content-Type: application/json

{
  "department": "Sales",
  "role": "admin"
}
```

#### Delete User
```http
DELETE /admin/users/delete/{user_id}
Authorization: Bearer {token}
```

### Documents

#### Upload Document
```http
POST /documents/ingest
Authorization: Bearer {token}
Content-Type: multipart/form-data

file: {file}
name: "Document Name"
department: "Engineering"
version: "1.0"
category: "department"
```

#### List Documents
```http
GET /documents/list
Authorization: Bearer {token}
```

#### Delete Document
```http
DELETE /documents/delete/{doc_id}
Authorization: Bearer {token}
```

### Question Answering

#### Ask Question
```http
POST /question
Authorization: Bearer {token}
Content-Type: application/json

{
  "question": "What is our PTO policy?"
}
```

### Profile

#### Get Profile
```http
GET /profile
Authorization: Bearer {token}
```

---

## 🗄 Database Schema

### PostgreSQL Tables

#### users
| Column | Type | Description |
|--------|------|-------------|
| id | SERIAL | Primary key |
| email | VARCHAR(255) | Unique email |
| name | VARCHAR(255) | Display name |
| department | VARCHAR(100) | User's department |
| role | VARCHAR(50) | 'admin' or 'user' |
| password_hash | VARCHAR(255) | bcrypt hashed password |
| created_at | TIMESTAMP | Account creation time |

### ChromaDB Collections

#### documents
| Metadata Field | Type | Description |
|----------------|------|-------------|
| id | string | "{name}:{version}" |
| department | string | Target department or "common" |
| name | string | Document name |
| version | string | Document version |
| category | string | "common" or "department" |

---

## 🔒 Security

### Authentication Flow

```
User                    Frontend                 Backend                  Google
  │                        │                        │                        │
  ├─── Click Login ───────►│                        │                        │
  │                        ├─── GET /auth/login ───►│                        │
  │                        │                        ├─── OAuth Redirect ────►│
  │                        │                        │                        │
  │◄─────────────────── Redirect to Google ─────────┼────────────────────────┤
  │                        │                        │                        │
  ├─── Login with Google ──┼────────────────────────┼───────────────────────►│
  │                        │                        │                        │
  │◄──────────────────── Callback with code ────────┼────────────────────────┤
  │                        │                        │                        │
  │                        │                        ├◄── Verify code ────────┤
  │                        │                        │                        │
  │                        ├◄── JWT Token ──────────┤                        │
  │◄── Redirect + Token ───┤                        │                        │
  │                        │                        │                        │
```

### Security Features

| Feature | Implementation |
|---------|----------------|
| Password Hashing | bcrypt with salt |
| Session Tokens | JWT with expiration |
| OAuth 2.0 | Google Sign-In |
| Access Control | Role + Department checks |
| Input Validation | Pydantic models |
| SQL Injection | SQLAlchemy ORM |
| CORS | Configured for frontend origin |

### Password Policy

- Minimum 12 characters (auto-generated)
- Includes: uppercase, lowercase, numbers, special characters
- Hashed with bcrypt (72-byte limit handled)
- Never stored in plaintext

---

## 📁 Project Structure

```
enterprise-assistant/
├── docker-compose.yml          # Container orchestration
├── README.md                   # This file
│
├── backend/
│   ├── Dockerfile              # Backend container config
│   └── app/
│       ├── main.py             # FastAPI application entry
│       ├── requirements.txt    # Python dependencies
│       ├── .env                # Environment variables
│       │
│       ├── agents/             # AI/RAG agents
│       │   ├── answer_agent.py
│       │   ├── escalation_agent.py
│       │   ├── policy_agent.py
│       │   └── retrieval_agent.py
│       │
│       ├── auth/               # Authentication
│       │   ├── access_control.py
│       │   ├── google_oauth.py
│       │   ├── jwt_utils.py
│       │   └── password_utils.py
│       │
│       ├── db/                 # Database
│       │   ├── database.py
│       │   ├── models.py
│       │   └── migrations/
│       │
│       ├── routes/             # API endpoints
│       │   ├── admin_users.py
│       │   ├── document_ingestion.py
│       │   ├── password_reset.py
│       │   ├── question_answering.py
│       │   └── register.py
│       │
│       └── services/           # Business logic
│           └── document_ingestion.py
│
├── frontend/
│   ├── Dockerfile              # Frontend container config
│   ├── nginx.conf              # Production web server
│   ├── package.json            # Node dependencies
│   │
│   ├── public/                 # Static assets
│   │   └── index.html
│   │
│   └── src/
│       ├── App.tsx             # Main React component
│       ├── App.css             # Global styles
│       │
│       ├── components/         # React components
│       │   ├── AdminUserManagement.tsx
│       │   ├── Chat.tsx
│       │   ├── DocumentUpload.tsx
│       │   ├── KnowledgeBase.tsx
│       │   └── Profile.tsx
│       │
│       ├── pages/              # Page components
│       │   ├── LoginPage.tsx
│       │   └── ForgotPasswordPage.tsx
│       │
│       ├── services/           # API client
│       │   └── api.ts
│       │
│       └── utils/              # Utilities
│           └── jwt.ts
│
└── data/
    └── documents/              # Sample documents
        ├── common_company_handbook.txt
        ├── common_security_policy.txt
        ├── hr_leave_policy.txt
        ├── engineering_coding_standards.txt
        └── ... (more sample docs)
```

---

## 💻 Development

### Local Development (Without Docker)

#### Backend
```bash
cd backend/app
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

#### Frontend
```bash
cd frontend
npm install
npm start
```

### Running Tests

```bash
# Backend tests
cd backend/app
pytest tests/

# Frontend tests
cd frontend
npm test
```

### Code Style

- **Python**: PEP 8, Black formatter
- **TypeScript**: ESLint, Prettier
- **Commits**: Conventional Commits

---

## 🔍 Troubleshooting

### Common Issues

#### "Connection refused" to backend
```bash
# Check if containers are running
docker-compose ps

# View backend logs
docker-compose logs backend
```

#### "OAuth redirect mismatch"
- Ensure `GOOGLE_REDIRECT_URI` matches Google Console settings
- Check frontend is accessible at the configured origin

#### "Document not found" in chat
- Verify document was uploaded with correct category
- Check user's department matches document department
- Common documents should have `category: "common"`

#### "Invalid password" after reset
- Passwords are hashed with bcrypt (72-byte limit)
- Ensure using the complete generated password

### Viewing Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend

# Application logs
cat backend/logs/feature_log.txt
```

### Rebuilding Containers

```bash
# Rebuild and restart all
docker-compose up --build -d

# Rebuild specific service
docker-compose up --build backend -d

# Full reset (removes data!)
docker-compose down -v
docker-compose up --build -d
```

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines

- Write tests for new features
- Update documentation
- Follow existing code style
- Keep commits atomic and descriptive

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- [FastAPI](https://fastapi.tiangolo.com/) - Modern Python web framework
- [React](https://reactjs.org/) - UI library
- [ChromaDB](https://www.trychroma.com/) - Vector database
- [SentenceTransformers](https://www.sbert.net/) - Embeddings
- [Ollama](https://ollama.ai/) - Local LLM runtime

---

<div align="center">

**Built with ❤️ for Enterprise Knowledge Management**

[⬆ Back to Top](#-enterprise-knowledge-assistant)

</div>
