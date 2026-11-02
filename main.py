"""Runs the email assistant pipeline: understand -> plan -> draft -> review -> revise."""

from assistant import MODEL, email_agent

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

final_email = email_agent(email, user_context)

print("\nFinal email:")
print(final_email)
