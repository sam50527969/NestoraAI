from sqlalchemy.orm import Session

from app.database.models import Lead


class CEOBrain:

    def __init__(self, db: Session):
        self.db = db

    def think(self, question: str):

        question = question.lower()

        if "highest" in question and "score" in question:
            return self.best_lead()

        if "restaurant" in question:
            return self.restaurants()

        if "website" in question:
            return self.no_website()

        if "priority" in question:
            return self.high_priority()

        return (
            "I understand your request, "
            "but I don't know how to answer it yet."
        )

    def best_lead(self):

        lead = (
            self.db.query(Lead)
            .order_by(Lead.ai_score.desc())
            .first()
        )

        if not lead:
            return "No leads available."

        return (
            f"Your best lead is {lead.name} "
            f"with AI Score {lead.ai_score}."
        )

    def restaurants(self):

        leads = (
            self.db.query(Lead)
            .filter(Lead.category.ilike("%restaurant%"))
            .all()
        )

        if not leads:
            return "No restaurants found."

        names = ", ".join(x.name for x in leads[:10])

        return f"Restaurants:\n\n{names}"

    def no_website(self):

        leads = (
            self.db.query(Lead)
            .filter(
                (Lead.website == None)
                | (Lead.website == "")
            )
            .all()
        )

        if not leads:
            return "Every lead has a website."

        return (
            f"{len(leads)} businesses "
            "do not have a website."
        )

    def high_priority(self):

        leads = (
            self.db.query(Lead)
            .filter(Lead.priority == "High")
            .all()
        )

        if not leads:
            return "No high priority leads."

        names = ", ".join(x.name for x in leads)

        return f"High priority:\n\n{names}"