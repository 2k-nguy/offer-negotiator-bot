# Neogiator Bot 🤖💼

**Professional Auto-Negotiation Assistant**

A sophisticated AI-powered bot that uses professional passive-aggressive tactics to position you as the ideal candidate during job negotiations. The bot strategically crafts responses that compel companies to consider you as a strong potential hire while maintaining professional courtesy.

## ✨ Features

### 🎯 Core Capabilities
- **Professional Passive-Aggressive Negotiation**: Uses sophisticated tactics that maintain courtesy while asserting your value
- **AI-Powered Response Generation**: Leverages GPT-4 for dynamic, context-aware responses
- **Multiple Negotiation Strategies**: 
  - Professional Passive-Aggressive
  - Confident Assertive
  - Collaborative Problem Solver
  - Strategic Questioner
- **Real-time Strategy Adaptation**: Switch tactics based on company responses
- **Leverage Point Identification**: Automatically identifies your strengths and market advantages

### 🛠️ Technical Features
- **Resume Upload & Parsing**: Automatically extract information from PDF, DOC, DOCX, TXT, and image files
- **AI-Powered Resume Analysis**: Uses GPT-4 to intelligently parse and structure resume data
- **Web Interface**: Clean, intuitive dashboard for managing negotiations
- **Context Management**: Track multiple negotiations simultaneously
- **Response Templates**: Pre-built templates for common negotiation scenarios
- **Negotiation History**: Complete audit trail of all interactions
- **Status Monitoring**: Real-time tracking of negotiation progress

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- OpenAI API Key
- Modern web browser

### Installation

1. **Clone or Download** the project files
2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up Environment Variables**:
   Create a `.env` file in the project root:
   ```
   OPENAI_API_KEY=your_openai_api_key_here
   ```

4. **Run the Application**:
   ```bash
   python app.py
   ```

5. **Open Your Browser**:
   Navigate to `http://localhost:5000`

## 📖 Usage Guide

### 1. Upload Your Resume

Simply upload your resume file:
- **Supported Formats**: PDF, DOC, DOCX, TXT, PNG, JPG, JPEG
- **Automatic Parsing**: AI extracts your experience, skills, education, and achievements
- **Profile Review**: Review and confirm the extracted information
- **Minimal Input**: Only need to specify company name, position, and negotiation targets

### 2. Starting a Negotiation

1. Upload your resume and review the extracted profile
2. Enter company name, position, and negotiation targets
3. Click "Confirm Profile & Start Negotiation"
4. The bot will analyze your profile and identify leverage points
5. Choose your initial negotiation strategy

### 3. Managing Conversations

- **Input Company Messages**: Paste recruiter/manager communications
- **Generate Responses**: Let the bot craft professional responses
- **Monitor Status**: Track progress and adjust strategy
- **Review History**: Analyze all interactions

### 4. Strategy Adaptation

Switch between strategies based on company responses:
- **Professional Passive-Aggressive**: Default strategy for most situations
- **Confident Assertive**: When you have strong leverage
- **Collaborative Problem Solver**: For creative solutions
- **Strategic Questioner**: To gather information and position yourself

## 🎭 Negotiation Strategies Explained

### Professional Passive-Aggressive
**Best for**: Most initial negotiations
- Maintains courtesy while subtly questioning offers
- Uses phrases like "I'm curious about..." and "I had hoped for..."
- Positions you as thoughtful and market-aware

### Confident Assertive
**Best for**: When you have strong leverage
- Direct statements about market value
- Clear expectations and boundaries
- Confident tone backed by data

### Collaborative Problem Solver
**Best for**: Budget-constrained companies
- Offers creative alternatives
- Focuses on mutual benefit
- Suggests performance-based solutions

### Strategic Questioner
**Best for**: Information gathering
- Asks probing questions about growth
- Understands company culture and values
- Positions you as thoughtful and strategic

## 🔧 Advanced Configuration

### Resume Parsing

The bot uses advanced AI to parse resumes and extract:

**Personal Information:**
- Name, email, phone number
- Contact information

**Professional Details:**
- Years of experience
- Education level
- Industry classification
- Work experience history

**Skills & Achievements:**
- Technical skills
- Certifications
- Key achievements
- Project experience

**Fallback Parsing:**
If AI parsing fails, the bot uses regex patterns to extract basic information like email, phone, and common skills.

### Custom Response Templates

