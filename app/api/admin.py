from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import select
from sqlalchemy import func
from app.auth.dependencies import get_current_admin
from app.db.session import get_session
from app.models.review import Review
from app.models.user import User
from app.models.resume import Resume

router = APIRouter()

@router.get("/stats")
def get_stats(session=Depends(get_session), admin=Depends(get_current_admin)):
    review_count = session.exec(select(func.count()).select_from(Review)).one()
    user_count = session.exec(select(func.count()).select_from(User)).one()
    resume_count = session.exec(select(func.count()).select_from(Resume)).one()
    return {
        "review_count": review_count,
        "user_count": user_count,
        "resume_count": resume_count
    }

@router.get("/reviews")
def get_all_reviews(session=Depends(get_session), admin=Depends(get_current_admin)):
    reviews = session.exec(select(Review)).all()
    if not reviews:
        raise HTTPException(status_code=404, detail="No reviews found")
    return [review.dict() for review in reviews]

@router.get("/users")
def get_all_users(session=Depends(get_session), admin=Depends(get_current_admin)):
    users = session.exec(select(User)).all()
    if not users:
        raise HTTPException(status_code=404, detail="No users found")
    # Exclude the current admin and the password field
    filtered_users = []
    for user in users:
        if user.id == admin.id:
            continue  # Skip the current admin
        user_dict = user.dict()
        user_dict.pop("hashed_password", None)  # Remove password field if present
        filtered_users.append(user_dict)
    return filtered_users

@router.get("/resumes")
def get_all_resumes(session=Depends(get_session), admin=Depends(get_current_admin)):
    resumes = session.exec(select(Resume)).all()
    if not resumes:
        raise HTTPException(status_code=404, detail="No resumes found")
    return [resume.dict() for resume in resumes]

@router.get("/user/{user_id}/resumes")
def get_user_resumes(user_id: int, session=Depends(get_session), admin=Depends(get_current_admin)):
    resumes = session.exec(select(Resume).where(Resume.user_id == user_id)).all()
    if not resumes:
        raise HTTPException(status_code=404, detail="No resumes found for this user")
    return [resume.dict() for resume in resumes]

@router.get("/user/{user_id}/reviews")
def get_user_reviews(user_id: int, session=Depends(get_session), admin=Depends(get_current_admin)):
    reviews = session.exec(select(Review).where(Review.user_id == user_id)).all()
    if not reviews:
        raise HTTPException(status_code=404, detail="No reviews found for this user")
    return [review.dict() for review in reviews]

@router.get("/resume/{resume_id}/reviews")
def get_resume_reviews(resume_id: int, session=Depends(get_session), admin=Depends(get_current_admin)):
    reviews = session.exec(select(Review).where(Review.resume_id == resume_id)).all()
    if not reviews:
        raise HTTPException(status_code=404, detail="No reviews found for this resume")
    return [review.dict() for review in reviews]