#!/usr/bin/env python3
"""
Test script for resume parsing functionality
"""

import os
import tempfile
from resume_parser import ResumeParser
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()

def create_sample_resume():
    """Create a sample resume text for testing"""
    sample_text = """
    John Smith
    john.smith@email.com
    (555) 123-4567
    
    PROFESSIONAL SUMMARY
    Experienced Software Engineer with 7 years of experience in full-stack development.
    Led teams that increased revenue by 150% and improved system performance by 40%.
    
    WORK EXPERIENCE
    
    Senior Software Engineer | TechCorp Inc | 2020-2024
    - Led a team of 5 developers in building scalable web applications
    - Implemented microservices architecture reducing system downtime by 60%
    - Mentored junior developers and conducted code reviews
    
    Software Engineer | StartupXYZ | 2018-2020
    - Developed RESTful APIs using Python and Django
    - Collaborated with product team to define technical requirements
    - Improved application performance by 30%
    
    EDUCATION
    Master of Science in Computer Science | University of Technology | 2018
    Bachelor of Science in Software Engineering | State University | 2016
    
    SKILLS
    Python, JavaScript, React, Node.js, Django, PostgreSQL, AWS, Docker, Git
    
    CERTIFICATIONS
    AWS Solutions Architect, PMP, Agile Certified Practitioner
    
    ACHIEVEMENTS
    - Led team that increased revenue by 150%
    - Improved system performance by 40%
    - Reduced system downtime by 60%
    - Top Performer Award 2023
    """
    return sample_text

def test_resume_parsing():
    """Test the resume parsing functionality"""
    console.print(Panel.fit(
        "[bold blue]Resume Parser Test[/bold blue]\n"
        "Testing resume parsing functionality",
        border_style="blue"
    ))
    
    # Check for API key
    if not os.getenv("OPENAI_API_KEY"):
        console.print("[yellow]⚠️  No OpenAI API key found. Testing with fallback parsing only.[/yellow]")
    
    try:
        # Initialize parser
        parser = ResumeParser()
        console.print("[green]✅ Resume parser initialized[/green]")
        
        # Create sample resume file
        sample_text = create_sample_resume()
        
        # Write to temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write(sample_text)
            temp_file = f.name
        
        try:
            # Parse resume
            console.print("[blue]📄 Parsing sample resume...[/blue]")
            parsed_resume = parser.parse_resume(temp_file)
            
            # Display results
            display_parsing_results(parsed_resume)
            
            # Test user profile creation
            console.print("\n[blue]👤 Creating user profile...[/blue]")
            user_profile = parser.create_user_profile(parsed_resume)
            
            display_user_profile(user_profile)
            
        finally:
            # Clean up temp file
            os.unlink(temp_file)
            
    except Exception as e:
        console.print(f"[red]❌ Error: {e}[/red]")

def display_parsing_results(parsed_resume):
    """Display parsed resume results"""
    table = Table(title="📋 Parsed Resume Data")
    table.add_column("Field", style="cyan")
    table.add_column("Value", style="magenta")
    
    table.add_row("Name", parsed_resume.name or "Not found")
    table.add_row("Email", parsed_resume.email or "Not found")
    table.add_row("Phone", parsed_resume.phone or "Not found")
    table.add_row("Years Experience", str(parsed_resume.years_experience))
    table.add_row("Education Level", parsed_resume.education_level)
    table.add_row("Industry", parsed_resume.industry)
    table.add_row("Skills Count", str(len(parsed_resume.skills)))
    table.add_row("Certifications Count", str(len(parsed_resume.certifications)))
    table.add_row("Achievements Count", str(len(parsed_resume.achievements)))
    table.add_row("Work Experience Count", str(len(parsed_resume.work_experience)))
    
    console.print(table)
    
    # Display skills
    if parsed_resume.skills:
        console.print(f"\n[bold]Skills:[/bold] {', '.join(parsed_resume.skills[:10])}")
    
    # Display certifications
    if parsed_resume.certifications:
        console.print(f"\n[bold]Certifications:[/bold] {', '.join(parsed_resume.certifications)}")
    
    # Display achievements
    if parsed_resume.achievements:
        console.print(f"\n[bold]Achievements:[/bold]")
        for achievement in parsed_resume.achievements[:3]:
            console.print(f"  • {achievement}")

def display_user_profile(user_profile):
    """Display user profile created from parsed resume"""
    table = Table(title="👤 Generated User Profile")
    table.add_column("Field", style="cyan")
    table.add_column("Value", style="magenta")
    
    table.add_row("Years Experience", str(user_profile.get("years_experience", 0)))
    table.add_row("Industry", user_profile.get("industry", "Not found"))
    table.add_row("Education Level", user_profile.get("education_level", "Not found"))
    table.add_row("Primary Skill", user_profile.get("primary_skill", "Not found"))
    table.add_row("Key Achievement", user_profile.get("key_achievement", "Not found")[:50] + "..." if len(user_profile.get("key_achievement", "")) > 50 else user_profile.get("key_achievement", "Not found"))
    table.add_row("Leadership Experience", str(user_profile.get("leadership_experience", False)))
    table.add_row("Skills Count", str(len(user_profile.get("skills", []))))
    table.add_row("Certifications Count", str(len(user_profile.get("certifications", []))))
    table.add_row("Industry Awards Count", str(len(user_profile.get("industry_awards", []))))
    
    console.print(table)

def main():
    """Main test function"""
    test_resume_parsing()
    
    console.print("\n[bold green]🎉 Resume parsing test completed![/bold green]")
    console.print("\n[bold]Next steps:[/bold]")
    console.print("1. Upload your actual resume to test with real data")
    console.print("2. Run the web interface: python app.py")
    console.print("3. Test the full negotiation workflow")

if __name__ == "__main__":
    main()
