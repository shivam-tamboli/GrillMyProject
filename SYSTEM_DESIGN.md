# GrillMyProject

## 1. Project Name and Problem Statement

**Project name:** GrillMyProject

**Problem:** Developers preparing for interviews have no platform to practice on their own personal projects. Every existing platform offers generic questions, peer interviews, or DSA practice. Nobody grills you on the project you actually built and will be asked about in a real interview.

---

## 2. Core Functional Requirements

1. **Project input.** User can add their project in three ways:
   - Upload a README
   - Connect a private GitHub repo using a personal token
   - Paste the codebase directly
2. **Resume scan.** System scans the resume and detects the experience level (Easy / Medium / Hard). User confirms it.
3. **Live interview.** AI runs a live session of 25 questions in 45 minutes, with dynamic questioning, follow-ups, and real-time scoring.
4. **Session report.** Generated at the end of the session:
   - Overall score
   - Score per question
   - Weak and strong areas
   - Feedback on answer structure

---

## 3. Additional Functional Requirements

Also part of Phase 1, kept separate so the core stays clear.

- **Three layer questioning**
  - Generic opening questions from a curated bank
  - Technology specific questions from a curated bank
  - LLM deep dive questions for the rest
- **Timer per question**
- **Three prompt personalities** based on level: Easy, Medium, Hard
- **Dynamic difficulty escalation.** If the user scores 7+/10 consistently, AI moves to the next difficulty level for the final questions.
- **Coaching when stuck.** AI motivates and guides the user, and never lets them feel defeated.
- **5 lens preparation guide.** Shown in the report only when AI detects unstructured or shallow answers.
- **Session history.** User can revisit all past interview sessions.

---

## 4. Core Non Functional Requirements

1. **Low latency.** LLM response must return fast enough to feel like a real conversation.
2. **Consistency over availability.** Every answer and score is saved to the database before the next question is served. No data loss during live sessions.
3. **Security.** GitHub personal tokens are encrypted before storing. User data is protected.
4. **Fault tolerance.** If the user drops off mid session, all progress is saved and the session can be recovered.

---

## 5. Additional Non Functional Requirements

Also handled in Phase 1.

- **Scalability.** System handles concurrent interview sessions without the database becoming a bottleneck. Active session data is cached in Redis, permanent data lives in PostgreSQL.
- **LLM rate limit handling.** A Redis queue absorbs excess LLM requests at scale. No request fails, they wait in the queue.
- **Rate limiting per user.** Maximum 10 LLM calls per minute per user, to prevent abuse and control API cost.

---

## 6. Core Entities

The main objects the system stores and works with.

**User**
- id, name, email, google_oauth_id, created_at

**Resume**
- id, user_id, raw_text, detected_level (easy/medium/hard), confirmed_level, created_at

**Project**
- id, user_id, input_type (readme/github/paste), raw_content, extracted_summary, github_token (encrypted), created_at

**Session**
- id, user_id, project_id, difficulty_level, status (ongoing/completed), started_at, ended_at

**Message**
- id, session_id, role (ai/user), content, question_number, score (out of 10), feedback, created_at

**Report**
- id, session_id, overall_score, strong_areas, weak_areas, answer_structure_feedback, show_preparation_guide (boolean), created_at

---

## 7. API Design

### POST /api/resume/upload
Upload resume, scan it, return detected level.

Request:
```json
{ "file": "pdf" }
```
Response:
```json
{ "detected_level": "easy/medium/hard", "resume_id": "string" }
```

### POST /api/project
Submit project input.

Request:
```json
{
  "input_type": "readme/github/paste",
  "content": "string",
  "github_token": "string (optional)"
}
```
Response:
```json
{ "project_id": "string", "extracted_summary": "string" }
```

### POST /api/session/confirm-level
User confirms or changes the detected level.

Request:
```json
{ "resume_id": "string", "confirmed_level": "easy/medium/hard" }
```
Response:
```json
{ "confirmed": true, "level": "string" }
```

### POST /api/session/start
Start the interview session and get the first question.

Request:
```json
{ "project_id": "string", "level": "easy/medium/hard" }
```
Response:
```json
{
  "session_id": "string",
  "question": "string",
  "question_number": 1,
  "timer_seconds": 108
}
```

### POST /api/session/answer
Submit an answer, get score, feedback and the next question.

Request:
```json
{ "session_id": "string", "question_number": 1, "answer": "string" }
```
Response:
```json
{
  "score": 7,
  "feedback": "string",
  "next_question": "string",
  "question_number": 2,
  "session_complete": false
}
```

### POST /api/session/{session_id}/end
Mark the session complete and trigger report generation.

Request:
```json
{ "session_id": "string" }
```
Response:
```json
{ "session_id": "string", "report_id": "string" }
```

### GET /api/session/{session_id}/report
Get the final session report.

Response:
```json
{
  "overall_score": 7,
  "per_question_scores": [],
  "strong_areas": "string",
  "weak_areas": "string",
  "answer_structure_feedback": "string",
  "show_preparation_guide": false
}
```

### GET /api/sessions
Get all past sessions for the logged in user.

Response:
```json
{
  "sessions": [
    {
      "session_id": "string",
      "date": "string",
      "overall_score": 7,
      "level": "string",
      "status": "string"
    }
  ]
}
```
