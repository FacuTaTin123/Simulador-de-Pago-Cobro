import os
from datetime import datetime

from dotenv import load_dotenv
from flask import Flask, abort, flash, redirect, render_template, request, session, url_for
from flask_login import LoginManager, UserMixin, current_user, login_required, login_user, logout_user
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash, generate_password_hash

load_dotenv()  # lee el archivo .env (MP_ACCESS_TOKEN, SECRET_KEY)

import mp  # noqa: E402  (después de load_dotenv)
from forms import LoginForm, ProductForm, RegisterForm  # noqa: E402

app = Flask(__name__)
app.config.update(
    SECRET_KEY=os.environ.get("SECRET_KEY", "aguantetalleres"),
    SQLALCHEMY_DATABASE_URI="sqlite:///pixel_store.db",
    SQLALCHEMY_TRACK_MODIFICATIONS=False,
)
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = "login"


# ---------------------------------------------------------------- MODELOS
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    orders = db.relationship("Order", backref="user", lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    genre = db.Column(db.String(80), nullable=False)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    description = db.Column(db.Text, default="")
    orders = db.relationship("OrderItem", backref="product", lazy=True)


class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    status = db.Column(db.String(30), default="pendiente de pago", nullable=False)
    total = db.Column(db.Numeric(10, 2), nullable=False)
    items = db.relationship("OrderItem", backref="order", lazy=True, cascade="all, delete-orphan")
    payment = db.relationship("Payment", backref="order", uselist=False)


class OrderItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey("order.id"), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey("product.id"), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    unit_price = db.Column(db.Numeric(10, 2), nullable=False)


class Payment(db.Model):
    """Pago confirmado por Mercado Pago."""
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey("order.id"), nullable=False)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    status = db.Column(db.String(30), default="pendiente", nullable=False)
    method = db.Column(db.String(50))
    mp_payment_id = db.Column(db.String(40))
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))


# ---------------------------------------------------------------- UTILIDADES
def seed_products():
    if Product.query.first():
        return
    db.session.add_all([
        Product(name="Orbit Runner", genre="AVENTURA · INDIE", price=12500, description="Exploración espacial."),
        Product(name="Neon Drift", genre="CARRERAS · ARCADE", price=9800, description="Carreras de neón."),
        Product(name="Wild Tales", genre="EXPLORACIÓN · RPG", price=15000, description="Aventura salvaje."),
        Product(name="Block Shift", genre="PUZZLE · CASUAL", price=6500, description="Desafíos de lógica."),
    ])
    db.session.commit()


def current_cart():
    return session.get("cart", {})


def own_order_or_403(order_id):
    order = db.get_or_404(Order, order_id)
    if order.user_id != current_user.id:
        abort(403)
    return order


with app.app_context():
    db.create_all()
    seed_products()


# ---------------------------------------------------------------- AUTH Y CATÁLOGO
@app.route("/")
def home():
    return render_template("home.html", products=Product.query.order_by(Product.id).all())


@app.route("/registro", methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        if User.query.filter((User.username == form.username.data) | (User.email == form.email.data)).first():
            flash("El usuario o correo ya está registrado.", "error")
        else:
            user = User(username=form.username.data, email=form.email.data)
            user.set_password(form.password.data)
            db.session.add(user)
            db.session.commit()
            login_user(user)
            flash("Cuenta creada.", "success")
            return redirect(url_for("home"))
    return render_template("auth_form.html", form=form, title="Crear cuenta")


@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            return redirect(request.args.get("next") or url_for("home"))
        flash("Correo o contraseña incorrectos.", "error")
    return render_template("auth_form.html", form=form, title="Iniciar sesión")


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("home"))


@app.route("/productos", methods=["GET", "POST"])
@login_required
def products():
    form = ProductForm()
    if form.validate_on_submit():
        db.session.add(Product(name=form.name.data, genre=form.genre.data,
                               price=form.price.data, description=form.description.data))
        db.session.commit()
        flash("Producto agregado.", "success")
        return redirect(url_for("products"))
    return render_template("products.html", form=form, products=Product.query.all())


@app.route("/productos/<int:product_id>/editar", methods=["GET", "POST"])
@login_required
def edit_product(product_id):
    product = db.get_or_404(Product, product_id)
    form = ProductForm(obj=product)
    if form.validate_on_submit():
        form.populate_obj(product)
        db.session.commit()
        return redirect(url_for("products"))
    return render_template("edit_product.html", form=form, product=product)


@app.post("/productos/<int:product_id>/eliminar")
@login_required
def delete_product(product_id):
    db.session.delete(db.get_or_404(Product, product_id))
    db.session.commit()
    return redirect(url_for("products"))


