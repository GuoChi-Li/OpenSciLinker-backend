from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database.dataSchema import get_db, Post,User
from pydantic import BaseModel
from datetime import datetime
from typing import List

router = APIRouter()



########## Pydantic Models ##########
class StatisticsOut(BaseModel):
    total_projects: int
    new_projects: int
    total_users: int



########## Utility Functions ##########

########## API Endpoints ##########
from datetime import timedelta

@router.get("/statistics/", response_model=StatisticsOut)
def get_statistics(db: Session = Depends(get_db)):
    """Retrieve statistics about projects and users"""
    # Total number of projects
    total_projects = db.query(Post).count()
    
    # Projects created in the last week
    one_week_ago = datetime.now() - timedelta(weeks=1)
    new_projects = db.query(Post).filter(Post.timestamp >= one_week_ago).count()
    
    # Total number of users
    total_users = db.query(User).count()  # 注意，你需要從dataSchema中導入User。

    return {
        "total_projects": total_projects,
        "new_projects": new_projects,
        "total_users": total_users
    }
