import os
import json
from fastapi import APIRouter, BackgroundTasks, UploadFile, File, Depends, HTTPException, status
from fastapi.responses import FileResponse
from app.db.session import get_session
from app.models.resume import Resume
from app.auth.dependencies import get_current_user
from app.models.review import Review
from app.services.ai_review import review_resume_ai
from app.services.parser import parse_resume_file
from datetime import datetime, timezone
from app.schemas.resume import ResumeRead
from datetime import datetime
from app.db.session import engine
from sqlmodel import Session
from app.services.review_download import generate_review_pdf, ensure_list
from app.models.resume import Resume
from app.models.review import Review
from app.db.session import engine
from sqlmodel import Session
import re, os


REVIEW_LIMIT_PER_DAY = 5

def get_today():
    return datetime.now(timezone.utc).date()

def get_review_count_today(session, user):
    today = get_today()
    return session.query(Review).filter(
        Review.user_id == user.id,
        Review.created_at >= today
    ).count()

router = APIRouter()

@router.post("/upload", status_code=status.HTTP_201_CREATED)
async def upload_resume(
    file: UploadFile = File(...),
    session=Depends(get_session),
    user=Depends(get_current_user)
):
    allowed_types = [
        "application/pdf",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    ]
    if file.content_type not in allowed_types:
        raise HTTPException(status_code=400, detail="Invalid file type")

    content = await file.read()
    if not content:
        raise HTTPException(status_code=400, detail="File is empty")
    
    parsed_text = parse_resume_file(file.filename, content)
    if not parsed_text.strip():
        raise HTTPException(status_code=400, detail="Could not extract text from resume")

    resume = Resume(
        user_id=user.id,
        filename=file.filename,
        content=parsed_text,
        uploaded_at=datetime.now(timezone.utc).isoformat()
    )
    session.add(resume)
    session.commit()
    session.refresh(resume)

    return {"resume_id": resume.id}


@router.get("/resumes")
async def list_resumes(
    session=Depends(get_session),
    user=Depends(get_current_user)
):
    resumes = session.query(Resume).filter(Resume.user_id == user.id).all()
    if not resumes:
        raise HTTPException(status_code=404, detail="No resumes found")
    return [
        {
            "id": r.id,
            "filename": r.filename,
            "uploaded_at": r.uploaded_at
        }
        for r in resumes
    ]

@router.get("/{resume_id}", response_model=ResumeRead)
async def get_resume(
    resume_id: int,
    session=Depends(get_session),
    user=Depends(get_current_user)
):
    resume = session.query(Resume).filter(Resume.id == resume_id, Resume.user_id == user.id).first()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")

    return {"id": resume.id, "filename": resume.filename, "content": resume.content, "uploaded_at": resume.uploaded_at}


@router.get("/{resume_id}/review")
async def review_resume(
    resume_id: int,
    background_tasks: BackgroundTasks,
    session=Depends(get_session),
    user=Depends(get_current_user)
):
    today = get_today()
    start = datetime.combine(today, datetime.min.time())
    end = datetime.combine(today, datetime.max.time())
    review_count = session.query(Review).filter(
        Review.user_id == user.id,
        Review.created_at >= start,
        Review.created_at <= end
    ).count()
    if review_count >= REVIEW_LIMIT_PER_DAY:
        raise HTTPException(status_code=429, detail="Daily review limit reached")

    resume = session.query(Resume).filter(Resume.id == resume_id, Resume.user_id == user.id).first()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
    
    def clean_ai_json_response(ai_response: str):
        # Remove code block markers if present
        if ai_response.strip().startswith("```"):
            ai_response = ai_response.strip().split('\n', 1)[1]
            if ai_response.startswith("json"):
                ai_response = ai_response[4:]
            ai_response = ai_response.rsplit("```", 1)[0]
        return ai_response.strip()

    def save_and_format_review(resume_id: int, user_id: int):
        

        with Session(engine) as bg_session:
            resume = bg_session.query(Resume).filter(Resume.id == resume_id, Resume.user_id == user_id).first()
            if not resume:
                return
            ai_response = review_resume_ai(resume.content)
            cleaned = clean_ai_json_response(ai_response)
            try:
                parsed = json.loads(cleaned)
                
                suggestions = parsed.get("suggestions", [])
                suggestions = ensure_list(suggestions)
                summary = parsed.get("summary", "")
                if isinstance(summary, list):
                    summary = " ".join(str(s) for s in summary)
                score = parsed.get("score")
                # Save normalized JSON
                feedback_to_store = json.dumps({
                    "score": score,
                    "suggestions": suggestions,
                    "summary": summary
                }, ensure_ascii=False)
            except Exception:
                # fallback: store raw
                score = None
                suggestions = []
                summary = ""
                feedback_to_store = ai_response

            review = Review(
                resume_id=resume.id,
                user_id=user_id,
                feedback=feedback_to_store,
                score=score
            )
            bg_session.add(review)
            bg_session.commit()
            bg_session.refresh(review)
            # Generate PDF
            pdf_dir = "generated_reviews"
            os.makedirs(pdf_dir, exist_ok=True)
            pdf_path = os.path.join(pdf_dir, f"{review.id}.pdf")
            generate_review_pdf(resume, score, suggestions, summary, pdf_path)

    background_tasks.add_task(save_and_format_review, resume.id, user.id)
    return {"message": "Review is being processed in the background. Check /resume/{resume_id}/reviews for results."}

@router.get("/{resume_id}/reviews")
async def list_reviews(
    resume_id: int,
    session=Depends(get_session),
    user=Depends(get_current_user)
):
    reviews = session.query(Review).filter(
        Review.resume_id == resume_id,
        Review.user_id == user.id
    ).all()
    if not reviews:
        raise HTTPException(status_code=404, detail="No reviews found for this resume")
    result = []
    for r in reviews:
        try:
            parsed = json.loads(r.feedback)
            score = parsed.get("score")
            suggestions = parsed.get("suggestions", [])
            summary = parsed.get("summary", "")
        except Exception:
            score = r.score
            suggestions = []
            summary = ""
        result.append({
            "id": r.id,
            "score": score,
            "created_at": r.created_at,
            "suggestions": suggestions,
            "summary": summary
        })
    return result

@router.get("/{resume_id}/review/{review_id}/download")
async def download_review_pdf(
    resume_id: int,
    review_id: int,
    session=Depends(get_session),
    user=Depends(get_current_user)
):
    review = session.query(Review).filter(
        Review.id == review_id,
        Review.resume_id == resume_id,
        Review.user_id == user.id
    ).first()
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    pdf_path = os.path.join("generated_reviews", f"{review_id}.pdf")
    if not os.path.exists(pdf_path):
        raise HTTPException(status_code=404, detail="PDF not generated yet")
    return FileResponse(pdf_path, filename=f"resume_review_{review_id}.pdf", media_type="application/pdf")