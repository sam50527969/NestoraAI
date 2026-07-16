def analyze_opportunity(lead: dict):
    """
    Business Intelligence Engine

    Evaluates a lead and estimates:

    - Opportunity Score
    - Deal Value
    - Closing Probability
    - Business Potential
    - Recommended Service
    - Next Action
    """

    score = 0

    has_website = bool(lead.get("website"))
    has_phone = bool(lead.get("phone"))
    has_email = bool(lead.get("email"))

    ai_score = int(lead.get("ai_score") or 0)
    priority = (lead.get("priority") or "medium").lower()
    category = lead.get("category") or "Business"

    if not has_website:
        score += 25
    else:
        score += 10

    if has_phone:
        score += 15

    if has_email:
        score += 10

    score += int(ai_score * 0.30)

    if priority == "high":
        score += 20
    elif priority == "medium":
        score += 10

    score = max(0, min(score, 100))

    if score >= 90:
        estimated_value = 6000
        closing_probability = 85
        business_potential = "High"

    elif score >= 80:
        estimated_value = 4500
        closing_probability = 70
        business_potential = "High"

    elif score >= 70:
        estimated_value = 3000
        closing_probability = 55
        business_potential = "Medium"

    elif score >= 60:
        estimated_value = 2000
        closing_probability = 40
        business_potential = "Medium"

    else:
        estimated_value = 1000
        closing_probability = 20
        business_potential = "Low"

    recommended_service = "Business Consultation"

    if not has_website:
        recommended_service = "Professional Website"

    elif not has_email:
        recommended_service = "Business Email Setup"

    elif category in [
        "restaurant",
        "cafe",
        "fast_food",
    ]:
        recommended_service = "Online Ordering System"

    elif category in [
        "dentist",
        "clinic",
        "hospital",
    ]:
        recommended_service = "Appointment Booking System"

    elif category in [
        "hotel",
        "guest_house",
    ]:
        recommended_service = "Booking Website"

    elif category in [
        "car_repair",
        "garage",
    ]:
        recommended_service = "Workshop Management Website"

    elif category in [
        "travel_agency",
    ]:
        recommended_service = "Travel Booking Platform"

    if score >= 90:
        next_action = "Schedule Sales Call"

    elif score >= 70:
        next_action = "Send Proposal"

    elif score >= 50:
        next_action = "Send Outreach"

    else:
        next_action = "Keep in CRM"

    return {
        "opportunity_score": score,
        "estimated_value": estimated_value,
        "closing_probability": closing_probability,
        "business_potential": business_potential,
        "recommended_service": recommended_service,
        "next_action": next_action,
    }