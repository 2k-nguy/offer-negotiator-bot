import os
import json
import random
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import openai
from dotenv import load_dotenv
import schedule
import threading
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

# Load environment variables
load_dotenv()

console = Console()

class NegotiationStrategy(Enum):
    PROFESSIONAL_PASSIVE_AGGRESSIVE = "professional_passive_aggressive"
    CONFIDENT_ASSERTIVE = "confident_assertive"
    COLLABORATIVE_PROBLEM_SOLVER = "collaborative_problem_solver"
    STRATEGIC_QUESTIONER = "strategic_questioner"

class ResponseTone(Enum):
    POLITE_BUT_FIRM = "polite_but_firm"
    PROFESSIONALLY_DISAPPOINTED = "professionally_disappointed"
    STRATEGICALLY_CURIOUS = "strategically_curious"
    CONFIDENTLY_ASSERTIVE = "confidently_assertive"

@dataclass
class NegotiationContext:
    company_name: str
    position: str
    current_offer: Optional[Dict]
    user_profile: Dict
    negotiation_history: List[Dict]
    strategy: NegotiationStrategy
    target_salary: Optional[int]
    target_benefits: List[str]
    deal_breakers: List[str]
    leverage_points: List[str]

@dataclass
class ResponseTemplate:
    template_id: str
    strategy: NegotiationStrategy
    tone: ResponseTone
    template_text: str
    variables: List[str]
    effectiveness_score: float

