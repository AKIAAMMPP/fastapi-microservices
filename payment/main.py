from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.background import BackgroundTasks
from redis_om import get_redis_connection, HashModel
from starlette.requests import Request
import requests, time
from otel_instrumentation import init_tracing_and_metrics



app = FastAPI()
init_tracing_and_metrics(app, service_name="payment-service")

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


class Order(HashModel):
    product_id: str
    price: float
    fee: float
    total: float
    quantity: int
    status: str  # pending, completed, refunded

    class Meta:
        database = redis


@app.get('/orders/{pk}')
def get(pk: str):
    return Order.get(pk)


@app.post('/orders')
async def create(request: Request, background_tasks: BackgroundTasks):
    body = await request.json()

    # Récupérer le produit depuis Inventory
    req = requests.get(f'http://inventory:8001/products/{body["id"]}')
    product = req.json()

    # Vérifier si la quantité demandée est disponible
    if int(body['quantity']) > int(product['quantity']):
        return {'error': 'Not enough stock available'}

    # Créer la commande
    order = Order(
        product_id=body['id'],
        price=product['price'],
        fee=0.2 * product['price'],
        total=1.2 * product['price'],
        quantity=body['quantity'],
        status='pending'
    )
    order.save()

    # Diminuer la quantité dans Inventory
    new_quantity = product['quantity'] - int(body['quantity'])
    requests.put(f'http://inventory:8001/products/{body["id"]}', json={'quantity': new_quantity})

    # Compléter la commande en arrière-plan
    background_tasks.add_task(order_completed, order)

    return order



def order_completed(order: Order):
    time.sleep(5)
    order.status = 'completed'
    order.save()
    redis.xadd('order_completed', order.dict(), '*')
    
    

@app.get("/metrics")
async def metrics_endpoint():
    from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
    from opentelemetry.exporter.prometheus import PrometheusMetricReader

    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)
