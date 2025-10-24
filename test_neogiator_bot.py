import unittest
import json
from unittest.mock import patch, MagicMock
from neogiator_bot import NeogiatorBot, NegotiationStrategy, ResponseTone, NegotiationContext
import os

class TestNeogiatorBot(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures"""
        # Mock OpenAI API key for testing
        with patch.dict(os.environ, {'OPENAI_API_KEY': 'test-key'}):
            self.bot = NeogiatorBot()
        
        self.sample_user_profile = {
            "years_experience": 7,
            "industry": "technology",
            "education_level": "Masters",
            "key_achievement": "led a team that increased revenue by 150%",
            "primary_skill": "product management",
            "certifications": ["PMP", "Agile Certified"],
            "leadership_experience": True,
            "industry_awards": ["Top Performer 2023"]
        }
        
        self.sample_offer = {
            "salary": 85000,
            "benefits": ["basic_health", "401k"],
            "start_date": "immediately",
            "remote": False
        }

    def test_bot_initialization(self):
        """Test bot initialization"""
        self.assertIsNotNone(self.bot)
        self.assertIsNotNone(self.bot.response_templates)
        self.assertEqual(len(self.bot.response_templates), 6)  # Should have 6 templates

    def test_create_negotiation_context(self):
        """Test creating negotiation context"""
        context_id = self.bot.create_negotiation_context(
            company_name="TestCorp",
            position="Software Engineer",
            user_profile=self.sample_user_profile,
            target_salary=100000
        )
        
        self.assertIsNotNone(context_id)
        self.assertIn(context_id, self.bot.negotiation_contexts)
        
        context = self.bot.negotiation_contexts[context_id]
        self.assertEqual(context.company_name, "TestCorp")
        self.assertEqual(context.position, "Software Engineer")
        self.assertEqual(context.target_salary, 100000)
        self.assertEqual(context.strategy, NegotiationStrategy.PROFESSIONAL_PASSIVE_AGGRESSIVE)

    def test_leverage_points_identification(self):
        """Test leverage points identification"""
        context_id = self.bot.create_negotiation_context(
            company_name="TestCorp",
            position="Software Engineer",
            user_profile=self.sample_user_profile
        )
        
        context = self.bot.negotiation_contexts[context_id]
        leverage_points = context.leverage_points
        
        # Should identify multiple leverage points
        self.assertIn("senior_experience", leverage_points)
        self.assertIn("advanced_education", leverage_points)
        self.assertIn("specialized_certifications", leverage_points)
        self.assertIn("leadership_skills", leverage_points)
        self.assertIn("industry_recognition", leverage_points)

    @patch('openai.chat.completions.create')
    def test_generate_response_with_mock_ai(self, mock_openai):
        """Test response generation with mocked AI"""
        # Mock OpenAI response
        mock_response = MagicMock()
        mock_response.choices[0].message.content = json.dumps({
            "tactic": "lowball_offer",
            "pressure_points": ["urgency", "budget_constraints"],
            "response_strategy": "professional_pushback"
        })
        mock_openai.return_value = mock_response
        
        context_id = self.bot.create_negotiation_context(
            company_name="TestCorp",
            position="Software Engineer",
            user_profile=self.sample_user_profile,
            target_salary=100000
        )
        
        # Mock AI response for template enhancement
        mock_enhancement = MagicMock()
        mock_enhancement.choices[0].message.content = "Enhanced response with professional passive-aggressive tactics"
        mock_openai.side_effect = [mock_response, mock_enhancement]
        
        response = self.bot.generate_response(
            context_id=context_id,
            incoming_message="We're offering $70,000. We need your decision by Friday.",
            offer_details=self.sample_offer
        )
        
        self.assertIsNotNone(response)
        self.assertIsInstance(response, str)
        self.assertGreater(len(response), 50)  # Should be substantial response

    def test_template_selection(self):
        """Test template selection logic"""
        # Test salary-related template selection
        analysis = {
            "tactic": "lowball_offer",
            "pressure_points": ["urgency"],
            "response_strategy": "salary_pushback"
        }
        
        context_id = self.bot.create_negotiation_context(
            company_name="TestCorp",
            position="Software Engineer",
            user_profile=self.sample_user_profile,
            target_salary=100000
        )
        
        context = self.bot.negotiation_contexts[context_id]
        context.current_offer = {"salary": 70000}  # Below target
        
        template = self.bot._select_template(analysis, context)
        
        # Should select a salary-related template
        self.assertIn("salary", template.template_id.lower())

    def test_strategy_update(self):
        """Test strategy updating"""
        context_id = self.bot.create_negotiation_context(
            company_name="TestCorp",
            position="Software Engineer",
            user_profile=self.sample_user_profile
        )
        
        # Update strategy
        self.bot.update_strategy(context_id, NegotiationStrategy.CONFIDENT_ASSERTIVE)
        
        context = self.bot.negotiation_contexts[context_id]
        self.assertEqual(context.strategy, NegotiationStrategy.CONFIDENT_ASSERTIVE)

    def test_leverage_point_addition(self):
        """Test adding leverage points"""
        context_id = self.bot.create_negotiation_context(
            company_name="TestCorp",
            position="Software Engineer",
            user_profile=self.sample_user_profile
        )
        
        initial_count = len(self.bot.negotiation_contexts[context_id].leverage_points)
        
        self.bot.add_leverage_point(context_id, "competing_offer")
        
        new_count = len(self.bot.negotiation_contexts[context_id].leverage_points)
        self.assertEqual(new_count, initial_count + 1)
        self.assertIn("competing_offer", self.bot.negotiation_contexts[context_id].leverage_points)

    def test_negotiation_status(self):
        """Test getting negotiation status"""
        context_id = self.bot.create_negotiation_context(
            company_name="TestCorp",
            position="Software Engineer",
            user_profile=self.sample_user_profile,
            target_salary=100000
        )
        
        status = self.bot.get_negotiation_status(context_id)
        
        self.assertEqual(status["company"], "TestCorp")
        self.assertEqual(status["position"], "Software Engineer")
        self.assertEqual(status["target_salary"], 100000)
        self.assertIsInstance(status["leverage_points"], list)
        self.assertIsInstance(status["negotiation_history"], list)

    def test_response_templates_structure(self):
        """Test response templates have correct structure"""
        for template in self.bot.response_templates:
            self.assertIsNotNone(template.template_id)
            self.assertIsInstance(template.strategy, NegotiationStrategy)
            self.assertIsInstance(template.tone, ResponseTone)
            self.assertIsNotNone(template.template_text)
            self.assertIsInstance(template.variables, list)
            self.assertIsInstance(template.effectiveness_score, float)
            self.assertGreaterEqual(template.effectiveness_score, 0.0)
            self.assertLessEqual(template.effectiveness_score, 1.0)

class TestNegotiationScenarios(unittest.TestCase):
    """Test specific negotiation scenarios"""
    
    def setUp(self):
        with patch.dict(os.environ, {'OPENAI_API_KEY': 'test-key'}):
            self.bot = NeogiatorBot()
        
        self.user_profile = {
            "years_experience": 5,
            "industry": "finance",
            "education_level": "Bachelor's",
            "key_achievement": "reduced operational costs by 30%",
            "primary_skill": "financial analysis"
        }

    @patch('openai.chat.completions.create')
    def test_lowball_salary_scenario(self, mock_openai):
        """Test response to lowball salary offer"""
        mock_response = MagicMock()
        mock_response.choices[0].message.content = json.dumps({
            "tactic": "lowball_offer",
            "pressure_points": ["budget_constraints"],
            "response_strategy": "market_value_assertion"
        })
        mock_enhancement = MagicMock()
        mock_enhancement.choices[0].message.content = "Professional response questioning the salary offer"
        mock_openai.side_effect = [mock_response, mock_enhancement]
        
        context_id = self.bot.create_negotiation_context(
            company_name="FinanceCorp",
            position="Financial Analyst",
            user_profile=self.user_profile,
            target_salary=80000
        )
        
        lowball_offer = {"salary": 55000}
        
        response = self.bot.generate_response(
            context_id=context_id,
            incoming_message="We're offering $55,000. This is our standard rate for this position.",
            offer_details=lowball_offer
        )
        
        # Should contain elements questioning the offer
        self.assertIsNotNone(response)
        self.assertGreater(len(response), 100)

    @patch('openai.chat.completions.create')
    def test_urgency_pressure_scenario(self, mock_openai):
        """Test response to urgency pressure"""
        mock_response = MagicMock()
        mock_response.choices[0].message.content = json.dumps({
            "tactic": "urgency_pressure",
            "pressure_points": ["timeline", "other_candidates"],
            "response_strategy": "professional_patience"
        })
        mock_enhancement = MagicMock()
        mock_enhancement.choices[0].message.content = "Professional response about taking time to evaluate"
        mock_openai.side_effect = [mock_response, mock_enhancement]
        
        context_id = self.bot.create_negotiation_context(
            company_name="TechStartup",
            position="Data Scientist",
            user_profile=self.user_profile
        )
        
        response = self.bot.generate_response(
            context_id=context_id,
            incoming_message="We need your decision by tomorrow. We have other candidates waiting."
        )
        
        self.assertIsNotNone(response)
        # Should contain elements about taking time to evaluate

    @patch('openai.chat.completions.create')
    def test_benefits_negotiation_scenario(self, mock_openai):
        """Test benefits negotiation scenario"""
        mock_response = MagicMock()
        mock_response.choices[0].message.content = json.dumps({
            "tactic": "benefits_limitation",
            "pressure_points": ["budget"],
            "response_strategy": "benefits_inquiry"
        })
        mock_enhancement = MagicMock()
        mock_enhancement.choices[0].message.content = "Professional inquiry about benefits philosophy"
        mock_openai.side_effect = [mock_response, mock_enhancement]
        
        context_id = self.bot.create_negotiation_context(
            company_name="HealthCorp",
            position="Healthcare Analyst",
            user_profile=self.user_profile,
            target_benefits=["health_insurance", "401k", "flexible_hours"]
        )
        
        limited_benefits = {
            "salary": 70000,
            "benefits": ["basic_health"],
            "remote": False
        }
        
        response = self.bot.generate_response(
            context_id=context_id,
            incoming_message="Our benefits package is standard for the industry.",
            offer_details=limited_benefits
        )
        
        self.assertIsNotNone(response)

def run_scenario_tests():
    """Run comprehensive scenario tests"""
    print("Running Neogiator Bot Scenario Tests...")
    
    scenarios = [
        {
            "name": "Lowball Salary Offer",
            "company": "StartupCorp",
            "position": "Software Developer",
            "offer": {"salary": 60000, "benefits": ["basic_health"]},
            "message": "We're offering $60,000. This is competitive for our market.",
            "expected_elements": ["market", "competitive", "experience"]
        },
        {
            "name": "Urgency Pressure",
            "company": "FastTrack Inc",
            "position": "Project Manager",
            "offer": {"salary": 75000, "start_date": "immediately"},
            "message": "We need your decision by Friday. We have other candidates.",
            "expected_elements": ["time", "evaluate", "decision"]
        },
        {
            "name": "Benefits Limitation",
            "company": "ConservativeCorp",
            "position": "Business Analyst",
            "offer": {"salary": 80000, "benefits": ["basic_health", "401k"]},
            "message": "Our benefits are standard. We can't offer more.",
            "expected_elements": ["benefits", "standard", "philosophy"]
        },
        {
            "name": "Remote Work Denial",
            "company": "TraditionalCorp",
            "position": "Marketing Manager",
            "offer": {"salary": 85000, "remote": False},
            "message": "We don't offer remote work. It's company policy.",
            "expected_elements": ["remote", "policy", "flexibility"]
        }
    ]
    
    results = []
    
    for scenario in scenarios:
        print(f"\nTesting: {scenario['name']}")
        
        try:
            with patch.dict(os.environ, {'OPENAI_API_KEY': 'test-key'}):
                bot = NeogiatorBot()
            
            user_profile = {
                "years_experience": 6,
                "industry": "technology",
                "education_level": "Masters",
                "key_achievement": "increased team productivity by 40%",
                "primary_skill": "project management"
            }
            
            context_id = bot.create_negotiation_context(
                company_name=scenario["company"],
                position=scenario["position"],
                user_profile=user_profile,
                target_salary=90000,
                target_benefits=["health_insurance", "401k", "stock_options", "remote_work"]
            )
            
            # Mock AI responses
            with patch('openai.chat.completions.create') as mock_openai:
                mock_response = MagicMock()
                mock_response.choices[0].message.content = json.dumps({
                    "tactic": "test_tactic",
                    "pressure_points": ["test_pressure"],
                    "response_strategy": "test_strategy"
                })
                mock_enhancement = MagicMock()
                mock_enhancement.choices[0].message.content = f"Professional response for {scenario['name']}"
                mock_openai.side_effect = [mock_response, mock_enhancement]
                
                response = bot.generate_response(
                    context_id=context_id,
                    incoming_message=scenario["message"],
                    offer_details=scenario["offer"]
                )
            
            # Check if response contains expected elements
            response_lower = response.lower()
            elements_found = [elem for elem in scenario["expected_elements"] 
                            if elem in response_lower]
            
            result = {
                "scenario": scenario["name"],
                "success": len(elements_found) > 0,
                "elements_found": elements_found,
                "response_length": len(response),
                "response_preview": response[:100] + "..." if len(response) > 100 else response
            }
            
            results.append(result)
            print(f"✓ Success: {result['success']}")
            print(f"  Elements found: {result['elements_found']}")
            print(f"  Response length: {result['response_length']}")
            
        except Exception as e:
            print(f"✗ Failed: {str(e)}")
            results.append({
                "scenario": scenario["name"],
                "success": False,
                "error": str(e)
            })
    
    # Summary
    successful = sum(1 for r in results if r["success"])
    total = len(results)
    
    print(f"\n{'='*50}")
    print(f"Scenario Test Results: {successful}/{total} successful")
    print(f"{'='*50}")
    
    return results

if __name__ == "__main__":
    # Run unit tests
    unittest.main(argv=[''], exit=False, verbosity=2)
    
    # Run scenario tests
    scenario_results = run_scenario_tests()
