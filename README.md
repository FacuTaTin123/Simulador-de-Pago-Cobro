# Facundo Balancini — Simulador de pago/cobro

Aplicación educativa construida con Python y Flask. Implementa catálogo de videojuegos, autenticación, gestión de productos, carrito y creación de pedidos. El módulo de pago queda preparado para que lo desarrolles.

## Requisitos e instalación

```powershell
cd SimulacionPago-Cobro
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
python app.py
```

Abrí `http://127.0.0.1:5000/`. La base SQLite se crea automáticamente en `instance/pixel_store.db` y carga cuatro productos de ejemplo.

## Funcionalidades implementadas

- Registro, inicio y cierre de sesión con Flask-Login.
- Formularios protegidos con CSRF mediante Flask-WTF.
- Modelos SQLAlchemy: `User`, `Product`, `Order`, `OrderItem` y `Payment`.
- Gestión de productos: agregar, editar y eliminar (requiere iniciar sesión).
- Carrito guardado en sesión y creación de pedidos asociados al usuario.
- Vista `/pagos/<id>` que recibe el pedido creado y es el lugar para desarrollar el simulador.

## Cómo completar el simulador de pago

En la ruta `payment_placeholder` de `app.py`, recibís el objeto `order`. Creá un formulario para método e importe, guardá un objeto `Payment` y actualizá `order.status` (por ejemplo, a `pagado` o `rechazado`). Luego ejecutá `db.session.commit()`.

Antes de publicar el proyecto, reemplazá `SECRET_KEY` por una variable de entorno segura y desactivá `debug=True`.
