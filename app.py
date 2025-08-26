from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from functools import wraps
import os
from dotenv import load_dotenv
import logging
from flask_migrate import Migrate
import uuid
import boto3

# Cargar variables de entorno desde .env
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "default_secret_key")
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("SQLALCHEMY_DATABASE_URI")
app.config["UPLOAD_FOLDER"] = os.getenv("UPLOAD_FOLDER", os.path.join("static", "uploads"))
db = SQLAlchemy(app)
migrate = Migrate(app, db)


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
    username = db.Column(db.String(50))
    descripcion = db.Column(db.Text)  # Nuevo campo
    score = db.Column(db.Integer, default=2)  # Nuevo campo, inicia en 2
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

# Configuración de entorno y S3
env = os.getenv("FLASK_ENV", "development")
S3_BUCKET = os.getenv("S3_BUCKET")
S3_REGION = os.getenv("S3_REGION")
S3_ACCESS_KEY = os.getenv("S3_ACCESS_KEY")
S3_SECRET_KEY = os.getenv("S3_SECRET_KEY")

def save_image(file):
    ext = os.path.splitext(file.filename)[1]
    unique_filename = f"{uuid.uuid4().hex}{ext}"
    if True: #env == "development":
        # Guardar localmente
        full_path = os.path.join(app.config["UPLOAD_FOLDER"], unique_filename)
        file.save(full_path)
        return os.path.join("uploads", unique_filename)
    else:
        # Guardar en S3
        s3 = boto3.client(
            "s3",
            region_name=S3_REGION,
            aws_access_key_id=S3_ACCESS_KEY,
            aws_secret_access_key=S3_SECRET_KEY
        )
        s3.upload_fileobj(
            file,
            S3_BUCKET,
            unique_filename,
            ExtraArgs={"ACL": "public-read", "ContentType": file.content_type}
        )
        # URL pública de la imagen en S3
        return f"https://{S3_BUCKET}.s3.{S3_REGION}.amazonaws.com/{unique_filename}"


# ---------- RUTAS ----------
@app.route("/", methods=["GET", "POST"])
@login_required
def index():
    posts = Post.query.all()
    # Ordenar primero por score (desc), luego por cantidad de likes (desc)
    posts = sorted(posts, key=lambda p: (-p.score, -len(p.likes)))
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

        # Ya no se analiza el título con IA
        score = 2
        justificacion = "Justificación no disponible."

        # Guardar imagen según entorno
        image_path = None
        if file and file.filename != "":
            image_path = save_image(file)

        # Crear nueva publicación con el nombre de usuario
        new_post = Post(
            title=descripcion[:50],
            image_path=image_path,
            username=session["username"],
            descripcion=justificacion,
            score=score
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

@app.route("/like_ajax/<int:post_id>", methods=["POST"])
@login_required
def like_post_ajax(post_id):
    if "username" not in session:
        return jsonify({"success": False, "error": "No login"})
    existing_like = Like.query.filter_by(post_id=post_id, username=session["username"]).first()
    if not existing_like:
        new_like = Like(post_id=post_id, username=session["username"])
        db.session.add(new_like)
        db.session.commit()
        liked = True
    else:
        db.session.delete(existing_like)
        db.session.commit()
        liked = False
    likes_count = Like.query.filter_by(post_id=post_id).count()
    return jsonify({"success": True, "likes": likes_count, "liked": liked})

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
    post = Post.query.get_or_404(post_id)
    is_admin = session.get("is_admin")
    username = session.get("username")
    # Permite eliminar si es admin o el autor
    if not (is_admin or post.username == username):
        return redirect(url_for("index"))
    db.session.delete(post)
    db.session.commit()
    return redirect(url_for("index"))

@app.route("/delete_comment/<int:comment_id>", methods=["POST"])
@login_required
def delete_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    is_admin = session.get("is_admin")
    username = session.get("username")
    # Permite eliminar si es admin o el autor
    if not (is_admin or comment.username == username):
        return redirect(url_for("index"))
    db.session.delete(comment)
    db.session.commit()
    return redirect(url_for("index"))

@app.route("/update_score/<int:post_id>", methods=["POST"])
@login_required
def update_score(post_id):
    if not session.get("is_admin"):
        flash("Solo el administrador puede modificar el puntaje.")
        return redirect(url_for("index"))
    post = Post.query.get_or_404(post_id)
    try:
        score = int(request.form.get("score", 5))
        if 0 <= score <= 5:
            post.score = score
            db.session.commit()
            flash("Puntaje actualizado.")
        else:
            flash("El puntaje debe estar entre 0 y 5.")
    except Exception:
        flash("Error al actualizar el puntaje.")
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

@app.cli.command("change-admin-password")
def change_admin_password():
    """Modifica la contraseña de un usuario administrador existente."""
    username = input("Nombre de usuario del admin: ")
    user = User.query.filter_by(username=username, is_admin=True).first()
    if not user:
        print("No existe un administrador con ese nombre de usuario.")
        return
    new_password = input("Nueva contraseña: ")
    user.password_hash = generate_password_hash(new_password)
    db.session.commit()
    print(f"Contraseña actualizada para el administrador '{username}'.")

if __name__ == "__main__":
    # Configuración de logging
    logging.basicConfig(
        level=logging.INFO,  # Cambia a logging.ERROR en producción si prefieres menos información
        format="%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s",
        handlers=[
            logging.FileHandler("app.log"),  # Guarda logs en app.log
            logging.StreamHandler()          # Muestra logs en consola
        ]
    )
    with app.app_context():
        db.create_all()
    env = os.getenv("FLASK_ENV", "development")
    if env == "development":
        app.run(host="0.0.0.0", port=5000, debug=True)
    # En producción, gunicorn/nginx se encargan de ejecutar la app


