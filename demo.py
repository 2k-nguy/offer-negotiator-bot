#!/usr/bin/env python3
"""
Neogiator Bot Demo Script
Demonstrates the bot's capabilities with example scenarios
"""

import os
import json
from neogiator_bot import NeogiatorBot, NegotiationStrategy
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
import time

console = Console()

def print_banner():
    """Print the Neogiator Bot banner"""
    banner = """
    ╔══════════════════════════════════════════════════════════════╗
    ║                    🤖 NEOGIATOR BOT 🤖                        ║
    ║              Professional Auto-Negotiation Assistant         ║
    ║                                                              ║
    ║  Strategically positioning you as the ideal candidate      ║
    ║  through professional passive-aggressive tactics           ║
    ╚══════════════════════════════════════════════════════════════╝
    """
    console.print(Panel(banner, style="bold blue"))

def create_sample_profile():
    """Create a sample user profile for demonstration"""
    return {
        "years_experience": 7,
        "industry": "technology",
        "education_level": "Masters",
        "key_achievement": "led a team that increased revenue by 150%",
        "primary_skill": "product management",
        "certifications": ["PMP", "Agile Certified", "AWS Solutions Architect"],
        "leadership_experience": True,
        "industry_awards": ["Top Performer 2023", "Innovation Award 2022"],
        "current_offer": None  # Simulating no current offer
    }

def run_demo_scenario(bot, scenario_name, company_message, offer_details=None):
    """Run a demo negotiation scenario"""
    console.print(f"\n[bold yellow]📋 Scenario: {scenario_name}[/bold yellow]")
    console.print(f"[bold]Company Message:[/bold] {company_message}")
    
    if offer_details:
        console.print(f"[bold]Offer Details:[/bold] {json.dumps(offer_details, indent=2)}")
    
    # Create context for this scenario
    context_id = bot.create_negotiation_context(
        company_name="DemoCorp",
        position="Senior Product Manager",
        user_profile=create_sample_profile(),
        target_salary=120000,
        target_benefits=["health_insurance", "401k", "stock_options", "remote_work"],
        deal_breakers=["salary_below_100k", "no_remote_work"]
    )
    
    # Generate response
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Generating response...", total=None)
        
        try:
            response = bot.generate_response(
                context_id=context_id,
                incoming_message=company_message,
                offer_details=offer_details
            )
            
            progress.update(task, description="Response generated!")
            time.sleep(0.5)  # Brief pause for effect
            
        except Exception as e:
            console.print(f"[red]Error generating response: {e}[/red]")
            response = "Error: Could not generate response. Please check your OpenAI API key."
    
    # Display response
    console.print(Panel(
        response,
        title="🤖 Neogiator Bot Response",
        border_style="green"
    ))
    
    # Show negotiation status
    status = bot.get_negotiation_status(context_id)
    display_negotiation_status(status)
    
    return context_id

def display_negotiation_status(status):
    """Display negotiation status in a table"""
    table = Table(title="📊 Negotiation Status")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="magenta")
    
    table.add_row("Company", status["company"])
    table.add_row("Position", status["position"])
    table.add_row("Strategy", status["strategy"].replace("_", " ").title())
    table.add_row("Target Salary", f"${status['target_salary']:,}" if status["target_salary"] else "Not set")
    table.add_row("Current Offer", f"${status['current_offer']['salary']:,}" if status["current_offer"] and status["current_offer"].get("salary") else "None")
    table.add_row("Leverage Points", ", ".join(status["leverage_points"]))
    table.add_row("History Entries", str(len(status["negotiation_history"])))
    
    console.print(table)

