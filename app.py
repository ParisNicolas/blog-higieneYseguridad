#mysql+pymysql://root:@localhost/reportes_db
from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from flask_sqlalchemy import SQLAlchemy
import os
from datetime import datetime
from functools import wraps

app = Flask(__name__)
app.secret_key = "super_secret_key"  # Cambiar en producción

# Base de datos MySQL
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:@localhost/reportes_db"
app.config["UPLOAD_FOLDER"] = os.path.join("static", "uploads")
db = SQLAlchemy(app)

# ---------- MODELOS ----------
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True)
    password_hash = db.Column(db.String(200))
    is_admin = db.Column(db.Boolean, default=False)

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200))
    image_path = db.Column(db.String(300))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    username = db.Column(db.String(50))  # Nuevo campo
    likes = db.relationship("Like", backref="post", lazy=True)
    comments = db.relationship("Comment", backref="post", lazy=True)

class Like(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey("post.id"))
    username = db.Column(db.String(50))

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey("post.id"))
    username = db.Column(db.String(50))
    text = db.Column(db.String(300))

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get("username"):
            flash("Debes iniciar sesión para acceder.")
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated_function

# ---------- RUTAS ----------
@app.route("/", methods=["GET", "POST"])
@login_required
def index():
    posts = Post.query.all()
    posts = sorted(posts, key=lambda p: len(p.likes), reverse=True)
    logged_in_user = session.get("username")
    is_admin = session.get("is_admin", False)
    return render_template("index.html", posts=posts, logged_in_user=logged_in_user, is_admin=is_admin)

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        session["username"] = username
        session["is_admin"] = False
        return redirect(url_for("index"))
    return render_template("login.html")

@app.route("/admin_login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        username = request.form["admin_user"]
        password = request.form["admin_pass"]
        user = User.query.filter_by(username=username, is_admin=True).first()
        if user and check_password_hash(user.password_hash, password):
            session["username"] = username
            session["is_admin"] = True
            return redirect(url_for("index"))
        else:
            flash("Usuario o contraseña incorrectos")
    return redirect(url_for("login"))

@app.route("/nuevo_post", methods=["GET", "POST"])
@login_required
def nuevo_post():
    if "username" not in session:
        flash("Debes iniciar sesión para crear un reporte")
        return redirect(url_for("login"))

    if request.method == "POST":
        descripcion = request.form["descripcion"]
        file = request.files["file"]

        # Guardar imagen
        image_path = None
        if file and file.filename != "":
            filename = secure_filename(file.filename)
            full_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            file.save(full_path)
            image_path = os.path.join("uploads", filename)

        # Crear nueva publicación con el nombre de usuario
        new_post = Post(
            title=descripcion[:50],
            image_path=image_path,
            username=session["username"]  # Guardar el usuario
        )
        db.session.add(new_post)
        db.session.commit()

        flash("Reporte subido con éxito")
        return redirect(url_for("index"))

    return render_template("nuevo_post.html")

@app.route("/like/<int:post_id>", methods=["POST"])
@login_required
def like_post(post_id):
    if "username" not in session:
        return redirect(url_for("login"))
    existing_like = Like.query.filter_by(post_id=post_id, username=session["username"]).first()
    if not existing_like:
        new_like = Like(post_id=post_id, username=session["username"])
        db.session.add(new_like)
        db.session.commit()
    return redirect(url_for("index"))

@app.route("/comment/<int:post_id>", methods=["POST"])
@login_required
def comment_post(post_id):
    if "username" not in session:
        return redirect(url_for("login"))
    text = request.form["comment_text"]
    if text.strip():
        new_comment = Comment(post_id=post_id, username=session["username"], text=text)
        db.session.add(new_comment)
        db.session.commit()
    return redirect(url_for("index"))

@app.route("/delete/<int:post_id>", methods=["POST"])
@login_required
def delete_post(post_id):
    if not session.get("is_admin"):
        return redirect(url_for("index"))
    post = Post.query.get_or_404(post_id)
    db.session.delete(post)
    db.session.commit()
    return redirect(url_for("index"))

@app.route("/delete_comment/<int:comment_id>", methods=["POST"])
@login_required
def delete_comment(comment_id):
    if not session.get("is_admin"):
        return redirect(url_for("index"))
    comment = Comment.query.get_or_404(comment_id)
    db.session.delete(comment)
    db.session.commit()
    return redirect(url_for("index"))

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

@app.cli.command("create-admin")
def create_admin():
    """Crea un usuario administrador desde la terminal."""
    username = input("Nombre de usuario: ")
    password = input("Contraseña: ")
    if User.query.filter_by(username=username).first():
        print("El usuario ya existe.")
        return
    new_admin = User(username=username, password_hash=generate_password_hash(password), is_admin=True)
    db.session.add(new_admin)
    db.session.commit()
    print(f"Administrador '{username}' creado exitosamente.")

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(host="0.0.0.0", port=5000)
