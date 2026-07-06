from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_mysqldb import MySQL
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from datetime import datetime
import os, re
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'techblog-dev-key')
app.config['MYSQL_HOST']        = os.getenv('MYSQL_HOST', '127.0.0.1')
app.config['MYSQL_PORT']        = int(os.getenv('MYSQL_PORT', 3306))
app.config['MYSQL_USER']        = os.getenv('MYSQL_USER', 'root')
app.config['MYSQL_PASSWORD']    = os.getenv('MYSQL_PASSWORD', '')
app.config['MYSQL_DB']          = os.getenv('MYSQL_DB', 'techblog')
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
mysql = MySQL(app)

def slugify(text):
    text = text.lower().strip()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[\s_-]+', '-', text)
    return text

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in first.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session or not session.get('is_admin'):
            flash('Admin access required.', 'danger')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated

def publish_due_scheduled_posts():
    """Flip any 'scheduled' post whose time has arrived to 'published'.
    Called opportunistically on read-heavy routes (no cron needed)."""
    cur = mysql.connection.cursor()
    cur.execute(
        "UPDATE posts SET status='published' WHERE status='scheduled' AND scheduled_at <= %s",
        (datetime.now(),)
    )
    mysql.connection.commit()
    cur.close()

# ── Public Routes ─────────────────────────────────────────────────────────────

@app.route('/')
def index():
    publish_due_scheduled_posts()
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT p.*, u.username, c.name as cat_name, c.color as cat_color, c.slug as cat_slug
        FROM posts p
        JOIN users u ON p.author_id = u.user_id
        LEFT JOIN categories c ON p.category_id = c.category_id
        WHERE p.status = 'published'
        ORDER BY p.created_at DESC LIMIT 6
    """)
    posts = cur.fetchall()
    cur.execute("SELECT * FROM categories")
    categories = cur.fetchall()
    cur.execute("SELECT COUNT(*) as cnt FROM posts WHERE status='published'")
    post_count = cur.fetchone()['cnt']
    cur.close()
    return render_template('index.html', posts=posts, categories=categories, post_count=post_count)

@app.route('/post/<slug>')
def post_detail(slug):
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT p.*, u.username, u.bio, c.name as cat_name, c.color as cat_color
        FROM posts p
        JOIN users u ON p.author_id = u.user_id
        LEFT JOIN categories c ON p.category_id = c.category_id
        WHERE p.slug = %s AND p.status = 'published'
    """, (slug,))
    post = cur.fetchone()
    if not post:
        flash('Post not found.', 'danger')
        return redirect(url_for('index'))
    # increment views
    cur.execute("UPDATE posts SET views = views + 1 WHERE slug = %s", (slug,))
    mysql.connection.commit()
    # comments
    cur.execute("SELECT * FROM comments WHERE post_id = %s ORDER BY created_at DESC", (post['post_id'],))
    comments = cur.fetchall()
    # related posts
    cur.execute("""
        SELECT p.title, p.slug, p.excerpt, c.color as cat_color, c.name as cat_name
        FROM posts p LEFT JOIN categories c ON p.category_id = c.category_id
        WHERE p.category_id = %s AND p.slug != %s AND p.status='published'
        LIMIT 3
    """, (post['category_id'], slug))
    related = cur.fetchall()
    cur.close()
    return render_template('post_detail.html', post=post, comments=comments, related=related)

@app.route('/post/<slug>/comment', methods=['POST'])
def add_comment(slug):
    cur = mysql.connection.cursor()
    cur.execute("SELECT post_id FROM posts WHERE slug = %s", (slug,))
    post = cur.fetchone()
    if post:
        user_id = session.get('user_id')  # None for guest commenters
        cur.execute(
            "INSERT INTO comments (post_id, user_id, author_name, author_email, content, created_at) VALUES (%s,%s,%s,%s,%s,%s)",
            (post['post_id'], user_id, request.form['name'], request.form['email'],
             request.form['content'], datetime.now())
        )
        mysql.connection.commit()
        flash('Comment added!', 'success')
    cur.close()
    return redirect(url_for('post_detail', slug=slug))

