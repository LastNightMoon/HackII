# http://45.144.64.108:9002/browser - WEB UI
import io
import boto3
import os


class ManagerMinio:
    def __init__(self):
        self.client = boto3.client("s3", endpoint_url=f"http://{os.environ.get('MINIO_URL')}",
                                   aws_access_key_id=str(os.environ.get("MINIO_PUB")),
                                   aws_secret_access_key=str(os.environ.get("MINIO_PRI")))

    def upload_file(self, bucket: str, data: bytes, path_from: str):
        self.client.upload_fileobj(io.BytesIO(data), bucket, path_from)

    def download_file(self, bucket: str, path_to: str):
        obj = self.client.get_object(Bucket=bucket, Key=path_to)
        return obj["Body"].read()


minio_manager = ManagerMinio()

# @staticmethod
# def upload_image(image, name):
#   image.seek(0)
#   minio_manager.upload_file("task", image, name + ".png")
