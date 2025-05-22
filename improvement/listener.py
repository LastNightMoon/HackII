import os
import logging
from kombu import Connection, Queue, Producer
from audio_pipeline import process_audio

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
rabbitmq_url = os.environ.get('RABBITMQ_URL')
INPUT_QUEUE = 'audio_input'
OUTPUT_QUEUE = 'audio_output1'
WORK_DIR = 'temp_output_i'

# Define durable queues
input_queue = Queue(INPUT_QUEUE, durable=True, queue_declare=True)
notification_queue = Queue(OUTPUT_QUEUE, durable=True, queue_declare=True)

try:
    with Connection(rabbitmq_url) as conn:
        with conn.SimpleQueue(input_queue) as simple_queue:
            logger.info(f" [*] Waiting for messages on queue '{INPUT_QUEUE}'. To exit press CTRL+C")
            while True:
                try:
                    message = simple_queue.get(timeout=1)
                    if message:
                        body = message.payload
                        logger.info(f" [x] Received: {body}")

                        try:
                            # Обработка аудио
                            process_audio(song_path=body, output_path="final_output.wav")
                            logger.info(f" [x] Processed audio file: {body}")

                            # Отправка нотификации
                            producer = Producer(conn)
                            producer.publish(
                                body=f"Processed: {body}",
                                routing_key=OUTPUT_QUEUE,
                                exchange='',
                                delivery_mode=2
                            )
                            logger.info(f" [x] Notification sent")

                        except Exception as process_err:
                            logger.error(f"Failed to process audio: {process_err}")

                        message.ack()

                except simple_queue.Empty:
                    continue
                except Exception as e:
                    logger.error(f"Error in message loop: {e}")

except KeyboardInterrupt:
    logger.info(' [*] Stopped consuming')
except Exception as conn_err:
    logger.error(f"Connection error: {conn_err}")
