import os
import re
import json
from typing import Dict, List, Optional, Tuple
import PyPDF2
from docx import Document
import pytesseract
from PIL import Image
import openai
from dataclasses import dataclass

@dataclass
class ParsedResume:
    """Structured data extracted from resume"""
    name: str
    email: str
    phone: str
    years_experience: int
    education_level: str
    industry: str
    skills: List[str]
    certifications: List[str]
    achievements: List[str]
    work_experience: List[Dict]
    education: List[Dict]
    projects: List[Dict]
    languages: List[str]
    raw_text: str

class ResumeParser:
    """Parse resumes from various formats and extract structured information"""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if self.api_key:
            openai.api_key = self.api_key
    
    def parse_resume(self, file_path: str) -> ParsedResume:
        """Parse resume from file and return structured data"""
        # Extract text based on file type
        text = self._extract_text(file_path)
        
        # Use AI to parse and structure the information
        structured_data = self._parse_with_ai(text)
        
        # Create ParsedResume object
        return ParsedResume(
            name=structured_data.get("name", ""),
            email=structured_data.get("email", ""),
            phone=structured_data.get("phone", ""),
            years_experience=structured_data.get("years_experience", 0),
            education_level=structured_data.get("education_level", "Bachelor's"),
            industry=structured_data.get("industry", "technology"),
            skills=structured_data.get("skills", []),
            certifications=structured_data.get("certifications", []),
            achievements=structured_data.get("achievements", []),
            work_experience=structured_data.get("work_experience", []),
            education=structured_data.get("education", []),
            projects=structured_data.get("projects", []),
            languages=structured_data.get("languages", []),
            raw_text=text
        )
    
    def _extract_text(self, file_path: str) -> str:
        """Extract text from resume file based on format"""
        file_extension = os.path.splitext(file_path)[1].lower()
        
        if file_extension == '.pdf':
            return self._extract_from_pdf(file_path)
        elif file_extension == '.docx':
            return self._extract_from_docx(file_path)
        elif file_extension in ['.doc']:
            return self._extract_from_doc(file_path)
        elif file_extension in ['.txt']:
            return self._extract_from_txt(file_path)
        elif file_extension in ['.png', '.jpg', '.jpeg']:
            return self._extract_from_image(file_path)
        else:
            raise ValueError(f"Unsupported file format: {file_extension}")
    
    def _extract_from_pdf(self, file_path: str) -> str:
        """Extract text from PDF file"""
        text = ""
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
        except Exception as e:
            print(f"Error extracting PDF: {e}")
            # Try OCR as fallback
            return self._extract_from_image(file_path)
        return text
    
    def _extract_from_docx(self, file_path: str) -> str:
        """Extract text from DOCX file"""
        try:
            doc = Document(file_path)
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            return text
        except Exception as e:
            print(f"Error extracting DOCX: {e}")
            return ""
    
    def _extract_from_doc(self, file_path: str) -> str:
        """Extract text from DOC file (converted to DOCX first)"""
        # For DOC files, we'll need to convert or use OCR
        # This is a simplified approach - in production, you might want to use python-docx2txt
        return self._extract_from_image(file_path)
    
    def _extract_from_txt(self, file_path: str) -> str:
        """Extract text from TXT file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read()
        except Exception as e:
            print(f"Error reading TXT file: {e}")
            return ""
    
    def _extract_from_image(self, file_path: str) -> str:
        """Extract text from image using OCR"""
        try:
            image = Image.open(file_path)
            text = pytesseract.image_to_string(image)
            return text
        except Exception as e:
            print(f"Error extracting from image: {e}")
            return ""
    
    def _parse_with_ai(self, text: str) -> Dict:
        """Use AI to parse and structure resume information"""
        if not self.api_key:
            return self._fallback_parsing(text)
        
        prompt = f"""
        Parse this resume text and extract structured information. Return a JSON object with the following structure:
        
        {{
            "name": "Full name",
            "email": "email@example.com",
            "phone": "phone number",
            "years_experience": number of years of professional experience,
            "education_level": "High School", "Bachelor's", "Masters", or "PhD",
            "industry": "primary industry (technology, finance, healthcare, etc.)",
            "skills": ["skill1", "skill2", "skill3"],
            "certifications": ["cert1", "cert2"],
            "achievements": ["achievement1", "achievement2"],
            "work_experience": [
                {{
                    "title": "Job Title",
                    "company": "Company Name",
                    "duration": "Duration",
                    "description": "Job description"
                }}
            ],
            "education": [
                {{
                    "degree": "Degree Name",
                    "institution": "Institution Name",
                    "year": "Graduation Year"
                }}
            ],
            "projects": [
                {{
                    "name": "Project Name",
                    "description": "Project description",
                    "technologies": ["tech1", "tech2"]
                }}
            ],
            "languages": ["language1", "language2"]
        }}
        
        Resume text:
        {text}
        
        Extract as much information as possible. If information is not available, use appropriate defaults or empty arrays.
        """
        
        try:
            response = openai.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                max_tokens=2000
            )
            
            result = response.choices[0].message.content.strip()
            
            # Try to parse JSON
            try:
                return json.loads(result)
            except json.JSONDecodeError:
                # If JSON parsing fails, try to extract JSON from the response
                json_match = re.search(r'\{.*\}', result, re.DOTALL)
                if json_match:
                    return json.loads(json_match.group())
                else:
                    return self._fallback_parsing(text)
                    
        except Exception as e:
            print(f"Error with AI parsing: {e}")
            return self._fallback_parsing(text)
    
    def _fallback_parsing(self, text: str) -> Dict:
        """Fallback parsing using regex patterns when AI is not available"""
        # Extract email
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        email_match = re.search(email_pattern, text)
        email = email_match.group() if email_match else ""
        
        # Extract phone
        phone_pattern = r'(\+?1[-.\s]?)?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})'
        phone_match = re.search(phone_pattern, text)
        phone = phone_match.group() if phone_match else ""
        
        # Extract name (first line usually)
        lines = text.split('\n')
        name = lines[0].strip() if lines else ""
        
        # Extract skills (look for common skill keywords)
        skill_keywords = [
            'python', 'java', 'javascript', 'react', 'angular', 'vue', 'node.js',
            'sql', 'mongodb', 'postgresql', 'aws', 'azure', 'docker', 'kubernetes',
            'git', 'agile', 'scrum', 'project management', 'leadership', 'communication',
            'data analysis', 'machine learning', 'artificial intelligence', 'blockchain',
            'cybersecurity', 'devops', 'frontend', 'backend', 'full stack'
        ]
        
        skills = []
        text_lower = text.lower()
        for skill in skill_keywords:
            if skill in text_lower:
                skills.append(skill.title())
        
        # Estimate years of experience
        years_experience = 0
        experience_patterns = [
            r'(\d+)\s*years?\s*of\s*experience',
            r'experience:\s*(\d+)',
            r'(\d+)\+?\s*years?\s*in'
        ]
        
        for pattern in experience_patterns:
            match = re.search(pattern, text_lower)
            if match:
                years_experience = int(match.group(1))
                break
        
        # Extract education level
        education_level = "Bachelor's"
        if re.search(r'master|mba|msc|ma', text_lower):
            education_level = "Masters"
        elif re.search(r'phd|doctorate|ph\.d', text_lower):
            education_level = "PhD"
        elif re.search(r'associate|diploma', text_lower):
            education_level = "Associate"
        
        # Determine industry
        industry = "technology"
        industry_keywords = {
            'finance': ['finance', 'banking', 'investment', 'financial'],
            'healthcare': ['healthcare', 'medical', 'pharmaceutical', 'hospital'],
            'education': ['education', 'teaching', 'academic', 'university'],
            'consulting': ['consulting', 'advisory', 'strategy'],
            'marketing': ['marketing', 'advertising', 'brand', 'digital marketing'],
            'retail': ['retail', 'e-commerce', 'sales', 'customer service']
        }
        
        for ind, keywords in industry_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                industry = ind
                break
        
        return {
            "name": name,
            "email": email,
            "phone": phone,
            "years_experience": years_experience,
            "education_level": education_level,
            "industry": industry,
            "skills": skills[:10],  # Limit to top 10
            "certifications": [],
            "achievements": [],
            "work_experience": [],
            "education": [],
            "projects": [],
            "languages": []
        }
    
    def create_user_profile(self, parsed_resume: ParsedResume) -> Dict:
        """Convert parsed resume to user profile format expected by the bot"""
        # Extract key achievement from work experience or achievements
        key_achievement = ""
        if parsed_resume.achievements:
            key_achievement = parsed_resume.achievements[0]
        elif parsed_resume.work_experience:
            # Try to extract achievement from work experience descriptions
            for exp in parsed_resume.work_experience:
                desc = exp.get('description', '')
                if 'increased' in desc.lower() or 'improved' in desc.lower() or 'led' in desc.lower():
                    key_achievement = desc[:100] + "..." if len(desc) > 100 else desc
                    break
        
        # Determine primary skill
        primary_skill = ""
        if parsed_resume.skills:
            primary_skill = parsed_resume.skills[0]
        elif parsed_resume.work_experience:
            # Extract from job titles
            for exp in parsed_resume.work_experience:
                title = exp.get('title', '').lower()
                if 'manager' in title:
                    primary_skill = "Management"
                elif 'developer' in title or 'engineer' in title:
                    primary_skill = "Software Development"
                elif 'analyst' in title:
                    primary_skill = "Data Analysis"
                elif 'designer' in title:
                    primary_skill = "Design"
                break
        
        return {
            "years_experience": parsed_resume.years_experience,
            "industry": parsed_resume.industry,
            "education_level": parsed_resume.education_level,
            "key_achievement": key_achievement or f"Experienced {parsed_resume.industry} professional",
            "primary_skill": primary_skill or "Professional",
            "certifications": parsed_resume.certifications,
            "leadership_experience": any('manager' in exp.get('title', '').lower() or 'lead' in exp.get('title', '').lower() 
                                      for exp in parsed_resume.work_experience),
            "industry_awards": parsed_resume.achievements[:3],  # Top 3 achievements as awards
            "skills": parsed_resume.skills,
            "work_experience": parsed_resume.work_experience,
            "education": parsed_resume.education,
            "projects": parsed_resume.projects,
            "languages": parsed_resume.languages,
            "contact_info": {
                "name": parsed_resume.name,
                "email": parsed_resume.email,
                "phone": parsed_resume.phone
            }
        }
