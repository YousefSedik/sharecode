from sqlalchemy import event
from sqlalchemy.orm import Session
from models import Project
from datetime import datetime


# Define the listener for the after_update event
@event.listens_for(Session, "after_flush")
def update_updated_at(session, flush_context, instances):
    for instance in session.dirty:
        if isinstance(instance, Project):  # Check if the instance is a Project
            instance.updated_at = datetime.now(datetime.timezone.utc)
