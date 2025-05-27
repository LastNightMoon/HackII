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
        return self.stream_file(bucket, path_to).read()

    def stream_file(self, bucket: str, path_to: str):
        obj = self.client.get_object(Bucket=bucket, Key=path_to)
        return obj["Body"]

    def delete_file(self, bucket: str, path: str):
        self.client.delete_object(Bucket=bucket, Key=path)

minio_manager = ManagerMinio()

if __name__ == "__main__":
    minio_manager.delete_file("music", "impБаксанская.wav")

# @staticmethod
# def upload_image(image, name):
#   image.seek(0)
#   minio_manager.upload_file("task", image, name + ".png")