def demonstrate_strategies():
    """Demonstrate different negotiation strategies"""
    console.print("\n[bold blue]🎭 Strategy Demonstration[/bold blue]")
    
    strategies_info = [
        {
            "name": "Professional Passive-Aggressive",
            "description": "Maintains courtesy while subtly questioning offers",
            "best_for": "Most initial negotiations"
        },
        {
            "name": "Confident Assertive", 
            "description": "Direct statements about market value and expectations",
            "best_for": "When you have strong leverage"
        },
        {
            "name": "Collaborative Problem Solver",
            "description": "Offers creative alternatives and focuses on mutual benefit",
            "best_for": "Budget-constrained companies"
        },
        {
            "name": "Strategic Questioner",
            "description": "Asks probing questions to gather information",
            "best_for": "Information gathering and positioning"
        }
    ]
    
    for strategy in strategies_info:
        console.print(f"\n[bold]{strategy['name']}[/bold]")
        console.print(f"  [italic]{strategy['description']}[/italic]")
        console.print(f"  [dim]Best for: {strategy['best_for']}[/dim]")

def main():
    """Main demo function"""
    print_banner()
    
    # Check for API key
    if not os.getenv("OPENAI_API_KEY"):
        console.print("[red]❌ Error: OPENAI_API_KEY environment variable not set[/red]")
        console.print("[yellow]Please set your OpenAI API key to run the demo:[/yellow]")
        console.print("[dim]export OPENAI_API_KEY='your-api-key-here'[/dim]")
        return
    
    try:
        # Initialize bot
        console.print("[green]🚀 Initializing Neogiator Bot...[/green]")
        bot = NeogiatorBot()
        console.print("[green]✅ Bot initialized successfully![/green]")
        
        # Show available strategies
        demonstrate_strategies()
        
        # Demo scenarios
        scenarios = [
            {
                "name": "Lowball Salary Offer",
                "message": "We're excited to offer you the position at $85,000. This is competitive for our market and we need your decision by Friday.",
                "offer": {
                    "salary": 85000,
                    "benefits": ["basic_health", "401k"],
                    "start_date": "immediately",
                    "remote": False
                }
            },
            {
                "name": "Benefits Limitation",
                "message": "Our benefits package is standard for the industry. We can't offer more due to budget constraints.",
                "offer": {
                    "salary": 95000,
                    "benefits": ["basic_health"],
                    "remote": False
                }
            },
            {
                "name": "Urgency Pressure",
                "message": "We have other candidates waiting and need your decision by tomorrow. This is a time-sensitive hire.",
                "offer": {
                    "salary": 100000,
                    "benefits": ["health_insurance", "401k"],
                    "start_date": "next_week"
                }
            },
            {
                "name": "Remote Work Denial",
                "message": "We don't offer remote work. It's company policy and we believe in face-to-face collaboration.",
                "offer": {
                    "salary": 110000,
                    "benefits": ["health_insurance", "401k", "stock_options"],
                    "remote": False
                }
            }
        ]
        
        console.print("\n[bold green]🎬 Running Demo Scenarios[/bold green]")
        
        for i, scenario in enumerate(scenarios, 1):
            console.print(f"\n[bold blue]Scenario {i}/{len(scenarios)}[/bold blue]")
            context_id = run_demo_scenario(
                bot, 
                scenario["name"], 
                scenario["message"], 
                scenario["offer"]
            )
            
            if i < len(scenarios):
                console.print("\n[dim]Press Enter to continue to next scenario...[/dim]")
                input()
        
        # Final summary
        console.print("\n[bold green]🎉 Demo Complete![/bold green]")
        console.print("\n[bold]Key Takeaways:[/bold]")
        console.print("• The bot maintains professional courtesy while asserting your value")
        console.print("• Responses are tailored to specific negotiation tactics")
        console.print("• Multiple strategies can be employed based on the situation")
        console.print("• The bot positions you as a thoughtful, market-aware candidate")
        
        console.print("\n[bold yellow]💡 Next Steps:[/bold yellow]")
        console.print("1. Set up your own profile with real information")
        console.print("2. Use the web interface for easier interaction")
        console.print("3. Customize strategies based on your negotiation style")
        console.print("4. Practice with different scenarios before real negotiations")
        
    except Exception as e:
        console.print(f"[red]❌ Error: {e}[/red]")
        console.print("[yellow]Please check your setup and try again.[/yellow]")

if __name__ == "__main__":
    main()
