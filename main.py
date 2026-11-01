"""Runs the email assistant pipeline: understand -> plan -> draft -> review -> revise."""

from assistant import (
    MODEL,
    understand_email,
    plan_response,
    draft_reply,
    review_reply,
    revise_reply,
    email_agent,
)

print("Using model:", MODEL)

email = """
Hi,

I wanted to check whether you've completed
the project report. We need it before Friday's meeting.

Thanks!
"""

user_context = """
The project report is not complete yet.
I expect to finish it by Thursday afternoon.
"""

understanding = understand_email(email)

print(understanding)

plan = plan_response(
    email,
    understanding,
    user_context
)

print(plan)

draft = draft_reply(
    email,
    plan,
    user_context
)

print(draft)

review = review_reply(
    email,
    draft,
    user_context
)

print(review)

if review.startswith("NEEDS_REVISION"):

    draft = revise_reply(
        email,
        draft,
        review,
        user_context
    )

print(draft)

final_email = email_agent(email, user_context)

print("\nFinal email:")
print(final_email)
