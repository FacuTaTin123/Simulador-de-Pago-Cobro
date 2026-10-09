"""Integración con Mercado Pago (Checkout Pro)."""
import os
import mercadopago


def _sdk():
    token = os.environ.get("MP_ACCESS_TOKEN")
    if not token:
        raise RuntimeError("Falta MP_ACCESS_TOKEN en el archivo .env")
    return mercadopago.SDK(token)


def crear_preferencia(order, base_url):
    """Crea la preferencia de pago de un pedido y devuelve la respuesta de Mercado Pago."""
    data = {
        "items": [
            {
                "title": item.product.name,
                "quantity": item.quantity,
                "unit_price": float(item.unit_price),
                "currency_id": "ARS",
            }
            for item in order.items
        ],
        "external_reference": str(order.id),
        "back_urls": {
            "success": f"{base_url}/pagos/retorno",
            "failure": f"{base_url}/pagos/retorno",
            "pending": f"{base_url}/pagos/retorno",
        },
    }
    resp = _sdk().preference().create(data)
    if resp["status"] not in (200, 201):
        raise RuntimeError(f"Mercado Pago rechazó la preferencia: {resp['response']}")
    return resp["response"]


def obtener_pago(payment_id):
    """Consulta un pago directamente a Mercado Pago (no confiamos en lo que llega por la URL)."""
    resp = _sdk().payment().get(payment_id)
    return resp["response"] if resp["status"] == 200 else None