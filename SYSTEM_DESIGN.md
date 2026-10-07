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
