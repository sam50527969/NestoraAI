from app.agents.lead_agent import LeadAgent
from app.agents.analysis_agent import AnalysisAgent
from app.agents.outreach_agent import OutreachAgent


class AIAgent:
    def __init__(self):
        self.leads = LeadAgent()
        self.analysis = AnalysisAgent()
        self.outreach = OutreachAgent()

    async def run(self, request):
        leads = await self.leads.search(
            business_type=request.business_type,
            location=request.location,
            quantity=request.quantity,
        )

        analyzed = 0
        outreach_generated = 0

        for lead in leads:
            if request.analyze_websites:
                await self.analysis.analyze(lead)
                analyzed += 1

            if request.generate_outreach:
                await self.outreach.generate(lead)
                outreach_generated += 1

        return {
            "searched": len(leads),
            "analyzed": analyzed,
            "outreach_generated": outreach_generated,
            "leads": leads,
        }