# IMPACT-V Resume Analyzer

A streamlined tool for analyzing resumes with OpenAI/Anthropic models using the IMPACT-V scoring framework.

## Features

- Upload multiple resumes (PDF or DOCX format)
- Process them in batch with GPT-4o or Claude
- Display structured scoring based on the IMPACT-V framework
- Visual representation of candidate scores
- Save and review previous analysis results

## Quick Start

1. Clone this repository
2. Install dependencies: `pip install -r requirements.txt`
3. Set your OpenAI API key in `.env` file
4. Run the app: `streamlit run batch_analyzer.py`

## Project Structure

- `batch_analyzer.py` - Streamlit UI interface
- `resume_matcher_impact.py` - Core resume analysis logic
- `impact_v_template.py` - IMPACT-V scoring template

## IMPACT-V Scoring Framework

The IMPACT-V framework evaluates candidates across six key dimensions:

- **Industry Fit**: Experience and knowledge of relevant industry sectors
- **Market Knowledge**: Understanding of the business landscape and regional expertise
- **Performance Record**: Quantifiable achievements and target attainment
- **Approach & Solutions**: Sales methodology and solution selling capabilities
- **Capability to Lead**: Team building and cross-functional collaboration skills
- **Time-to-Value**: Potential speed to productivity and network advantages

## Requirements

- Python 3.7+
- OpenAI API key or Anthropic API key
- PyPDF2
- Streamlit
- json5
- termcolor 