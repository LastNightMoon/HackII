import os
import logging
from kombu import Connection, Queue, Producer
from dotenv import load_dotenv

from improvement.audio_pipeline import process_audio
from improvement.schems import Song
from utils.generate_sql_stmz import select_music_by_id
from DataBaseManager.minio_manager import minio_manager


def audio_download(body: dict):
    logger = logging.getLogger(__name__)
    logger.info("Parsing input metadata...")
    meta_data = Song.model_validate_json(body)

    logger.info(f"Fetching audio metadata for ID: {meta_data.id}")
    audio_meta = select_music_by_id(meta_data.id)
    if not audio_meta:
        logger.info(f'No audio found for ID: {meta_data.id}')
        return
    logger.info(f"Downloading audio from Minio: {audio_meta.url}")
    data = minio_manager.download_file("music", audio_meta.url)

    logger.info("Starting audio processing pipeline...")
    audio = process_audio(data)

    new_filename = f"imp_{audio_meta.url}"
    logger.info(f"Uploading processed audio to Minio as: {new_filename}")
    minio_manager.upload_file("music", audio, new_filename)

    logger.info("Audio processing and upload completed successfully.")


def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )


def main():
    setup_logging()
    logger = logging.getLogger(__name__)
    load_dotenv()

    rabbitmq_url = os.getenv('RABBITMQ_URL')
    if not rabbitmq_url:
        logger.error("RABBITMQ_URL is not set in the environment.")
        return

    INPUT_QUEUE = 'audio_input'
    OUTPUT_QUEUE = 'audio_output1'

    input_queue = Queue(INPUT_QUEUE, durable=True)
    notification_queue = Queue(OUTPUT_QUEUE, durable=True)

    try:
        with Connection(rabbitmq_url) as conn:
            with conn.SimpleQueue(input_queue) as simple_queue:
                logger.info(f" [*] Waiting for messages on queue '{INPUT_QUEUE}'. To exit press CTRL+C")

                while True:
                    try:
                        message = simple_queue.get(timeout=1)
                        if message:
                            body = message.payload
                            logger.info(f" [x] Received message: {body}")

                            try:
                                audio_download(body)

                                logger.info(f" [✓] Processed audio file: {body}")

                                # Send notification
                                producer = Producer(conn)
                                response_payload = body
                                producer.publish(
                                    body=response_payload,
                                    routing_key=OUTPUT_QUEUE,
                                    exchange='',
                                    delivery_mode=2
                                )
                                logger.info(" [→] Notification sent")

                            except Exception as process_err:
                                logger.exception(f" [!] Failed to process audio: {process_err}")

                            message.ack()

                    except simple_queue.Empty:
                        continue
                    except Exception as e:
                        logger.exception(f" [!] Error in message loop: {e}")

    except KeyboardInterrupt:
        logger.info(' [*] Stopped consuming (KeyboardInterrupt)')
    except Exception as conn_err:
        logger.exception(f" [!] Connection error: {conn_err}")


if __name__ == "__main__":
    main()
