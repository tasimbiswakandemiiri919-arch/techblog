

---


# 📘 TechBlog — Programming & Tech Blog Platform

A full-featured, modern blog platform for tech and programming content. Built with **Python Flask** and **PostgreSQL**, featuring user authentication, comments, search, and a sleek dark theme.

---

## 🌐 Live Demo

🔗 **https://techblog--tasimbiswakande.replit.app**

---

## ✨ Features

### 👤 User Management
- **Registration & Login** — Secure authentication with hashed passwords
- **Admin Panel** — Special privileges for content management
- **User Roles** — Regular users and administrators
- **Profile Pages** — Each user has a public profile with their posts

### 📝 Content Management
- **Create Posts** — Write tech articles with a rich text editor
- **Edit/Delete** — Full CRUD operations
- **Draft/Published** — Workflow control for content
- **Categories** — Organize posts with color-coded categories
- **Cover Images** — Add beautiful cover photos to posts
- **View Counter** — Track post popularity
- **Like Button** — Show appreciation for posts

### 💬 Engagement
- **Comments System** — No login required for commenting
- **Related Posts** — Automatic suggestions based on categories
- **Search Functionality** — Find content across all posts
- **Author Pages** — Click any author to see all their posts

### 🎨 Design
- **Dark Theme** — Modern, eye-friendly interface
- **Responsive Layout** — Works on all devices
- **Clean Typography** — Optimized for reading tech content
- **Color-Coded Categories** — Visual organization

### 🔒 Security
- **Password Hashing** — Secure authentication with Werkzeug
- **Session Management** — User sessions
- **Admin Protection** — Admin-only routes and features
- **Input Sanitization** — Safe HTML rendering

---

## 🛠️ Tech Stack

### Backend
| Technology | Purpose |
|------------|---------|
| **Python 3.11+** | Core programming language |
| **Flask** | Web framework |
| **PostgreSQL** | Relational database |
| **Werkzeug** | Password hashing and utilities |
| **psycopg2** | PostgreSQL adapter for Python |

### Frontend
| Technology | Purpose |
|------------|---------|
| **Jinja2** | Template engine |
| **HTML5** | Structure |
| **CSS3** | Styling and dark theme |
| **Responsive Design** | Mobile-first approach |

### Hosting
| Platform | Purpose |
|----------|---------|
| **Replit** | Development and deployment |

---

## 📁 Project Structure

```
techblog/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── .env.example          # Environment variables example
├── .gitignore            # Git ignore file
│
├── static/               # Static assets
│   ├── css/
│   │   └── style.css     # Custom styling
│   └── uploads/          # User uploaded images
│
├── templates/            # Jinja2 templates
│   ├── base.html         # Base layout with navigation
│   ├── home.html         # Public home page
│   ├── dashboard.html    # Admin dashboard
│   ├── post_form.html    # Create/Edit post form
│   ├── post_detail.html  # Single post view
│   ├── register.html     # User registration
│   ├── login.html        # User login
│   ├── search.html       # Search results page
│   ├── profile.html      # User profile page
│   └── admin/            # Admin templates
│       ├── dashboard.html
│       └── users.html
│
└── migrations/           # Database migrations
```

---

## 🚀 Getting Started

### Prerequisites
- Python 3.11 or higher
- PostgreSQL (or use Replit's built-in database)

### Step 1: Clone the Repository
```bash
git clone https://github.com/tasimbiswakandemii919-arch/techblog.git
cd techblog
```

### Step 2: Create a Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Set Up Environment Variables
```bash
cp .env.example .env
# Edit .env with your database credentials
```

### Step 5: Set Up the Database
```bash
# Run the schema.sql file to create tables
psql -U your_username -d your_database -f schema.sql
```

### Step 6: Run the Application
```bash
python app.py
```

### Step 7: Access the Application
- Open `http://localhost:5000` in your browser

---

## 🗄️ Database Schema

### Users Table
```sql
CREATE TABLE users (
    user_id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    is_admin BOOLEAN DEFAULT FALSE,
    is_suspended BOOLEAN DEFAULT FALSE,
    role VARCHAR(20) DEFAULT 'user',
    bio TEXT,
    avatar VARCHAR(255),
    last_login TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Posts Table
```sql
CREATE TABLE posts (
    post_id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    excerpt TEXT,
    content TEXT,
    category_id INT,
    status VARCHAR(20) DEFAULT 'draft',
    image VARCHAR(255),
    views INT DEFAULT 0,
    likes INT DEFAULT 0,
    user_id INT REFERENCES users(user_id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Categories Table
```sql
CREATE TABLE categories (
    category_id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    color VARCHAR(7) DEFAULT '#63b3ed',
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Comments Table
```sql
CREATE TABLE comments (
    comment_id SERIAL PRIMARY KEY,
    post_id INT REFERENCES posts(post_id) ON DELETE CASCADE,
    author VARCHAR(100) NOT NULL,
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## 🔐 Environment Variables

Create a `.env` file with these variables:

```env
FLASK_SECRET_KEY=your-secret-key-here
DATABASE_URL=postgresql://username:password@host:port/database
```

---

## 📝 Creating an Admin User

1. Register normally via `/register`
2. In the database, run:
```sql
UPDATE users SET is_admin = TRUE WHERE username = 'your_username';
```

---

## 🎨 Features in Detail

### Rich Text Editor
- Posts support HTML formatting
- Formatting tips displayed below the content box
- Users can use bold, italic, headings, lists, and links

### Cover Images
- Upload cover images for posts
- Supported formats: PNG, JPG, JPEG, GIF, WEBP
- Max file size: 16MB

### Admin Dashboard
- View site statistics (total users, posts, comments)
- Manage all users
- Edit/delete any post
- View and delete comments

### Search
- Full-text search across post titles and content
- Real-time results

### Mobile Friendly
- Responsive design works on all screen sizes
- Optimized for mobile reading

---

## 👥 Contributors

- **Tasimbiswa Kandemiiri** — Developer & Designer
  - Year 2 Software Engineering Student
  - TelOne Centre for Learning, Harare, Zimbabwe
  - Email: tasimbiswakandemiiri919@gmail.com

---

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

---

## 🙏 Acknowledgments

- **Flask** — Web framework
- **PostgreSQL** — Database
- **Replit** — Hosting platform
- **TelOne Centre for Learning** — Education and support

---

## 📞 Contact

**Tasimbiswa Kandemiiri**
- GitHub: [@tasimbiswakandemii919-arch](https://github.com/tasimbiswakandemii919-arch)
- Email: tasimbiswakandemiiri919@gmail.com
- Location: Harare, Zimbabwe

---

## 🚀 Future Enhancements

- [ ] Email notifications
- [ ] User following system
- [ ] Post scheduling
- [ ] RSS feed
- [ ] Social media sharing
- [ ] Comment moderation
- [ ] User analytics
- [ ] Export/import posts

---

**Made with ❤️ by Tasimbiswa Kandemiiri • TelOne Centre for Learning, Harare, Zimbabwe**

---

*"Code. Learn. Grow."*
```

---

