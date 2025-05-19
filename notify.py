import os

from kombu import Connection, Queue
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
rabbitmq_url = os.environ.get('RABBITMQ_URL')
queue_name = 'notifications'

# Define a durable queue
queue = Queue(queue_name, durable=True)

try:
    # Connect to RabbitMQ
    with Connection(rabbitmq_url) as conn:
        # Create a SimpleQueue for consuming notifications
        with conn.SimpleQueue(queue) as simple_queue:
            logger.info(f" [*] Waiting for notifications on queue '{queue_name}'. To exit press CTRL+C")
            while True:
                try:
                    # Get message with a timeout to allow KeyboardInterrupt
                    message = simple_queue.get(block=True, timeout=1)
                    if message:
                        body = message.payload
                        logger.info(f" [x] Notification received: {body}")
                        message.ack()  # Acknowledge the notification
                except simple_queue.Empty:
                    continue  # No message, keep looping
                except Exception as e:
                    logger.error(f"Error processing notification: {e}")
except KeyboardInterrupt:
    logger.info(' [*] Stopped consuming')
except Exception as e:
    logger.error(f"Connection error: {e}")