You can modify response templates in `neogiator_bot.py`:

```python
ResponseTemplate(
    template_id="custom_template",
    strategy=NegotiationStrategy.PROFESSIONAL_PASSIVE_AGGRESSIVE,
    tone=ResponseTone.PROFESSIONALLY_DISAPPOINTED,
    template_text="Your custom template here with {variables}",
    variables=["variable1", "variable2"],
    effectiveness_score=0.85
)
```

### Adding Leverage Points

The bot automatically identifies leverage points, but you can add custom ones:

```python
bot.add_leverage_point(context_id, "custom_leverage_point")
```

### Strategy Customization

Switch strategies mid-negotiation:

```python
bot.update_strategy(context_id, NegotiationStrategy.CONFIDENT_ASSERTIVE)
```

## 🧪 Testing

Run the comprehensive test suite:

```bash
python test_neogiator_bot.py
```

The test suite includes:
- Unit tests for core functionality
- Scenario tests for common negotiation situations
- Mock AI responses for consistent testing
- Edge case handling

## 📊 Example Scenarios

### Scenario 1: Lowball Salary Offer
**Company**: "We're offering $70,000. This is competitive for our market."
**Bot Response**: "Thank you for your offer. While I appreciate the opportunity, I must express some concern about the compensation package. Given my 7 years of experience in technology and my track record of leading teams that increased revenue by 150%, I had hoped for a more competitive offer that reflects market standards..."

### Scenario 2: Urgency Pressure
**Company**: "We need your decision by Friday. We have other candidates waiting."
**Bot Response**: "I understand you'd like a quick decision, but I'm currently evaluating multiple opportunities and want to ensure I make the right choice for my career. Rushing this decision wouldn't be fair to either of us..."

### Scenario 3: Benefits Limitation
**Company**: "Our benefits package is standard for the industry."
**Bot Response**: "I notice the benefits package is quite different from what I've seen at other companies in this space. Specifically, the health insurance seems limited compared to industry standards. Could you help me understand your benefits philosophy?"

## 🎯 Best Practices

### Do's ✅
- **Be Specific**: Provide detailed information about your experience and achievements
- **Set Clear Targets**: Define your salary range and must-have benefits
- **Monitor Responses**: Review bot responses before sending
- **Adapt Strategy**: Switch tactics based on company responses
- **Stay Professional**: Always maintain courtesy and professionalism

### Don'ts ❌
- **Don't Rush**: Let the bot handle timing pressure professionally
- **Don't Accept First Offers**: Use the bot to negotiate better terms
- **Don't Ignore Leverage**: Highlight your unique value propositions
- **Don't Be Aggressive**: The bot uses subtle psychological pressure
- **Don't Skip Research**: Provide accurate market information

## 🔒 Privacy & Security

- **Local Processing**: All data stays on your machine
- **API Security**: OpenAI API key is only used for response generation
- **No Data Storage**: Negotiation contexts are stored locally in memory
- **Secure Communication**: All web traffic uses HTTPS in production

## 🛠️ Troubleshooting

### Common Issues

**Bot not responding**:
- Check OpenAI API key is set correctly
- Verify internet connection
- Check API usage limits

**Web interface not loading**:
- Ensure Flask is installed: `pip install flask`
- Check port 5000 is available
- Try different browser

**Poor response quality**:
- Provide more detailed user profile
- Add specific leverage points
- Try different negotiation strategy

### Getting Help

1. Check the test suite for examples
2. Review the response templates
3. Verify your OpenAI API key
4. Check the console for error messages

## 🚀 Future Enhancements

- **Email Integration**: Direct email negotiation
- **LinkedIn Integration**: Profile-based leverage detection
- **Market Data**: Real-time salary benchmarking
- **Multi-language Support**: Negotiations in different languages
- **Mobile App**: Native mobile interface
- **Analytics Dashboard**: Negotiation success metrics

## 📄 License

This project is for educational and personal use. Please use responsibly and ethically in your job negotiations.

## 🤝 Contributing

Contributions are welcome! Areas for improvement:
- Additional response templates
- New negotiation strategies
- Enhanced AI prompts
- Better error handling
- Performance optimizations

---

**Remember**: This bot is designed to help you negotiate professionally and effectively. Always use it ethically and in good faith. The goal is to create win-win situations where both you and the company benefit from a fair, mutually beneficial arrangement.

**Happy Negotiating!** 🎉
