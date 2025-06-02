from fastapi import APIRouter, Depends, HTTPException, Body
from app.services.jd_match import match_resume_with_job_desc
from app.db.session import get_session
from app.models.resume import Resume
from app.models.job_desc import JobMatch
from app.auth.dependencies import get_current_user
import json
from datetime import datetime

router = APIRouter()

@router.post("/{resume_id}/match")
def match_resume(
    resume_id: int,
    job_description: str = Body(..., embed=True),
    session=Depends(get_session),
    user=Depends(get_current_user)
):
    resume = session.get(Resume, resume_id)
    if not resume or resume.user_id != user.id:
        raise HTTPException(status_code=404, detail="Resume not found")
    ai_response = match_resume_with_job_desc(resume.content, job_description)
    try:
        result = json.loads(ai_response)
        ai_response_to_store = json.dumps(result, ensure_ascii=False)
    except Exception:
        ai_response_to_store = ai_response
        result = {"raw_feedback": ai_response}
    job_match = JobMatch(
        resume_id=resume.id,
        user_id=user.id,
        job_description=job_description,
        ai_response=ai_response_to_store,
        created_at=datetime.utcnow()
    )
    session.add(job_match)
    session.commit()
    session.refresh(job_match)
    result["job_match_id"] = job_match.id
    return result

@router.get("/{resume_id}/matches")
def list_job_matches(
    resume_id: int,
    session=Depends(get_session),
    user=Depends(get_current_user)
):
    matches = session.query(JobMatch).filter(
        JobMatch.resume_id == resume_id,
        JobMatch.user_id == user.id
    ).all()
    return [
        {
            "id": m.id,
            "job_description": m.job_description,
            "ai_response": json.loads(m.ai_response) if m.ai_response else {},
            "created_at": m.created_at
        }
        for m in matches
    ]