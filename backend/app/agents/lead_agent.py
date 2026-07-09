from app.services.business_search import search_businesses


class LeadAgent:
    async def search(self, business_type, location, quantity):
        try:
            return await search_businesses(
                business_type=business_type,
                location=location,
                limit=quantity,
            )
        except Exception as error:
            print(f"LeadAgent search failed: {error}")
            return []