# AI Resume Reviewer API

A FastAPI backend for uploading resumes, getting AI-powered reviews, and matching resumes to job descriptions.

---

## 🚀 Features

- **User Management**

  - JWT-based authentication (register/login/logout)
  - User roles: `user` and `admin`
  - Users can view and manage their own resumes and reviews

- **Resume Upload & Parsing**

  - Upload resumes in PDF or DOCX format
  - Automatic text extraction using `pdfminer.six` and `python-docx`
  - Stores file metadata and parsed text in PostgreSQL

- **AI Resume Review**

  - Uses OpenAI-compatible API (via OpenRouter) for resume analysis
  - Extracts key sections, scores resumes, and suggests improvements
  - Returns structured JSON: score, suggestions, summary

- **Job Description Matching**

  - Users can paste a job description to compare with their resume
  - AI highlights matching and missing keywords
  - Provides suggestions to better align the resume with the job

- **Review History & PDF Download**

  - All reviews are stored and can be listed per resume
  - Download AI-reviewed feedback as a formatted PDF

- **Admin Panel**

  - Admin endpoints for viewing all users, resumes, and reviews
  - Usage statistics

- **Security & Validation**

  - File type and size validation
  - Secure JWT-based endpoints
  - Only owners can access or modify their own data

- **Rate Limiting & Background Tasks**
  - Limits resume reviews per user per day
  - AI review and PDF generation run as background tasks

---

## 🛠️ Quickstart

### 1. Clone the repo

```sh
git clone https://github.com/yourusername/ai-resume-reviewer.git
cd ai-resume-reviewer
```

### 2. Install dependencies

```sh
pip install -r requirements.txt
```

### 3. Set up your environment variables

Copy `.env.example` to `.env` and fill in your secrets:

```sh
cp .env.example .env
```

- You must provide your OpenRouter/OpenAI API key and PostgreSQL connection string.

### 4. Set up your database

- Make sure PostgreSQL is running.
- Create a database (e.g. `ai_resume_reviewer`).
- Tables are auto-created on app startup.

### 5. Run the app

```sh
uvicorn app.main:app --reload
```

Visit [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) for the interactive API docs.

---

## ⚙️ Environment Variables

See `.env.example` for all required variables:

- `OPENROUTER_API_KEY` - Your OpenRouter/OpenAI API key
- `SECRET_KEY` - Secret for JWT signing
- `ALGORITHM` - JWT algorithm (e.g. HS256)
- `ACCESS_TOKEN_EXPIRE_MINUTES` - JWT expiry in minutes
- `ADMIN_EMAIL` - The email that will be assigned the admin role on registration
- `SQL_MODEL_DATABASE_URL` - PostgreSQL connection string

---

## 📂 API Endpoints

### Auth

| Method | Endpoint         | Description                |
| ------ | ---------------- | -------------------------- |
| POST   | `/auth/register` | Register new user          |
| POST   | `/auth/login`    | Login and get JWT token    |
| POST   | `/auth/logout`   | Logout (client-side token) |

### Resume

| Method | Endpoint                                          | Description                             |
| ------ | ------------------------------------------------- | --------------------------------------- |
| POST   | `/resume/upload`                                  | Upload a resume file (PDF/DOCX)         |
| GET    | `/resume/resumes`                                 | List all resumes for the logged-in user |
| GET    | `/resume/{resume_id}`                             | Get a specific resume                   |
| GET    | `/resume/{resume_id}/review`                      | Request AI review (rate-limited, async) |
| GET    | `/resume/{resume_id}/reviews`                     | List all reviews for a resume           |
| GET    | `/resume/{resume_id}/review/{review_id}/download` | Download review as PDF                  |

### Job Description Matching

| Method | Endpoint                         | Description                            |
| ------ | -------------------------------- | -------------------------------------- |
| POST   | `/job_match/{resume_id}/match`   | Match resume against a job description |
| GET    | `/job_match/{resume_id}/matches` | List all job matches for a resume      |

### Admin (admin only)

| Method | Endpoint                            | Description               |
| ------ | ----------------------------------- | ------------------------- |
| GET    | `/admin/stats`                      | Get usage statistics      |
| GET    | `/admin/reviews`                    | List all reviews          |
| GET    | `/admin/users`                      | List all users            |
| GET    | `/admin/resumes`                    | List all resumes          |
| GET    | `/admin/user/{user_id}/resumes`     | List resumes for a user   |
| GET    | `/admin/user/{user_id}/reviews`     | List reviews for a user   |
| GET    | `/admin/resume/{resume_id}/reviews` | List reviews for a resume |

---

## 📝 How To Use

1. **Register and Login**

   - Register via `/auth/register`
   - Login via `/auth/login` to get your JWT token

