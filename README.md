

---

# <TechBlog /> — Programming & Tech Blog Platform

A full-featured, modern blog platform for tech and programming content. Built with Python Flask and MySQL, featuring user authentication, comments, search, and a sleek dark theme.

## ✨ Features

### 👤 User Management
- **Registration & Login**: Secure authentication with hashed passwords
- **Admin Panel**: Special privileges for content management
- **User Roles**: Regular users and administrators

### 📝 Content Management
- **Create Posts**: Write tech articles with ease
- **Edit/Delete**: Full CRUD operations
- **Draft/Published**: Workflow control for content
- **Categories**: Organize posts with color-coded categories
- **View Counter**: Track post popularity

### 💬 Engagement
- **Comments System**: No login required for comments
- **Related Posts**: Automatic suggestions based on categories
- **Search Functionality**: Find content across all posts

### 🎨 Design
- **Dark Theme**: Modern, eye-friendly interface
- **Responsive Layout**: Works on all devices
- **Clean Typography**: Optimized for reading tech content
- **Color-Coded Categories**: Visual organization

### 🔧 Technical Features
- **Password Hashing**: Secure authentication with Werkzeug
- **Session Management**: User sessions
- **Database ORM**: Raw SQL with connection pooling
- **Environment Variables**: Secure configuration

## 🛠️ Tech Stack

### Backend
- **Python 3.8+**: Core programming language
- **Flask**: Web framework
- **MySQL**: Relational database
- **Werkzeug**: Password hashing and utilities

### Frontend
- **Jinja2**: Template engine
- **HTML5/CSS3**: Structure and styling
- **Responsive Design**: Mobile-first approach

### Database
- **MySQL**: Production-ready database
- **phpMyAdmin**: Optional management tool

## ⚙️ Installation & Setup

### Prerequisites
- Python 3.8 or higher
- MySQL Server 5.7+
- phpMyAdmin (optional, for database management)
- pip (Python package manager)

### Step-by-Step Setup

1. **Clone the repository**
```bash
git clone <repository-url>
cd techblog
```

2. **Create a virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Set up the database**
   - Open phpMyAdmin or MySQL command line
   - Run the `schema.sql` file to create:
     - Database structure
     - Tables (users, posts, categories, comments)
     - Default categories

5. **Configure environment variables**
```bash
cp .env.example .env
# Edit .env with your MySQL credentials
```

6. **Run the application**
```bash
python app.py
```

7. **Access the application**
   - Open `http://localhost:5000` in your browser

## 👤 Create Admin User

1. **Register normally**: Visit `/register` and create your account

2. **Grant admin privileges**: In phpMyAdmin, run:
```sql
UPDATE users SET is_admin=1 WHERE username='your_username';
```

Alternatively, use MySQL command line:
```bash
mysql -u root -p techblog
UPDATE users SET is_admin=1 WHERE username='your_username';
```

## 📁 Project Structure

```
techblog/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── schema.sql            # Database schema
├── .env                   # Environment variables (not in repo)
├── .env.example          # Example environment file
├── static/               # Static assets
│   ├── css/
│   │   └── style.css     # Custom styles
│   └── images/
├── templates/            # Jinja2 templates
│   ├── base.html         # Base layout with navigation
│   ├── home.html         # Public home page
│   ├── dashboard.html    # Admin dashboard
│   ├── post_form.html    # Create/Edit post form
│   ├── post_detail.html  # Single post view
│   ├── register.html     # User registration
│   ├── login.html        # User login
│   └── search.html       # Search results page
└── uploads/              # Uploaded media (if enabled)
```

## 🗄️ Database Schema

