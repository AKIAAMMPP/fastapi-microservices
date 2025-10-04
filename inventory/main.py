from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware
from redis_om import get_redis_connection, HashModel
from otel_instrumentation import  init_tracing_and_metrics


app = FastAPI()

init_tracing_and_metrics(app, service_name="inventory-service")

app.add_middleware(
    CORSMiddleware,
    allow_origins=['http://localhost:3005'],
    allow_methods=['*'],
    allow_headers=['*']
)


# Utilisation de Redis local
redis = get_redis_connection(
    host="redis",  # Nom du service dans docker-compose
    port="6379",
    password="",   # Pas de mot de passe pour Redis local
    decode_responses=True
)
class Product(HashModel):
    name: str
    price: float
    quantity: int

    class Meta:
        database = redis


@app.get('/products')
def all():
    return [format(pk) for pk in Product.all_pks()]


def format(pk: str):
    product = Product.get(pk)

    return {
        'id': product.pk,
        'name': product.name,
        'price': product.price,
        'quantity': product.quantity
    }


@app.post('/products')
def create(product: Product):
    return product.save()


@app.get('/products/{pk}')
def get(pk: str):
    return Product.get(pk)


@app.delete('/products/{pk}')
def delete(pk: str):
    return Product.delete(pk)


@app.put('/products/{pk}')
def update(pk: str, product: dict):
    existing = Product.get(pk)
    existing.name = product.get('name', existing.name)
    existing.price = product.get('price', existing.price)
    existing.quantity = product.get('quantity', existing.quantity)
    return existing.save()


@app.get("/metrics")
async def metrics_endpoint():
    from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
    from opentelemetry.exporter.prometheus import PrometheusMetricReader

    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)