# <TechBlog /> — Programming & Tech Blog Platform

A full-stack blog platform for tech and programming content. Built with Python Flask + MySQL.

## ✨ Features
- User registration & login (hashed passwords)
- Create, edit, delete blog posts
- Draft / Published status
- Categories with colour coding
- Comments system (no login required)
- Search across all posts
- Related posts
- View counter
- Admin panel
- Responsive dark theme UI

## 🛠️ Tech Stack
- **Backend:** Python, Flask
- **Database:** MySQL
- **Frontend:** Jinja2, HTML, CSS
- **Auth:** Werkzeug password hashing

## ⚙️ Setup
1. Run `schema.sql` in phpMyAdmin to create database and categories
2. Copy `.env.example` to `.env` and fill in your MySQL details
3. Install dependencies: `pip install -r requirements.txt`
4. Run: `python app.py`
5. Visit: `http://localhost:5000`

## 👤 Create Admin User
Register normally via `/register`, then in phpMyAdmin run:
```sql
UPDATE users SET is_admin=1 WHERE username='your_username';
```

## 🌍 Built By
Tasimbiswa Kandemiiri — Year 2 Software Engineering student, TelOne Centre for Learning, Harare, Zimbabwe.