### Users Table
```sql
CREATE TABLE users (
    user_id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    is_admin BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Posts Table
```sql
CREATE TABLE posts (
    post_id INT PRIMARY KEY AUTO_INCREMENT,
    title VARCHAR(255) NOT NULL,
    excerpt TEXT,
    content TEXT,
    category_id INT,
    status ENUM('draft', 'published') DEFAULT 'draft',
    views INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (category_id) REFERENCES categories(category_id)
);
```

### Categories Table
```sql
CREATE TABLE categories (
    category_id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL UNIQUE,
    color VARCHAR(7) DEFAULT '#63b3ed',
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Comments Table
```sql
CREATE TABLE comments (
    comment_id INT PRIMARY KEY AUTO_INCREMENT,
    post_id INT NOT NULL,
    author VARCHAR(100) NOT NULL,
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (post_id) REFERENCES posts(post_id) ON DELETE CASCADE
);
```

## 🔗 API Routes

| Route | Method | Description | Auth Required |
|-------|--------|-------------|---------------|
| `/` | GET | Home page with published posts | No |
| `/register` | GET/POST | User registration | No |
| `/login` | GET/POST | User login | No |
| `/logout` | GET | User logout | Yes |
| `/dashboard` | GET | Admin dashboard | Admin |
| `/post/new` | GET/POST | Create new post | Admin |
| `/post/edit/<id>` | GET/POST | Edit existing post | Admin |
| `/post/delete/<id>` | POST | Delete post | Admin |
| `/post/<id>` | GET | View single post | No |
| `/category/<name>` | GET | View posts by category | No |
| `/search` | GET | Search posts | No |
| `/comment/add` | POST | Add comment to post | No |

## 🎨 Features in Detail

### User Authentication
- Secure password hashing with Werkzeug
- Session-based authentication
- Admin role management
- Protected routes

### Content Management
- Rich HTML content support
- Draft/publishing workflow
- Category assignment
- Automatic view counting
- Related posts algorithm

### Comments System
- No login required (open comments)
- Author name required
- Timestamp tracking
- Post-specific threading

### Search Functionality
- Full-text search across titles and content
- Category filtering
- Real-time results

### Dark Theme UI
- Eye-friendly dark color scheme
- Responsive design
- Typography optimized for technical content
- Color-coded categories

## 🔒 Security Features

- **Password Hashing**: bcrypt-style hashing with Werkzeug
- **SQL Injection Protection**: Parameterized queries
- **CSRF Protection**: Form validation
- **Session Security**: Secure cookie handling
- **Input Sanitization**: Safe HTML rendering
- **Admin Only Routes**: Protected with decorators

## 🚀 Deployment

### Local Development
```bash
python app.py
```

### Production (with Gunicorn)
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### With Nginx (Recommended)
1. Set up Gunicorn as WSGI server
2. Configure Nginx as reverse proxy
3. Set environment variables properly
4. Use SSL/TLS for production

## 📊 Performance Optimization

- Database indexing on foreign keys
- Query optimization
- Caching strategies (future implementation)
- Asset compression

## 🔧 Troubleshooting

### Common Issues

**Database Connection Error**
```bash
# Check MySQL is running
sudo systemctl status mysql  # Linux
# Or
mysql -u root -p  # Test connection
```

**Port 5000 Already in Use**
```bash
# Change port in app.py or use:
python app.py --port=5001
```

**Missing Dependencies**
```bash
pip install -r requirements.txt
```

**Environment Variables Not Loading**
```bash
pip install python-dotenv
```

**Admin User Not Working**
```sql
-- Check admin status
SELECT username, is_admin FROM users;
-- Update if needed
UPDATE users SET is_admin=1 WHERE username='your_username';
```

## 📝 Future Enhancements

- [ ] Rich text editor (CKEditor/TinyMCE)
- [ ] Image upload for posts
- [ ] User profiles
- [ ] Email notifications
- [ ] RSS feeds
- [ ] Social media sharing
- [ ] Post scheduling
- [ ] Newsletter integration
- [ ] Analytics dashboard
- [ ] Export/import functionality
- [ ] Tags system
- [ ] Multi-language support
- [ ] API endpoints (RESTful)
- [ ] Mobile app integration

## 🌍 Browser Support

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+
- Opera 76+

## 📄 License

MIT License - Feel free to use, modify, and distribute as needed.

## 🙏 Credits

**Developer & Designer**
- **Tasimbiswa Kandemiiri**
- Year 2 Software Engineering Student
- **TelOne Centre for Learning**
- Harare, Zimbabwe

**Third-Party Libraries**
- **Flask**: Web framework
- **Werkzeug**: Password hashing and utilities
- **MySQL Connector**: Database connectivity
- **python-dotenv**: Environment variable management

**Special Thanks**
- All users and contributors
- Tech community for inspiration
- TelOne Centre for Learning for support

---

**<TechBlog /> — Where developers share knowledge**

© 2026 Tasimbiswa Kandemiiri • TelOne Centre for Learning, Harare, Zimbabwe

Made with ❤️ and ☕ for the tech community
