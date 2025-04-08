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
   ```bash
   git clone https://github.com/Hire-AI-Agents/streamlit-resume-analyzer.git
   cd streamlit-resume-analyzer
   ```

2. Install dependencies
   ```bash
   pip install -r requirements.txt
   ```

3. Set your OpenAI API key
   ```bash
   # For Linux/Mac
   export OPENAI_API_KEY="your-api-key-here"
   
   # For Windows
   set OPENAI_API_KEY=your-api-key-here
   ```

4. Run the app
   ```bash
   streamlit run batch_analyzer.py
   ```

## Deploying to Streamlit.com

1. Fork this repository to your GitHub account
2. On Streamlit.com, create a new app from your forked repo
3. In your app's settings, add the following secret:
   ```
   openai_api_key = "your-api-key-here"
   ```
4. Deploy the app

## Project Structure

- `batch_analyzer.py` - Streamlit UI interface
- `resume_matcher_impact.py` - Core resume analysis logic
- `impact_v_template.py` - IMPACT-V scoring template
- `src/resumes/` - Directory where uploaded resumes are temporarily stored
- `results/` - Directory where analysis results are saved

## IMPACT-V Scoring Framework

The IMPACT-V framework evaluates candidates across six key dimensions:

- **Industry Fit**: Experience and knowledge of relevant industry sectors
- **Market Knowledge**: Understanding of the business landscape and regional expertise
- **Performance Record**: Quantifiable achievements and target attainment
- **Approach & Solutions**: Sales methodology and solution selling capabilities
- **Capability to Lead**: Team building and cross-functional collaboration skills
- **Time-to-Value**: Potential speed to productivity and network advantages

## Troubleshooting

### "Error: API key not found"
- For local deployment: Ensure the `OPENAI_API_KEY` environment variable is set
- For Streamlit.com: Add the API key in the app's Secrets management

### "Error processing resume"
- Check if the PDF file is valid and readable
- Verify that PDF extraction is working properly
- Confirm API key has sufficient credits

### "Directory error"
- Check file permissions in the `src/resumes` and `results` directories
- Ensure these directories exist in your deployment

## Requirements

- Python 3.7+
- OpenAI API key or Anthropic API key
- PyPDF2
- Streamlit
- json5
- termcolor

## Development Notes

To contribute to this project:

1. Create a fork of the repository
2. Make your changes
3. Ensure all tests pass
4. Submit a pull request

For any issues or suggestions, please open an issue on GitHub. 