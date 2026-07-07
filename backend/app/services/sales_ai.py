def analyze_lead(lead: dict):
    score = 50
    strengths = []
    weaknesses = []

    if lead.get("phone") and lead["phone"] != "Not found":
        score += 15
        strengths.append("Phone number available")
    else:
        weaknesses.append("No phone number")

    if lead.get("website") and lead["website"] != "Not found":
        score += 20
        strengths.append("Business website found")
    else:
        weaknesses.append("No website")

    category = (lead.get("category") or "").lower()

    if category in [
        "restaurant",
        "cafe",
        "coffee_shop",
        "salon",
        "gym",
        "clinic",
    ]:
        score += 10
        strengths.append("High-demand business category")

    recommendation = "Research before contacting."

    if score >= 80:
        recommendation = "Call immediately. High-value opportunity."

    elif score >= 65:
        recommendation = "Send WhatsApp first, then follow up."

    elif score >= 50:
        recommendation = "Email first before calling."

    return {
        "score": min(score, 100),
        "strengths": strengths,
        "weaknesses": weaknesses,
        "recommendation": recommendation,
    }