2. **Upload a Resume**

   - Use `/resume/upload` with a PDF or DOCX file

3. **Request an AI Review**

   - Call `/resume/{resume_id}/review`
   - The review is processed in the background; check `/resume/{resume_id}/reviews` for results

4. **Download Review as PDF**

   - Use `/resume/{resume_id}/review/{review_id}/download` to get a formatted PDF

5. **Job Description Matching**

   - POST to `/job_match/{resume_id}/match` with a job description
   - See results and suggestions for alignment

6. **Admin Features**
   - If your email matches `ADMIN_EMAIL`, you get admin access
   - Use `/admin/*` endpoints for stats and management

---

# 📬 Example Requests

**Register:**

```sh
curl -X POST http://localhost:8000/auth/register -H "Content-Type: application/json" -d '{"email":"user@example.com","password":"yourpassword"}'
```

**Login:**

```sh
curl -X POST http://localhost:8000/auth/login -H "Content-Type: application/json" -d '{"email":"user@example.com","password":"yourpassword"}'
```

**Upload Resume:**

```sh
curl -X POST http://localhost:8000/resume/upload -H "Authorization: Bearer <token>" -F "file=@your_resume.pdf"
```

---

## 🛡️ Security & Validation

- Only PDF and DOCX files are accepted for upload
- File size and content are validated
- JWT authentication required for all user endpoints
- Users can only access their own data

---

## 🐳 Docker (optional)

You can add a `Dockerfile` and `docker-compose.yml` for easier setup.  
**Example Dockerfile:**

```dockerfile
FROM python:3.11
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Example docker-compose.yml:**

```yaml
version: "3"
services:
  db:
    image: postgres:15
    environment:
      POSTGRES_DB: ai_resume_reviewer
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: yourpassword
    ports:
      - "5432:5432"
  app:
    build: .
    environment:
      - SQL_MODEL_DATABASE_URL=postgresql://postgres:yourpassword@db/ai_resume_reviewer
      - OPENROUTER_API_KEY=your-openrouter-key
      - SECRET_KEY=your-secret-key
      - ADMIN_EMAIL=admin@example.com
    ports:
      - "8000:8000"
    depends_on:
      - db
```

---

## 🧪 Testing

- Add your tests in the `tests/` directory.
- Run with `pytest` or your preferred test runner.

---

## 🧑‍💻 Tech Stack & Skills Demonstrated

- **Python 3.11+**  
  Modern, type-annotated Python for backend development.

- **FastAPI**  
  High-performance, async web framework for building APIs with automatic OpenAPI/Swagger docs.

- **SQLModel & SQLAlchemy**  
  Modern ORM for defining models, relationships, and database CRUD operations, leveraging SQLAlchemy under the hood.

- **PostgreSQL**  
  Robust, production-grade relational database for storing users, resumes, reviews, and job matches.

- **Authentication & Security**

  - **OAuth2/JWT**: Secure, stateless authentication with role-based access control (`user`, `admin`).
  - **Password Hashing**: Secure password storage using `passlib` and bcrypt.
  - **File Validation**: Strict file type and size checks for uploads.

- **AI Integration**

  - **OpenAI/OpenRouter API**: Integrates with LLMs for resume analysis, scoring, and job description matching.
  - **Prompt Engineering**: Carefully crafted prompts for structured, actionable AI feedback.

- **Document Parsing**

  - **pdfminer.six**: Extracts text from PDF resumes.
  - **python-docx**: Extracts text from DOCX resumes.

- **Background Processing**

  - **FastAPI BackgroundTasks**: Non-blocking, async execution for AI review and PDF generation.

- **PDF Generation**

  - **ReportLab**: Programmatic creation of downloadable, formatted PDF review reports.

- **Admin & User Management**

  - **Role-based Endpoints**: Separate admin/user APIs, with admin dashboards and stats.

- **Rate Limiting**

  - Per-user, per-day review limits to prevent abuse.

- **Docker (optional)**

  - Containerization for easy deployment and reproducibility.

- **Testing**

  - Project structure ready for `pytest` and automated testing.

- **DevOps Ready**
  - `.env`-based configuration, requirements management, and example Docker setup.

---

**Skillset demonstrated:**

- Modern Python backend development
- API design and documentation
- Secure authentication and authorization
- AI/LLM integration and prompt engineering
- File handling and validation
- Asynchronous programming and background task management
- Database modeling and ORM usage
- PDF report generation
- Containerization and deployment best practices
- Clean code organization and scalable architecture

---

## 🤝 Contributing

Pull requests are welcome! For major changes, please open an issue first to discuss what you would like to change.

---

## 📄 License

MIT
