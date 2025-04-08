#!/usr/bin/env python3
"""
Resume Job Matcher - Modified for IMPACT-V Framework
A tool to match resumes to job descriptions using AI models.
Adapted from the original by sliday, with IMPACT-V scoring framework integration.
"""

import os
import sys
import json
import re
import time
import argparse
# Try different imports for PyPDF2 to handle case sensitivity issues
try:
    import PyPDF2
except ImportError:
    try:
        import pypdf2 as PyPDF2
    except ImportError:
        try:
            from pypdf import PdfReader
            # Create compatibility layer
            class PyPDF2:
                class PdfReader(PdfReader):
                    pass
        except ImportError:
            print("Error: Could not import PDF processing library. Please install PyPDF2 or pypdf.")
            sys.exit(1)
            
import tqdm
import json5
from termcolor import colored
from pathlib import Path
from datetime import datetime
from impact_v_template import get_scoring_template

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Import OpenAI
try:
    import openai
    openai_installed = True
except ImportError:
    openai_installed = False

# Import Anthropic
try:
    import anthropic
    anthropic_installed = True
except ImportError:
    anthropic_installed = False

# Check for Streamlit
try:
    import streamlit as st
    streamlit_available = True
except ImportError:
    streamlit_available = False

# Environment variables for API keys
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
ANTHROPIC_API_KEY = os.environ.get('ANTHROPIC_API_KEY')

# If using Streamlit and keys are in secrets, use them
if streamlit_available:
    try:
        if 'openai_api_key' in st.secrets:
            OPENAI_API_KEY = st.secrets['openai_api_key']
        if 'anthropic_api_key' in st.secrets:
            ANTHROPIC_API_KEY = st.secrets['anthropic_api_key']
    except:
        pass

# Model configurations
ANTHROPIC_MODEL = os.environ.get('ANTHROPIC_MODEL', 'claude-3-5-sonnet-20240620')
OPENAI_MODEL = os.environ.get('OPENAI_MODEL', 'gpt-4o')
OPENAI_FAST_MODEL = os.environ.get('OPENAI_FAST_MODEL', 'gpt-4o-mini-2024-07-18')
DEFAULT_MAX_TOKENS = int(os.environ.get('DEFAULT_MAX_TOKENS', 1000))
GPT_4O_CONTEXT_WINDOW = int(os.environ.get('GPT_4O_CONTEXT_WINDOW', 128000))

# Default Head of Sales job description
DEFAULT_JOB_DESCRIPTION = """
Head of Sales

Job Overview:
We are seeking an experienced Head of Sales with a proven track record in driving revenue growth and leading high-performance sales teams. As the Head of Sales, you will be responsible for developing and executing sales strategies, building key customer relationships, and achieving sales targets across our target markets.

Responsibilities:
- Lead and develop a high-performing sales team, providing coaching, mentorship, and setting clear performance expectations
- Develop and implement effective sales strategies aligned with company goals
- Build and maintain relationships with key clients, partners, and stakeholders
- Analyze market trends and competition to identify new opportunities
- Create accurate sales forecasts and track performance against targets
- Work closely with marketing, product, and customer success teams to ensure alignment
- Report on sales performance to executive leadership

Requirements:
- Proven track record of consistently meeting or exceeding sales targets
- Experience in B2B sales, preferably in the SaaS, technology, or financial services industry
- Strong understanding of sales methodologies and CRM systems
- Exceptional communication, presentation, and negotiation skills
- Ability to build and maintain strong customer relationships at all levels
- Experience in hiring, developing, and retaining top sales talent
- Bachelor's degree in Business, Marketing, or related field
- MBA or relevant advanced degree preferred
"""

