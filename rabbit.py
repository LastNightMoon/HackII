import os

from kombu import Connection, Queue, Producer
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
rabbitmq_url = os.environ.get('RABBITMQ_URL')
queue_name = 'audio_input'

# Define a durable queue
queue = Queue(queue_name, durable=True)

try:
    # Connect to RabbitMQ
    with Connection(rabbitmq_url) as conn:
        # Ensure the connection is established
        conn.connect()
        producer = Producer(conn)
        # Publish a persistent message
        producer.publish(
            body='{"id": 1}',
            routing_key=queue_name,
            exchange='',  # Default exchange
        )
        logger.info(f" [x] Sent 'Hello, RabbitMQ from kombu!' to queue '{queue_name}'")
except Exception as e:
    logger.error(f"Error sending message: {e}")