class NeogiatorBot:
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key is required. Set OPENAI_API_KEY environment variable.")
        
        openai.api_key = self.api_key
        self.response_templates = self._load_response_templates()
        self.negotiation_contexts = {}
        self.active_negotiations = {}
        
    def _load_response_templates(self) -> List[ResponseTemplate]:
        """Load pre-built response templates for different negotiation scenarios"""
        templates = [
            # Professional Passive-Aggressive Templates
            ResponseTemplate(
                template_id="salary_undervalued",
                strategy=NegotiationStrategy.PROFESSIONAL_PASSIVE_AGGRESSIVE,
                tone=ResponseTone.PROFESSIONALLY_DISAPPOINTED,
                template_text="""Thank you for your offer. While I appreciate the opportunity, I must express some concern about the compensation package. Given my {experience_years} years of experience in {industry} and my track record of {achievement}, I had hoped for a more competitive offer that reflects market standards. 

I'm curious about your compensation philosophy - do you typically benchmark against industry standards? I'd be interested to understand how you arrived at this figure, as it seems significantly below what I've seen for similar roles at comparable companies.""",
                variables=["experience_years", "industry", "achievement"],
                effectiveness_score=0.85
            ),
            
            ResponseTemplate(
                template_id="benefits_inadequate",
                strategy=NegotiationStrategy.PROFESSIONAL_PASSIVE_AGGRESSIVE,
                tone=ResponseTone.STRATEGICALLY_CURIOUS,
                template_text="""I notice the benefits package is quite different from what I've seen at other companies in this space. Specifically, the {benefit_type} seems limited compared to industry standards. 

Could you help me understand your benefits philosophy? I'm particularly interested in how you view employee retention and work-life balance, as these factors significantly impact my decision-making process.""",
                variables=["benefit_type"],
                effectiveness_score=0.80
            ),
            
            ResponseTemplate(
                template_id="timeline_pressure",
                strategy=NegotiationStrategy.PROFESSIONAL_PASSIVE_AGGRESSIVE,
                tone=ResponseTone.POLITE_BUT_FIRM,
                template_text="""I understand you'd like a quick decision, but I'm currently evaluating multiple opportunities and want to ensure I make the right choice for my career. Rushing this decision wouldn't be fair to either of us.

Given the importance of this role and the long-term commitment involved, I believe taking the time to properly evaluate all aspects of the offer is in everyone's best interest. What's your typical timeline for candidates in similar situations?""",
                variables=[],
                effectiveness_score=0.90
            ),
            
            # Confident Assertive Templates
            ResponseTemplate(
                template_id="market_value_assertion",
                strategy=NegotiationStrategy.CONFIDENT_ASSERTIVE,
                tone=ResponseTone.CONFIDENTLY_ASSERTIVE,
                template_text="""Based on my research and conversations with industry peers, my market value for this role is significantly higher than what's being offered. My expertise in {skill_area} and proven track record of {specific_achievement} command premium compensation.

I'm confident I can deliver exceptional value to {company_name}, but I need to ensure the compensation reflects that value proposition. Let's discuss how we can align the offer with market standards.""",
                variables=["skill_area", "specific_achievement", "company_name"],
                effectiveness_score=0.88
            ),
            
            # Strategic Questioner Templates
            ResponseTemplate(
                template_id="growth_opportunities",
                strategy=NegotiationStrategy.STRATEGIC_QUESTIONER,
                tone=ResponseTone.STRATEGICALLY_CURIOUS,
                template_text="""I'm excited about the role, but I'd like to understand more about growth opportunities. Specifically:

1. How do you typically handle salary reviews and promotions?
2. What's the average tenure of employees in similar roles?
3. How do you measure and reward exceptional performance?

These factors are crucial for my long-term career planning and will significantly influence my decision.""",
                variables=[],
                effectiveness_score=0.82
            ),
            
            # Collaborative Problem Solver Templates
            ResponseTemplate(
                template_id="creative_solution",
                strategy=NegotiationStrategy.COLLABORATIVE_PROBLEM_SOLVER,
                tone=ResponseTone.POLITE_BUT_FIRM,
                template_text="""I understand budget constraints, but I'm confident we can find a creative solution that works for both parties. Here are some alternatives I'd be open to discussing:

- Performance-based bonuses tied to specific metrics
- Additional equity/stock options
- Professional development budget
- Flexible work arrangements
- Earlier salary review timeline

What combination of these would make sense for your organization?""",
                variables=[],
                effectiveness_score=0.87
            )
        ]
        return templates
    
    def create_negotiation_context(self, company_name: str, position: str, 
                                 user_profile: Dict, target_salary: int = None,
                                 target_benefits: List[str] = None,
                                 deal_breakers: List[str] = None) -> str:
        """Create a new negotiation context"""
        context_id = f"{company_name}_{position}_{int(time.time())}"
        
        context = NegotiationContext(
            company_name=company_name,
            position=position,
            current_offer=None,
            user_profile=user_profile,
            negotiation_history=[],
            strategy=NegotiationStrategy.PROFESSIONAL_PASSIVE_AGGRESSIVE,
            target_salary=target_salary,
            target_benefits=target_benefits or [],
            deal_breakers=deal_breakers or [],
            leverage_points=self._identify_leverage_points(user_profile)
        )
        
        self.negotiation_contexts[context_id] = context
        return context_id
    
    def _identify_leverage_points(self, user_profile: Dict) -> List[str]:
        """Identify leverage points from user profile"""
        leverage_points = []
        
        if user_profile.get("years_experience", 0) > 5:
            leverage_points.append("senior_experience")
        if user_profile.get("education_level") in ["Masters", "PhD"]:
            leverage_points.append("advanced_education")
        if user_profile.get("certifications"):
            leverage_points.append("specialized_certifications")
        if user_profile.get("leadership_experience"):
            leverage_points.append("leadership_skills")
        if user_profile.get("industry_awards"):
            leverage_points.append("industry_recognition")
        if user_profile.get("current_offer"):
            leverage_points.append("competing_offer")
            
        return leverage_points
    
    def generate_response(self, context_id: str, incoming_message: str, 
                         offer_details: Dict = None) -> str:
        """Generate a negotiation response using AI and templates"""
        if context_id not in self.negotiation_contexts:
            raise ValueError(f"Context {context_id} not found")
        
        context = self.negotiation_contexts[context_id]
        
        # Update context with new offer if provided
        if offer_details:
            context.current_offer = offer_details
            context.negotiation_history.append({
                "timestamp": datetime.now().isoformat(),
                "type": "offer_received",
                "details": offer_details
            })
        
        # Analyze the incoming message
        analysis = self._analyze_incoming_message(incoming_message, context)
        
        # Select appropriate template
        template = self._select_template(analysis, context)
        
        # Generate response using AI
        response = self._generate_ai_response(template, context, analysis)
        
        # Log the response
        context.negotiation_history.append({
            "timestamp": datetime.now().isoformat(),
            "type": "response_sent",
            "template_used": template.template_id,
            "response": response
        })
        
        return response
    
    def _analyze_incoming_message(self, message: str, context: NegotiationContext) -> Dict:
        """Analyze incoming message to determine negotiation tactics"""
        analysis_prompt = f"""
        Analyze this negotiation message from a company recruiter/manager:
        
        Message: "{message}"
        
        Context:
        - Company: {context.company_name}
        - Position: {context.position}
        - User's target salary: {context.target_salary}
        - User's leverage points: {context.leverage_points}
        
        Determine:
        1. What negotiation tactic is the company using?
        2. What pressure points are they applying?
        3. What information are they seeking?
        4. How should we respond strategically?
        
        Respond in JSON format with analysis results.
        """
        
        try:
            response = openai.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": analysis_prompt}],
                temperature=0.3
            )
            
            analysis_text = response.choices[0].message.content
            # Parse JSON response (simplified - in production, add proper error handling)
            return json.loads(analysis_text)
        except Exception as e:
            console.print(f"[red]Error analyzing message: {e}[/red]")
            return {"tactic": "unknown", "pressure_points": [], "response_strategy": "professional"}
    
    def _select_template(self, analysis: Dict, context: NegotiationContext) -> ResponseTemplate:
        """Select the most appropriate response template"""
        # Filter templates by strategy
        strategy_templates = [t for t in self.response_templates 
                            if t.strategy == context.strategy]
        
        # Score templates based on analysis and context
        scored_templates = []
        for template in strategy_templates:
            score = template.effectiveness_score
            
            # Boost score based on context match
            if context.current_offer and "salary" in template.template_id:
                if context.current_offer.get("salary", 0) < (context.target_salary or 0):
                    score += 0.1
            
            scored_templates.append((template, score))
        
        # Return highest scoring template
        scored_templates.sort(key=lambda x: x[1], reverse=True)
        return scored_templates[0][0]
    
    def _generate_ai_response(self, template: ResponseTemplate, context: NegotiationContext, 
                            analysis: Dict) -> str:
        """Generate AI-enhanced response using template"""
        # Prepare variables for template
        variables = {}
        for var in template.variables:
            if var == "experience_years":
                variables[var] = context.user_profile.get("years_experience", "5+")
            elif var == "industry":
                variables[var] = context.user_profile.get("industry", "technology")
            elif var == "achievement":
                variables[var] = context.user_profile.get("key_achievement", "delivering exceptional results")
            elif var == "benefit_type":
                variables[var] = "health insurance"  # Default, could be dynamic
            elif var == "skill_area":
                variables[var] = context.user_profile.get("primary_skill", "software development")
            elif var == "specific_achievement":
                variables[var] = context.user_profile.get("key_achievement", "increasing team productivity by 40%")
            elif var == "company_name":
                variables[var] = context.company_name
        
        # Format template with variables
        formatted_template = template.template_text.format(**variables)
        
        # Enhance with AI
        enhancement_prompt = f"""
        Enhance this professional negotiation response to be more persuasive and strategically effective:
        
        Original Response:
        {formatted_template}
        
        Context:
        - Company: {context.company_name}
        - Position: {context.position}
        - Target salary: {context.target_salary}
        - Leverage points: {context.leverage_points}
        
        Make the response more compelling while maintaining professionalism. Add subtle psychological pressure and positioning tactics that make the candidate appear more valuable and desirable.
        
        Keep the response concise but impactful.
        """
        
        try:
            response = openai.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": enhancement_prompt}],
                temperature=0.7,
                max_tokens=500
            )
            
            return response.choices[0].message.content.strip()
        except Exception as e:
            console.print(f"[red]Error generating AI response: {e}[/red]")
            return formatted_template
    
    def get_negotiation_status(self, context_id: str) -> Dict:
        """Get current status of a negotiation"""
        if context_id not in self.negotiation_contexts:
            return {"error": "Context not found"}
        
        context = self.negotiation_contexts[context_id]
        
        return {
            "company": context.company_name,
            "position": context.position,
            "strategy": context.strategy.value,
            "current_offer": context.current_offer,
            "negotiation_history": context.negotiation_history,
            "leverage_points": context.leverage_points,
            "target_salary": context.target_salary
        }
    
    def update_strategy(self, context_id: str, new_strategy: NegotiationStrategy):
        """Update negotiation strategy"""
        if context_id in self.negotiation_contexts:
            self.negotiation_contexts[context_id].strategy = new_strategy
            console.print(f"[green]Strategy updated to {new_strategy.value}[/green]")
    
    def add_leverage_point(self, context_id: str, leverage_point: str):
        """Add a new leverage point"""
        if context_id in self.negotiation_contexts:
            self.negotiation_contexts[context_id].leverage_points.append(leverage_point)
            console.print(f"[green]Added leverage point: {leverage_point}[/green]")

