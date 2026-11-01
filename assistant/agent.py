"""Email assistant agent: understand -> plan -> draft -> review -> revise."""

from . import prompts
from .config import MODEL
from .llm_client import client


def understand_email(email):

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {
                "role": "system",
                "content": prompts.UNDERSTAND_SYSTEM
            },
            {
                "role": "user",
                "content": email
            }
        ]
    )

    return response.choices[0].message.content


def plan_response(email, understanding, context):

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {
                "role": "system",
                "content": prompts.PLAN_SYSTEM
            },
            {
                "role": "user",
                "content": prompts.PLAN_USER.format(
                    email=email,
                    understanding=understanding,
                    context=context
                )
            }
        ]
    )

    return response.choices[0].message.content


def draft_reply(email, plan, context):

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {
                "role": "system",
                "content": prompts.DRAFT_SYSTEM
            },
            {
                "role": "user",
                "content": prompts.DRAFT_USER.format(
                    email=email,
                    plan=plan,
                    context=context
                )
            }
        ]
    )

    return response.choices[0].message.content


def review_reply(email, draft, context):

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {
                "role": "system",
                "content": prompts.REVIEW_SYSTEM
            },
            {
                "role": "user",
                "content": prompts.REVIEW_USER.format(
                    email=email,
                    context=context,
                    draft=draft
                )
            }
        ]
    )

    return response.choices[0].message.content


def revise_reply(email, draft, review, context):

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {
                "role": "system",
                "content": prompts.REVISE_SYSTEM
            },
            {
                "role": "user",
                "content": prompts.REVISE_USER.format(
                    email=email,
                    context=context,
                    draft=draft,
                    review=review
                )
            }
        ]
    )

    return response.choices[0].message.content


def email_agent(email, user_context):

    print("Step 1: Understanding email...")
    understanding = understand_email(email)

    print("Step 2: Planning response...")
    plan = plan_response(
        email, understanding, user_context
    )

    print("Step 3: Drafting reply...")
    draft = draft_reply(
        email, plan, user_context
    )

    print("Step 4: Reviewing reply...")
    review = review_reply(
        email, draft, user_context
    )

    if review.startswith("NEEDS_REVISION"):
        print("Improving the draft...")
        draft = revise_reply(
            email, draft, review, user_context
        )

    return draft
