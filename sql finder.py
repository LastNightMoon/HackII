import requests
import sqlalchemy
from sqlalchemy import update
from DataBaseManager import MusicMeta
from utils.generate_sql_stmz import get_text_sql

# query = sqlalchemy.select(MusicMeta)
#
# response = requests.post("http://0.0.0.0:6543", json={"text": get_text_sql(query, "MusicMeta")})
# print(response.json())
