from fastapi import APIRouter, Depends, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.db.database import get_db
from app.models import Resume, User
from app.services.level import detect_level
from app.services.llm import LLMError
from app.services.resume import ResumeError, extract_text, is_pdf

router = APIRouter(prefix="/api/resume", tags=["resume"])

MAX_BYTES = 5 * 1024 * 1024


@router.post("/upload")
def upload_resume(
    file: UploadFile,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # read one byte past the limit so we can tell "exactly 5 MB" from "too big"
    data = file.file.read(MAX_BYTES + 1)
    if len(data) > MAX_BYTES:
        raise HTTPException(status_code=413, detail="file is larger than 5 MB")
    if not is_pdf(data):
        raise HTTPException(status_code=400, detail="only PDF files are accepted")

    try:
        text = extract_text(data)
    except ResumeError as e:
        raise HTTPException(status_code=422, detail=str(e))

    try:
        level = detect_level(text)
    except LLMError:
        raise HTTPException(status_code=502, detail="level detection failed, try again")

    resume = Resume(user_id=user.id, raw_text=text, detected_level=level)
    db.add(resume)
    db.commit()
    db.refresh(resume)
    return {"resume_id": str(resume.id), "detected_level": resume.detected_level}
