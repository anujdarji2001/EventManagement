from fastapi import FastAPI
from app.routes import events, attendees

app = FastAPI(title="Mini Event Management System")

app.include_router(events.router)
app.include_router(attendees.router)

# Routers will be included here 