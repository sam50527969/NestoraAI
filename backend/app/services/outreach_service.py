from app.schemas.outreach import OutreachRequest, OutreachResponse


def generate_outreach(request: OutreachRequest) -> OutreachResponse:
    lead = request.lead
    offer = request.offer or "starter business package"

    business_name = lead.name
    category = lead.category or "business"
    priority = lead.priority or "Medium"

    email_subject = f"Helping {business_name} attract more customers"

    email_body = f"""Hi {business_name} Team,

I came across {business_name} and noticed that you are operating in the {category} space.

We help local businesses improve their online presence, attract more customers, and turn more visitors into paying clients through affordable digital solutions.

Based on your profile, you may be a {priority.lower()} priority opportunity for improving visibility and customer engagement.

I would like to briefly introduce our {offer} and see if it could be useful for your business.

Best regards,
Nestora AI"""

    whatsapp_message = f"""Hi, I found {business_name} and wanted to quickly introduce a simple {offer} that helps local businesses attract more customers online. Would you be open to a quick chat?"""

    cold_call_script = f"""Hi, am I speaking with someone from {business_name}?

My name is Sam. I help local {category} businesses improve their online presence and attract more customers.

I only wanted to ask one quick question: are you currently doing anything actively to bring in more customers online?"""

    proposal_summary = f"""{business_name} may benefit from a {offer} focused on improving online visibility, customer trust, and lead generation.

Suggested first step:
Offer a simple audit of their online presence and recommend quick improvements."""

    return OutreachResponse(
        email_subject=email_subject,
        email_body=email_body,
        whatsapp_message=whatsapp_message,
        cold_call_script=cold_call_script,
        proposal_summary=proposal_summary,
    )