@app.route('/comment/<int:comment_id>/edit', methods=['POST'])
@login_required
def edit_comment(comment_id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM comments WHERE comment_id=%s AND user_id=%s", (comment_id, session['user_id']))
    comment = cur.fetchone()
    if not comment:
        flash("You can only edit your own comments.", 'danger')
        cur.close()
        return redirect(request.referrer or url_for('index'))
    new_content = request.form.get('content', '').strip()
    if new_content:
        cur.execute(
            "UPDATE comments SET content=%s, updated_at=%s WHERE comment_id=%s",
            (new_content, datetime.now(), comment_id)
        )
        mysql.connection.commit()
        flash('Comment updated.', 'success')
    cur.execute("SELECT slug FROM posts WHERE post_id=%s", (comment['post_id'],))
    slug = cur.fetchone()['slug']
    cur.close()
    return redirect(url_for('post_detail', slug=slug))

@app.route('/comment/<int:comment_id>/delete', methods=['POST'])
@login_required
def delete_comment(comment_id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM comments WHERE comment_id=%s AND user_id=%s", (comment_id, session['user_id']))
    comment = cur.fetchone()
    if not comment:
        flash("You can only delete your own comments.", 'danger')
        cur.close()
        return redirect(request.referrer or url_for('index'))
    cur.execute("SELECT slug FROM posts WHERE post_id=%s", (comment['post_id'],))
    slug = cur.fetchone()['slug']
    cur.execute("DELETE FROM comments WHERE comment_id=%s", (comment_id,))
    mysql.connection.commit()
    cur.close()
    flash('Comment deleted.', 'success')
    return redirect(url_for('post_detail', slug=slug))

@app.route('/category/<slug>')
def category(slug):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM categories WHERE slug = %s", (slug,))
    cat = cur.fetchone()
    if not cat:
        return redirect(url_for('index'))
    cur.execute("""
        SELECT p.*, u.username, c.name as cat_name, c.color as cat_color
        FROM posts p JOIN users u ON p.author_id = u.user_id
        LEFT JOIN categories c ON p.category_id = c.category_id
        WHERE p.category_id = %s AND p.status='published'
        ORDER BY p.created_at DESC
    """, (cat['category_id'],))
    posts = cur.fetchall()
    cur.close()
    return render_template('category.html', cat=cat, posts=posts)

@app.route('/search')
def search():
    q          = request.args.get('q', '').strip()
    cat_slug   = request.args.get('category', '').strip()
    author     = request.args.get('author', '').strip()
    date_from  = request.args.get('date_from', '').strip()
    date_to    = request.args.get('date_to', '').strip()

    cur = mysql.connection.cursor()

    conditions = ["p.status='published'"]
    params = []

    if q:
        conditions.append("(p.title LIKE %s OR p.content LIKE %s OR p.excerpt LIKE %s)")
        params += [f'%{q}%', f'%{q}%', f'%{q}%']
    if cat_slug:
        conditions.append("c.slug = %s")
        params.append(cat_slug)
    if author:
        conditions.append("u.username = %s")
        params.append(author)
    if date_from:
        conditions.append("p.created_at >= %s")
        params.append(date_from + ' 00:00:00')
    if date_to:
        conditions.append("p.created_at <= %s")
        params.append(date_to + ' 23:59:59')

    where_clause = " AND ".join(conditions)
    posts = []
    # Only run the query if there's at least one real filter, to avoid dumping
    # the whole blog on a blank /search visit.
    if q or cat_slug or author or date_from or date_to:
        cur.execute(f"""
            SELECT p.*, u.username, c.name as cat_name, c.color as cat_color
            FROM posts p JOIN users u ON p.author_id = u.user_id
            LEFT JOIN categories c ON p.category_id = c.category_id
            WHERE {where_clause}
            ORDER BY p.created_at DESC
        """, tuple(params))
        posts = cur.fetchall()

    cur.execute("SELECT * FROM categories ORDER BY name")
    categories = cur.fetchall()
    cur.execute("SELECT DISTINCT username FROM users ORDER BY username")
    authors = cur.fetchall()
    cur.close()

    return render_template('search.html', posts=posts, query=q, categories=categories,
                           authors=authors, cat_slug=cat_slug, author=author,
                           date_from=date_from, date_to=date_to)

# ── Follows & Feed ─────────────────────────────────────────────────────────────

@app.route('/author/<username>')
def author_profile(username):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM users WHERE username=%s", (username,))
    author = cur.fetchone()
    if not author:
        flash('Author not found.', 'danger')
        cur.close()
        return redirect(url_for('index'))
    cur.execute("""
        SELECT p.*, c.name as cat_name, c.color as cat_color
        FROM posts p LEFT JOIN categories c ON p.category_id = c.category_id
        WHERE p.author_id=%s AND p.status='published' ORDER BY p.created_at DESC
    """, (author['user_id'],))
    posts = cur.fetchall()
    cur.execute("SELECT COUNT(*) as cnt FROM follows WHERE author_id=%s", (author['user_id'],))
    follower_count = cur.fetchone()['cnt']
    is_following = False
    if session.get('user_id'):
        cur.execute("SELECT 1 FROM follows WHERE follower_id=%s AND author_id=%s",
                    (session['user_id'], author['user_id']))
        is_following = cur.fetchone() is not None
    cur.close()
    return render_template('author_profile.html', author=author, posts=posts,
                           follower_count=follower_count, is_following=is_following)

@app.route('/author/<username>/follow', methods=['POST'])
@login_required
def follow_author(username):
    cur = mysql.connection.cursor()
    cur.execute("SELECT user_id FROM users WHERE username=%s", (username,))
    author = cur.fetchone()
    if author and author['user_id'] != session['user_id']:
        cur.execute(
            "INSERT IGNORE INTO follows (follower_id, author_id, created_at) VALUES (%s,%s,%s)",
            (session['user_id'], author['user_id'], datetime.now())
        )
        mysql.connection.commit()
        flash(f'You are now following {username}.', 'success')
    cur.close()
    return redirect(url_for('author_profile', username=username))

@app.route('/author/<username>/unfollow', methods=['POST'])
@login_required
def unfollow_author(username):
    cur = mysql.connection.cursor()
    cur.execute("SELECT user_id FROM users WHERE username=%s", (username,))
    author = cur.fetchone()
    if author:
        cur.execute(
            "DELETE FROM follows WHERE follower_id=%s AND author_id=%s",
            (session['user_id'], author['user_id'])
        )
        mysql.connection.commit()
        flash(f'Unfollowed {username}.', 'success')
    cur.close()
    return redirect(url_for('author_profile', username=username))

@app.route('/feed')
@login_required
def feed():
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT p.*, u.username, c.name as cat_name, c.color as cat_color
        FROM posts p
        JOIN users u ON p.author_id = u.user_id
        JOIN follows f ON f.author_id = p.author_id
        LEFT JOIN categories c ON p.category_id = c.category_id
        WHERE f.follower_id = %s AND p.status='published'
        ORDER BY p.created_at DESC
    """, (session['user_id'],))
    posts = cur.fetchall()
    cur.close()
    return render_template('feed.html', posts=posts)

# ── Auth ──────────────────────────────────────────────────────────────────────

@app.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'POST':
        username = request.form['username'].strip()
        email    = request.form['email'].strip()
        password = request.form['password']
        cur = mysql.connection.cursor()
        cur.execute("SELECT user_id FROM users WHERE username=%s OR email=%s", (username, email))
        if cur.fetchone():
            flash('Username or email already taken.', 'danger')
        else:
            cur.execute(
                "INSERT INTO users (username, email, password_hash, is_admin, created_at) VALUES (%s,%s,%s,%s,%s)",
                (username, email, generate_password_hash(password), False, datetime.now())
            )
            mysql.connection.commit()
            flash('Account created! Please log in.', 'success')
            return redirect(url_for('login'))
        cur.close()
    return render_template('register.html')

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password']
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM users WHERE username=%s", (username,))
        user = cur.fetchone()
        cur.close()
        if user and check_password_hash(user['password_hash'], password):
            session['user_id']  = user['user_id']
            session['username'] = user['username']
            session['is_admin'] = user['is_admin']
            flash(f"Welcome back, {username}!", 'success')
            return redirect(url_for('dashboard'))
        flash('Invalid credentials.', 'danger')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out.', 'success')
    return redirect(url_for('index'))

@app.route('/profile/settings', methods=['GET', 'POST'])
@login_required
def profile_settings():
    cur = mysql.connection.cursor()
    if request.method == 'POST':
        bio          = request.form.get('bio', '').strip()
        avatar_url   = request.form.get('avatar_url', '').strip() or None
        social_links = request.form.get('social_links', '').strip() or None
        cur.execute(
            "UPDATE users SET bio=%s, avatar_url=%s, social_links=%s WHERE user_id=%s",
            (bio, avatar_url, social_links, session['user_id'])
        )
        mysql.connection.commit()
        flash('Profile updated!', 'success')
        cur.close()
        return redirect(url_for('profile_settings'))
    cur.execute("SELECT * FROM users WHERE user_id=%s", (session['user_id'],))
    user = cur.fetchone()
    cur.close()
    return render_template('profile_settings.html', user=user)

# ── Dashboard ─────────────────────────────────────────────────────────────────

@app.route('/dashboard')
@login_required
def dashboard():
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT p.*, c.name as cat_name, c.color as cat_color
        FROM posts p LEFT JOIN categories c ON p.category_id = c.category_id
        WHERE p.author_id = %s ORDER BY p.created_at DESC
    """, (session['user_id'],))
    posts = cur.fetchall()
    cur.execute("SELECT COUNT(*) as cnt FROM posts WHERE author_id=%s AND status='published'", (session['user_id'],))
    pub_count = cur.fetchone()['cnt']
    cur.execute("SELECT COUNT(*) as cnt FROM posts WHERE author_id=%s AND status='draft'", (session['user_id'],))
    draft_count = cur.fetchone()['cnt']
    cur.execute("SELECT SUM(views) as total FROM posts WHERE author_id=%s", (session['user_id'],))
    total_views = cur.fetchone()['total'] or 0
    cur.close()
    return render_template('dashboard.html', posts=posts, pub_count=pub_count,
                           draft_count=draft_count, total_views=total_views)

# ── Post CRUD ─────────────────────────────────────────────────────────────────

@app.route('/post/new', methods=['GET','POST'])
@login_required
def new_post():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM categories")
    categories = cur.fetchall()
    if request.method == 'POST':
        title    = request.form['title'].strip()
        excerpt  = request.form['excerpt'].strip()
        content  = request.form['content'].strip()
        cat_id   = request.form.get('category_id') or None
        status   = request.form.get('status', 'draft')
        scheduled_at = request.form.get('scheduled_at') or None
        if status == 'scheduled' and not scheduled_at:
            status = 'draft'  # can't schedule without a time, fall back safely
        slug     = slugify(title)
        # ensure unique slug
        cur.execute("SELECT post_id FROM posts WHERE slug=%s", (slug,))
        if cur.fetchone():
            slug = slug + '-' + str(int(datetime.now().timestamp()))
        cur.execute(
            "INSERT INTO posts (title,slug,excerpt,content,category_id,author_id,status,scheduled_at,created_at,updated_at) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
            (title, slug, excerpt, content, cat_id, session['user_id'], status, scheduled_at, datetime.now(), datetime.now())
        )
        mysql.connection.commit()
        cur.close()
        flash('Post created!', 'success')
        return redirect(url_for('dashboard'))
    cur.close()
    return render_template('post_form.html', categories=categories, post=None)

@app.route('/post/<int:post_id>/edit', methods=['GET','POST'])
@login_required
def edit_post(post_id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM posts WHERE post_id=%s AND author_id=%s", (post_id, session['user_id']))
    post = cur.fetchone()
    if not post:
        flash('Post not found.', 'danger')
        return redirect(url_for('dashboard'))
    cur.execute("SELECT * FROM categories")
    categories = cur.fetchall()
    if request.method == 'POST':
        status = request.form.get('status', 'draft')
        scheduled_at = request.form.get('scheduled_at') or None
        if status == 'scheduled' and not scheduled_at:
            status = 'draft'
        cur.execute("""
            UPDATE posts SET title=%s, excerpt=%s, content=%s, category_id=%s, status=%s,
                             scheduled_at=%s, updated_at=%s
            WHERE post_id=%s
        """, (request.form['title'], request.form['excerpt'], request.form['content'],
              request.form.get('category_id') or None, status,
              scheduled_at, datetime.now(), post_id))
        mysql.connection.commit()
        flash('Post updated!', 'success')
        return redirect(url_for('dashboard'))
    cur.close()
    return render_template('post_form.html', categories=categories, post=post)

@app.route('/post/<int:post_id>/delete', methods=['POST'])
@login_required
def delete_post(post_id):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM posts WHERE post_id=%s AND author_id=%s", (post_id, session['user_id']))
    mysql.connection.commit()
    cur.close()
    flash('Post deleted.', 'success')
    return redirect(url_for('dashboard'))

# ── Admin ─────────────────────────────────────────────────────────────────────

@app.route('/admin')
@admin_required
def admin():
    cur = mysql.connection.cursor()
    cur.execute("SELECT COUNT(*) as cnt FROM posts")
    total_posts = cur.fetchone()['cnt']
    cur.execute("SELECT COUNT(*) as cnt FROM users")
    total_users = cur.fetchone()['cnt']
    cur.execute("SELECT COUNT(*) as cnt FROM comments")
    total_comments = cur.fetchone()['cnt']
    cur.execute("""
        SELECT p.*, u.username, c.name as cat_name
        FROM posts p JOIN users u ON p.author_id=u.user_id
        LEFT JOIN categories c ON p.category_id=c.category_id
        ORDER BY p.created_at DESC
    """)
    posts = cur.fetchall()
    cur.close()
    return render_template('admin.html', total_posts=total_posts,
                           total_users=total_users, total_comments=total_comments, posts=posts)

if __name__ == '__main__':
    app.run(debug=True)
