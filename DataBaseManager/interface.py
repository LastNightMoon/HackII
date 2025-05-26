import uvicorn
from fastapi import FastAPI

from fastapi.responses import JSONResponse
from sqlalchemy import text

from DataBaseManager import db
from DataBaseManager.schems import SQLBase
from DataBaseManager.models import model_map

app = FastAPI()


@app.post("/")
async def execute_query(query: SQLBase):
    try:
        model = model_map.get(query.model_name)
        print(query)
        if model is None:
            return JSONResponse(status_code=400, content={"ok": False, "error": "Unknown model"})

        result = db.get_session().execute(text(query.text))
        print(result)
        rows = result.fetchall()
        print(rows)
        # Преобразуем SQLAlchemy Row в dict через маппинг
        return {
            "ok": True,
            "response": [dict(row._mapping) for row in rows]
        }
        return None

    except Exception as e:
        print(e)
        return JSONResponse(status_code=500, content={"ok": False, "error": str(e)})


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=6543)