class ResumeJobMatcher:
    """
    A class to match resumes to job descriptions using AI models.
    Uses IMPACT-V framework for candidate assessment.
    """
    
    def __init__(self, 
                 resume_path=None, 
                 job_desc_path=None, 
                 output_file=None,
                 model="openai"):
        """
        Initialize the ResumeJobMatcher class.
        
        Args:
            resume_path (str): Path to the resume file (PDF)
            job_desc_path (str): Path to the job description file (TXT) or None to use default
            output_file (str): Path to save the output file (JSON)
            model (str): AI model to use ("openai", "openai-fast", or "anthropic")
        """
        self.resume_path = resume_path
        self.job_desc_path = job_desc_path
        self.output_file = output_file
        self.model = model
        
        # Check required parameters
        if not resume_path:
            raise ValueError("Resume path is required.")
        
        # Ensure directories exist for output
        if output_file:
            os.makedirs(os.path.dirname(output_file) or '.', exist_ok=True)
        
        # Initialize results structure
        self.results = {
            "name": "",
            "current_role": "",
            "location": "",
            "years_of_experience": 0,
            "summary": "",
            "overall_score": 0,
            "verdict": "",
            "impact_scores": {},
            "report_markdown": ""
        }
        
        # Setup AI client based on model selection
        try:
            self._setup_ai_client()
        except Exception as e:
            error_msg = f"Error setting up AI client: {str(e)}"
            print(colored(error_msg, "red"))
            if streamlit_available:
                st.error(error_msg)
            raise
    
    def _setup_ai_client(self):
        """Set up the AI client based on the model selection."""
        if self.model.startswith("openai"):
            if not openai_installed:
                error_msg = "Error: OpenAI package not installed. Run: pip install openai"
                print(colored(error_msg, "red"))
                if streamlit_available:
                    st.error(error_msg)
                sys.exit(1)
            if not OPENAI_API_KEY:
                error_msg = "Error: OpenAI API key not found. Set OPENAI_API_KEY environment variable or add to Streamlit secrets."
                print(colored(error_msg, "red"))
                if streamlit_available:
                    st.error(error_msg)
                sys.exit(1)
                
            self.client = openai.OpenAI(api_key=OPENAI_API_KEY)
            
            # Select the model
            if self.model == "openai-fast":
                self.model_name = OPENAI_FAST_MODEL
            else:
                self.model_name = OPENAI_MODEL
                
            print(colored(f"Using OpenAI model: {self.model_name}", "blue"))
                
        elif self.model == "anthropic":
            if not anthropic_installed:
                error_msg = "Error: Anthropic package not installed. Run: pip install anthropic"
                print(colored(error_msg, "red"))
                if streamlit_available:
                    st.error(error_msg)
                sys.exit(1)
            if not ANTHROPIC_API_KEY:
                error_msg = "Error: Anthropic API key not found. Set ANTHROPIC_API_KEY environment variable or add to Streamlit secrets."
                print(colored(error_msg, "red"))
                if streamlit_available:
                    st.error(error_msg)
                sys.exit(1)
                
            self.client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
            self.model_name = ANTHROPIC_MODEL
            print(colored(f"Using Anthropic model: {self.model_name}", "blue"))
        else:
            error_msg = f"Error: Unknown model {self.model}. Use 'openai', 'openai-fast', or 'anthropic'."
            print(colored(error_msg, "red"))
            if streamlit_available:
                st.error(error_msg)
            sys.exit(1)
    
    def extract_text_from_pdf(self, pdf_path):
        """
        Extract text from a PDF file.
        
        Args:
            pdf_path (str): Path to the PDF file
            
        Returns:
            str: Extracted text
        """
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ""
                for page_num in range(len(pdf_reader.pages)):
                    text += pdf_reader.pages[page_num].extract_text()
                return text
        except Exception as e:
            print(colored(f"Error extracting text from PDF: {e}", "red"))
            return ""
    
    def read_job_description(self, job_desc_path=None):
        """
        Read job description from a text file or use default.
        
        Args:
            job_desc_path (str): Path to the job description file
            
        Returns:
            str: Job description text
        """
        if not job_desc_path:
            return DEFAULT_JOB_DESCRIPTION
            
        try:
            with open(job_desc_path, 'r', encoding='utf-8') as file:
                return file.read()
        except Exception as e:
            print(colored(f"Error reading job description file: {e}", "red"))
            print(colored("Using default Head of Sales job description.", "yellow"))
            return DEFAULT_JOB_DESCRIPTION
    
    def analyze_resume(self, resume_text, job_description, role_type="Head of Sales"):
        """
        Analyze a resume against a job description using an AI model.
        
        Args:
            resume_text (str): Resume text
            job_description (str): Job description text
            role_type (str): Role type for IMPACT-V scoring
            
        Returns:
            dict: Analysis results
        """
        print(colored("Analyzing resume...", "blue"))
        
        # Get IMPACT-V scoring template
        impact_v_template = get_scoring_template(role_type)
        
        # Prepare the prompt for AI
        system_prompt = f"""
        You are an expert HR recruitment specialist with expertise in evaluating resumes for {role_type} positions.
        
        You will analyze a resume and compare it to a job description to determine the candidate's fit.
        Use the IMPACT-V scoring framework to evaluate the candidate thoroughly.
        """
        
        user_prompt = f"""
        # Resume:
        ```
        {resume_text}
        ```
        
        # Job Description:
        ```
        {job_description}
        ```
        
        # Instructions:
        Analyze the resume against the job description using the IMPACT-V framework.
        
        First, extract key candidate information:
        - Name
        - Current role
        - Location
        - Years of experience
        
        Then score the candidate on each IMPACT-V dimension (0-100 scale):
        - Industry Fit: Evaluate the candidate's experience and knowledge of relevant industry sectors
        - Market Knowledge: Assess their understanding of the business landscape and regional expertise
        - Performance Record: Review quantifiable achievements and target attainment
        - Approach & Solutions: Analyze their sales methodology and solution selling capabilities
        - Capability to Lead: Evaluate team building, development, and cross-functional collaboration skills
        - Time-to-Value: Consider their potential speed to productivity and network leverage
        
        Calculate an overall score (0-100) based on the IMPACT-V dimensions.
        
        Determine a final verdict: "QUALIFIED", "QUALIFIED BUT UNAVAILABLE", or "NOT QUALIFIED"
        
        Finally, create a detailed assessment report using this template:
        
        {impact_v_template}
        
        Return your analysis in the following JSON format:
        {{
            "name": "Candidate name",
            "current_role": "Current role title",
            "location": "Candidate location",
            "years_of_experience": years_number,
            "summary": "Brief summary of candidate's background and fit",
            "impact_scores": {{
                "industry_fit": {{
                    "score": score_0_to_100,
                    "evidence": "Evidence from resume supporting this score"
                }},
                "market_knowledge": {{
                    "score": score_0_to_100,
                    "evidence": "Evidence from resume supporting this score"
                }},
                "performance_record": {{
                    "score": score_0_to_100,
                    "evidence": "Evidence from resume supporting this score"
                }},
                "approach_solutions": {{
                    "score": score_0_to_100,
                    "evidence": "Evidence from resume supporting this score"
                }},
                "capability_lead": {{
                    "score": score_0_to_100,
                    "evidence": "Evidence from resume supporting this score"
                }},
                "time_value": {{
                    "score": score_0_to_100,
                    "evidence": "Evidence from resume supporting this score"
                }}
            }},
            "overall_score": overall_score_0_to_100,
            "verdict": "QUALIFIED/QUALIFIED BUT UNAVAILABLE/NOT QUALIFIED",
            "report_markdown": "full_markdown_report_based_on_template"
        }}
        
        Use only the information available in the resume. If information is missing, make a reasonable assessment based on what is provided.
        """
        
        # Call the appropriate AI model
        if self.model.startswith("openai"):
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=DEFAULT_MAX_TOKENS,
                response_format={"type": "json_object"}
            )
            raw_response = response.choices[0].message.content
            
        elif self.model == "anthropic":
            response = self.client.messages.create(
                model=self.model_name,
                max_tokens=DEFAULT_MAX_TOKENS,
                system=system_prompt,
                messages=[
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.2
            )
            raw_response = response.content[0].text
        
        # Parse the JSON response
        try:
            # Use json5 to be more forgiving with potential formatting issues
            result = json5.loads(raw_response)
            return result
        except Exception as e:
            print(colored(f"Error parsing AI response: {e}", "red"))
            print(colored("Raw response:", "yellow"))
            print(raw_response)
            return None
    
    def process(self, role_type="Head of Sales"):
        """
        Process the resume and job description.
        
        Args:
            role_type (str): Role type for IMPACT-V scoring
            
        Returns:
            dict: Analysis results
        """
        # Extract text from resume
        print(colored(f"Extracting text from resume: {self.resume_path}", "blue"))
        resume_text = self.extract_text_from_pdf(self.resume_path)
        if not resume_text:
            print(colored("Error: Could not extract text from resume.", "red"))
            return None
        
        # Read job description
        job_description = self.read_job_description(self.job_desc_path)
        
        # Analyze resume
        results = self.analyze_resume(resume_text, job_description, role_type)
        if not results:
            print(colored("Error: Could not analyze resume.", "red"))
            return None
        
        # Save results
        self.results = results
        if self.output_file:
            print(colored(f"Saving results to: {self.output_file}", "blue"))
            with open(self.output_file, 'w', encoding='utf-8') as file:
                json.dump(results, file, indent=2)
        
        return results
    
    def print_results(self):
        """Print the analysis results to the console."""
        if not self.results:
            print(colored("No results available.", "red"))
            return
        
        # Extract results
        name = self.results.get("name", "Unknown")
        current_role = self.results.get("current_role", "Unknown")
        location = self.results.get("location", "Unknown")
        years_experience = self.results.get("years_of_experience", 0)
        overall_score = self.results.get("overall_score", 0)
        verdict = self.results.get("verdict", "Unknown")
        
        # Set verdict color based on result
        if "QUALIFIED" in verdict and "NOT" not in verdict:
            verdict_color = "green" if "UNAVAILABLE" not in verdict else "yellow"
        else:
            verdict_color = "red"
        
        # Set score color based on score
        score_color = "green" if overall_score >= 75 else "yellow" if overall_score >= 50 else "red"
        
        # Print header
        print("\n" + "=" * 80)
        print(colored(f"Resume Analysis: {name} - {current_role}", "cyan", attrs=["bold"]))
        print("=" * 80 + "\n")
        
        # Print candidate info
        print(colored("Candidate Information:", "blue", attrs=["bold"]))
        print(f"- Location: {location}")
        print(f"- Years of Experience: {years_experience}")
        print(f"- Overall Score: " + colored(f"{overall_score}/100", score_color, attrs=["bold"]))
        print(f"- Verdict: " + colored(verdict, verdict_color, attrs=["bold"]))
        print()
        
        # Print IMPACT-V scores
        print(colored("IMPACT-V Scores:", "blue", attrs=["bold"]))
        impact_scores = self.results.get("impact_scores", {})
        
        for category, data in impact_scores.items():
            if isinstance(data, dict) and "score" in data:
                score = data["score"]
                score_color = "green" if score >= 75 else "yellow" if score >= 50 else "red"
                print(f"- {category.replace('_', ' ').title()}: " + colored(f"{score}/100", score_color))
        
        print("\n" + "=" * 80 + "\n")
        
        # Print markdown report excerpt
        print(colored("Summary Assessment:", "blue", attrs=["bold"]))
        report = self.results.get("report_markdown", "")
        # Print first few lines of the report
        report_lines = report.strip().split('\n')
        for i, line in enumerate(report_lines):
            if i >= 10:  # Just show first 10 lines
                print("...")
                break
            print(line)
        
        print("\n" + colored("Full report saved to output file.", "green") + "\n")


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Resume Analyzer with IMPACT-V Framework')
    
    parser.add_argument('-r', '--resume', required=True, help='Path to resume file (PDF)')
    parser.add_argument('-j', '--job-description', help='Path to job description file (TXT) - optional')
    parser.add_argument('-o', '--output', help='Path to output file (JSON)')
    parser.add_argument('-m', '--model', choices=['openai', 'openai-fast', 'anthropic'], 
                        default='openai', help='AI model to use')
    parser.add_argument('-t', '--role-type', default='Head of Sales',
                        help='Role type for IMPACT-V scoring')
    
    return parser.parse_args()


def main():
    """Main function."""
    args = parse_arguments()
    
    # Create ResumeJobMatcher instance
    matcher = ResumeJobMatcher(
        resume_path=args.resume,
        job_desc_path=args.job_description,
        output_file=args.output,
        model=args.model
    )
    
    # Process resume
    results = matcher.process(role_type=args.role_type)
    
    # Print results
    if results:
        matcher.print_results()
    

if __name__ == "__main__":
    main() 