# CIU SnapAttend

CIU SnapAttend is a JWT-secured class attendance management web app designed for instructors at Cyprus International University. It simplifies classroom attendance tracking with features like real-time status updates, filtering, statistics, and CSV exports — all in a clean and intuitive interface.

# [DeepWiki](https://deepwiki.com/abdomody35/ciu-hackathon)

check the documentation of the project

---

## 🚀 Features

### 🔐 Authentication System
- **JWT-based Login** – Secure access using JSON Web Tokens.
- **Protected Routes** – Unauthorized users are redirected to the login page.
- **Session Persistence** – Auth state is stored in `localStorage`.
- **Logout Functionality** – Clean session management.

### 🧑‍🏫 Main Pages

#### 🔓 Login Page
- Clean UI with email/password fields.
- **Default credentials:**  
  `instructor@ciu.edu` / `password`
- Stores JWT token upon successful login.
- Redirects to Dashboard.

#### 📋 Dashboard Page
- Grid of classroom cards showing:
  - Class name, code, location, schedule
  - Student count
- Two main actions:
  - **View Classroom** – Opens detailed class page
  - **Record Attendance** – Sends attendance data to API

#### 🏫 Classroom Detail Page
- Top navigation bar with instructor profile and logout
- Stats panel showing:
  - Total students, present, absent, attendance rate
- Filtering tools:
  - Search by student
  - Filter by month and status
- Interactive student table with:
  - Attendance records
  - Manual status updates: Present, Absent, Late
- Export to CSV

---

## ⚙️ Technical Overview

### 📂 State Management
- **React Query (TanStack Query)** – Efficient data fetching and caching
- **React useState** – UI-level state
- **Context API** – Global auth state

### 🔌 API Integration
- Custom fetch wrapper with automatic JWT header injection
- Global error handling using toast notifications
- Mock API setup for demonstration

### 🧹 Components
- **Navbar** – Logo + profile dropdown
- **ClassCard** – Displays class info with actions
- **StatsPanel** – Shows attendance metrics
- **FilterPanel** – Search and filters
- **StudentTable** – Sortable, filterable student list with status updates

---

## 🧽 How It Works

### 1. Authentication Flow
- Login with credentials → JWT saved to `localStorage`
- All API calls include JWT in headers
- Routes are protected based on auth state

### 2. Dashboard
- Auth-guarded route
- Fetches and displays classrooms via React Query

### 3. Classroom Page
- Fetches students and attendance records
- Supports filtering, sorting, and manual updates
- Updates trigger API mutations and UI re-renders

---

## 📦 Setup & Run Locally

```bash
# Clone the repository
git clone https://github.com/your-username/ciu-snapattend.git
cd ciu-snapattend

# Install dependencies
npm install

# Start development server
npm run dev

# Install backend dependencies
cd backend
pip install -r requirements.txt

# run the api
python main.py
```

## 💡 Ensure you have Node.js and npm installed on your system
   
## Set up the PostgreSQL database:

- Configure the .env file with your database credentials:
  ```
  DB_NAME=<your-database-name>
  DB_USER=<your-database-username>
  DB_PASSWORD=<your-database-password>
  DB_HOST=<your-database-host>
  DB_PORT=<your-databse-port>
  ```
- Start the database container using Docker Compose:
  ```bash
  docker-compose up -d
  ```
- Apply the schema and seed data:
  ```bash
   psql -U <DB_USER> -d <DB_NAME> -f schema.sql
   psql -U <DB_USER> -d <DB_NAME> -f seed.sql
  ```
  [learn how to run commands on docker containers](https://docs.docker.com/reference/cli/docker/container/exec/)

## References
- [https://ijsret.com/wp-content/uploads/2025/03/IJSRET_V11_issue2_473.pdf](https://ijsret.com/wp-content/uploads/2025/03/IJSRET_V11_issue2_473.pdf)
- [https://www.researchgate.net/publication/328377150_On_the_Technologies_and_Systems_for_Student_Attendance_Tracking](https://www.researchgate.net/publication/328377150_On_the_Technologies_and_Systems_for_Student_Attendance_Tracking)
- [https://www.tandfonline.com/doi/full/10.1080/08839514.2022.2083796#abstract](https://www.tandfonline.com/doi/full/10.1080/08839514.2022.2083796#abstract)
