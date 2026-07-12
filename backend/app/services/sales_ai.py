def has_real_value(value):
    return bool(value and str(value).strip() and value != "Not found")


def analyze_lead(lead: dict):
    score = 35
    strengths = []
    weaknesses = []

    phone = lead.get("phone")
    website = lead.get("website")
    category = (lead.get("category") or "").lower()
    priority = (lead.get("priority") or "").lower()
    notes = lead.get("notes") or ""

    if has_real_value(phone):
        score += 20
        strengths.append("Phone number available for direct outreach")
    else:
        weaknesses.append("No usable phone number found")

    if has_real_value(website):
        score += 15
        strengths.append("Business website is available")
    else:
        score += 10
        weaknesses.append("No website found, which may indicate a website sales opportunity")

    high_demand_categories = {
        "restaurant",
        "cafe",
        "coffee_shop",
        "salon",
        "gym",
        "clinic",
        "dentist",
        "real_estate",
        "automotive",
    }

    if category in high_demand_categories:
        score += 15
        strengths.append("Business category has strong demand for digital services")

    if priority == "high":
        score += 10
        strengths.append("Lead is already marked as high priority")
    elif priority == "low":
        score -= 5
        weaknesses.append("Lead is currently marked as low priority")

    if notes:
        score += 5
        strengths.append("Lead includes useful sales context or recommendations")

    score = max(0, min(score, 100))

    if score >= 85:
        recommendation = (
            "Contact immediately. This is a high-value opportunity and should be "
            "prioritized for a direct call or personalized WhatsApp message."
        )
    elif score >= 70:
        recommendation = (
            "Send a personalized WhatsApp message or email, then schedule a follow-up."
        )
    elif score >= 55:
        recommendation = (
            "Research the business further and prepare a targeted outreach message."
        )
    else:
        recommendation = (
            "Enrich the lead with better contact details before spending time on outreach."
        )

    if not has_real_value(website):
        opportunity = (
            "Strong website or digital presence opportunity. Consider offering a "
            "starter website, Google Business optimization, or online ordering solution."
        )
    elif not has_real_value(phone):
        opportunity = (
            "The business has a website but limited contact information. Research social "
            "profiles or email before outreach."
        )
    else:
        opportunity = (
            "The business has enough contact information for direct sales outreach."
        )

    return {
        "score": score,
        "strengths": strengths,
        "weaknesses": weaknesses,
        "recommendation": recommendation,
        "opportunity": opportunity,
    }