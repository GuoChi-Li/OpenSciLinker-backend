
    
from fastapi import FastAPI
from api.login import router as api_login_router
from api.post import router as api_post_router
from api.search import router as api_search_router
from api.statistics import router as api_statistics_router
from api.search import populate_tags_dict
from database.dataSchema import engine, Base, SessionLocal
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

app = FastAPI()
app.include_router(api_login_router, prefix="/api")
app.include_router(api_post_router, prefix="/api")
app.include_router(api_search_router, prefix="/api")
app.include_router(api_statistics_router, prefix="/api")


# Configure CORS settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace with the origin of your frontend app
    allow_credentials=True,
    allow_methods=["GET", "POST"],  # Add other HTTP methods you need
    allow_headers=["*"],  # You can restrict this to specific headers if needed
)

@app.on_event("startup")
async def startup_event():
    populate_tags_dict(session_maker=SessionLocal)

if __name__ == "__main__":
    Base.metadata.create_all(bind=engine)
    uvicorn.run(app, host="0.0.0.0", port=8080)


