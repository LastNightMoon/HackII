import os

from kombu import Connection, Queue, Producer
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
rabbitmq_url = os.environ.get('RABBITMQ_URL')
queue_name = 'hi'
notification_queue_name = 'notifications'

# Define durable queues
input_queue = Queue(queue_name, durable=True, queue_declare=True)
notification_queue = Queue(notification_queue_name, durable=True, queue_declare=True)

try:
    # Connect to RabbitMQ
    with Connection(rabbitmq_url) as conn:
        # Create a SimpleQueue for consuming messages
        with conn.SimpleQueue(input_queue) as simple_queue:
            logger.info(f" [*] Waiting for messages on queue '{queue_name}'. To exit press CTRL+C")
            while True:
                try:
                    # Get message with a timeout to allow KeyboardInterrupt
                    message = simple_queue.get(timeout=1)
                    if message:
                        body = message.payload
                        logger.info(f" [x] Received: {body}")
                        # Send notification to the notifications queue
                        producer = Producer(conn)
                        producer.publish(
                            body=f"Processed message: {body}",
                            routing_key=notification_queue_name,
                            exchange='',  # Default exchange
                            delivery_mode=2  # Persistent
                        )
                        logger.info(f" [x] Sent notification to queue '{notification_queue_name}'")
                        message.ack()  # Acknowledge the original message
                except simple_queue.Empty:
                    continue  # No message, keep looping
                except Exception as e:
                    logger.error(f"Error processing message: {e}")
except KeyboardInterrupt:
    logger.info(' [*] Stopped consuming')
except Exception as e:
    logger.error(f"Connection error: {e}")