# ---------------------------------------------------------------- CARRITO
@app.post("/carrito/agregar/<int:product_id>")
def add_to_cart(product_id):
    db.get_or_404(Product, product_id)
    cart = current_cart()
    key = str(product_id)
    cart[key] = cart.get(key, 0) + 1
    session["cart"] = cart
    return redirect(url_for("cart"))


@app.route("/carrito")
def cart():
    quantities = current_cart()
    products = Product.query.filter(Product.id.in_([int(k) for k in quantities])).all() if quantities else []
    items = [(p, quantities[str(p.id)]) for p in products]
    total = sum(p.price * q for p, q in items)
    return render_template("cart.html", items=items, total=total)


@app.post("/carrito/quitar/<int:product_id>")
def remove_from_cart(product_id):
    cart = current_cart()
    cart.pop(str(product_id), None)
    session["cart"] = cart
    return redirect(url_for("cart"))


# ---------------------------------------------------------------- PEDIDOS Y PAGOS
@app.post("/pedidos/crear")
@login_required
def create_order():
    quantities = current_cart()
    products = Product.query.filter(Product.id.in_([int(k) for k in quantities])).all() if quantities else []
    if not products:
        flash("El carrito está vacío.", "error")
        return redirect(url_for("cart"))
    total = sum(p.price * quantities[str(p.id)] for p in products)
    order = Order(user_id=current_user.id, total=total)
    db.session.add(order)
    db.session.flush()
    for p in products:
        db.session.add(OrderItem(order_id=order.id, product_id=p.id,
                                 quantity=quantities[str(p.id)], unit_price=p.price))
    db.session.commit()
    session["cart"] = {}
    return redirect(url_for("checkout", order_id=order.id))


@app.route("/pagos/<int:order_id>")
@login_required
def checkout(order_id):
    """Resumen del pedido con el botón de Mercado Pago (comprobar.html)."""
    order = own_order_or_403(order_id)
    if order.status == "pagado":
        return redirect(url_for("payment_success", order_id=order.id))
    return render_template("comprobar.html", order=order)


@app.post("/pagos/<int:order_id>/mercadopago")
@login_required
def pay_with_mercadopago(order_id):
    """Crea la preferencia en Mercado Pago y redirige al checkout de MP."""
    order = own_order_or_403(order_id)
    if order.status == "pagado":
        return redirect(url_for("payment_success", order_id=order.id))
    try:
        preferencia = mp.crear_preferencia(order, request.host_url.rstrip("/"))
    except Exception as error:
        app.logger.error("Error con Mercado Pago: %s", error)
        flash("No pudimos iniciar el pago con Mercado Pago. Revisá la configuración.", "error")
        return redirect(url_for("checkout", order_id=order.id))
    return redirect(preferencia["init_point"])


@app.route("/pagos/retorno")
@login_required
def payment_return():
    """Mercado Pago vuelve acá. El resultado se verifica contra la API, no contra la URL."""
    payment_id = request.args.get("payment_id")
    order = own_order_or_403(int(request.args.get("external_reference", 0) or 0))

    if order.status == "pagado":
        return redirect(url_for("payment_success", order_id=order.id))

    info = mp.obtener_pago(payment_id) if payment_id and payment_id != "null" else None
    if not info or info.get("external_reference") != str(order.id):
        flash("No pudimos verificar el pago. Intentá de nuevo.", "error")
        return redirect(url_for("checkout", order_id=order.id))

    if info["status"] == "approved" and abs(float(info["transaction_amount"]) - float(order.total)) < 0.01:
        db.session.add(Payment(order_id=order.id, amount=order.total, status="aprobado",
                               method=f"Mercado Pago · {info.get('payment_method_id', 'tarjeta')}",
                               mp_payment_id=str(info["id"])))
        order.status = "pagado"
        db.session.commit()
        return redirect(url_for("payment_success", order_id=order.id))

    if info["status"] in ("pending", "in_process"):
        flash("Tu pago quedó pendiente de acreditación.", "success")
    else:
        flash("El pago fue rechazado. Probá con otro medio de pago.", "error")
    return redirect(url_for("checkout", order_id=order.id))


@app.route("/pagos/<int:order_id>/exito")
@login_required
def payment_success(order_id):
    """Pantalla de pago aprobado (pago.html)."""
    order = own_order_or_403(order_id)
    if not order.payment:
        return redirect(url_for("checkout", order_id=order.id))
    return render_template("pago.html", order=order, payment=order.payment)


if __name__ == "__main__":
    app.run(debug=True)