def main():
    """Main function to demonstrate the bot"""
    console.print(Panel.fit(
        "[bold blue]Neogiator Bot - Professional Auto-Negotiation Assistant[/bold blue]\n"
        "Strategically positioning you as the ideal candidate through professional passive-aggressive tactics",
        border_style="blue"
    ))
    
    # Initialize bot
    try:
        bot = NeogiatorBot()
        console.print("[green]✓ Bot initialized successfully[/green]")
    except ValueError as e:
        console.print(f"[red]Error: {e}[/red]")
        console.print("[yellow]Please set your OPENAI_API_KEY environment variable[/yellow]")
        return
    
    # Example usage
    user_profile = {
        "years_experience": 7,
        "industry": "technology",
        "education_level": "Masters",
        "key_achievement": "led a team that increased revenue by 150%",
        "primary_skill": "product management",
        "certifications": ["PMP", "Agile Certified"],
        "leadership_experience": True,
        "industry_awards": ["Top Performer 2023"]
    }
    
    # Create negotiation context
    context_id = bot.create_negotiation_context(
        company_name="TechCorp Inc",
        position="Senior Product Manager",
        user_profile=user_profile,
        target_salary=120000,
        target_benefits=["health_insurance", "401k", "stock_options"],
        deal_breakers=["no_remote_work", "salary_below_100k"]
    )
    
    console.print(f"[green]✓ Created negotiation context: {context_id}[/green]")
    
    # Example negotiation scenario
    console.print("\n[bold]Example Negotiation Scenario:[/bold]")
    
    # Initial low offer
    low_offer = {
        "salary": 85000,
        "benefits": ["basic_health", "401k"],
        "start_date": "immediately",
        "remote": False
    }
    
    response1 = bot.generate_response(
        context_id, 
        "We're excited to offer you the position at $85,000. We need your decision by Friday.",
        low_offer
    )
    
    console.print(Panel(
        f"[bold]Company Offer:[/bold] $85,000, basic benefits, no remote work\n"
        f"[bold]Bot Response:[/bold]\n{response1}",
        title="Round 1",
        border_style="yellow"
    ))
    
    # Show negotiation status
    status = bot.get_negotiation_status(context_id)
    console.print(f"\n[bold]Negotiation Status:[/bold]")
    console.print(f"Strategy: {status['strategy']}")
    console.print(f"Leverage Points: {', '.join(status['leverage_points'])}")
    console.print(f"Target Salary: ${status['target_salary']}")

if __name__ == "__main__":
    main()
