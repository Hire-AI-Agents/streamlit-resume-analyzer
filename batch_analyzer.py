import os
import json
import streamlit as st
import subprocess
import time
import glob
from pathlib import Path
from impact_v_template import get_scoring_template

# Set page configuration
st.set_page_config(
    page_title="IMPACT-V Resume Analyzer",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Create necessary directories
os.makedirs("src/resumes", exist_ok=True)
os.makedirs("results", exist_ok=True)

# Custom CSS for styling
st.markdown("""
<style>
    .report-card {
        background-color: #f8f9fa;
        border-radius: 10px;
        padding: 20px;
        margin-bottom: 20px;
        border-left: 5px solid #2D7FF9;
    }
    .qualified {
        border-left: 5px solid #28A745;
    }
    .qualified-unavailable {
        border-left: 5px solid #FFC107;
    }
    .not-qualified {
        border-left: 5px solid #DC3545;
    }
    .verdict {
        font-weight: bold;
        padding: 5px 10px;
        border-radius: 5px;
        display: inline-block;
    }
    .verdict-qualified {
        background-color: #d4edda;
        color: #155724;
    }
    .verdict-qualified-unavailable {
        background-color: #fff3cd;
        color: #856404;
    }
    .verdict-not-qualified {
        background-color: #f8d7da;
        color: #721c24;
    }
    .score-container {
        display: flex;
        align-items: center;
        margin-bottom: 10px;
    }
    .score-label {
        min-width: 150px;
        margin-right: 10px;
    }
    .score-bar {
        flex-grow: 1;
        height: 8px;
        background-color: #e9ecef;
        border-radius: 4px;
        overflow: hidden;
    }
    .score-bar-fill {
        height: 100%;
        border-radius: 4px;
    }
    .score-value {
        margin-left: 10px;
        font-weight: bold;
    }
    .download-container {
        position: sticky;
        bottom: 0;
        padding: 10px;
        background-color: white;
        border-top: 1px solid #e6e6e6;
        text-align: right;
    }
    
    .resume-filters {
        padding: 10px;
        background-color: #f8f9fa;
        border-radius: 10px;
        margin-bottom: 20px;
    }
</style>
""", unsafe_allow_html=True)

def get_results_files():
    """Get all results files"""
    return sorted(glob.glob("results/*.json"), key=os.path.getmtime, reverse=True)

def delete_result_file(file_path):
    """Delete a result file"""
    if os.path.exists(file_path):
        os.remove(file_path)
        return True
    return False

def analyze_resumes(resumes, model, role_type="Head of Sales"):
    """Analyze resumes"""
    
    # Ensure directories exist
    os.makedirs("results", exist_ok=True)
    os.makedirs("src/resumes", exist_ok=True)
    
    # Track progress
    progress_text = st.empty()
    progress_bar = st.progress(0)
    
    all_results = []
    
    for i, resume in enumerate(resumes):
        progress_text.text(f"Processing resume {i+1}/{len(resumes)}: {resume.name}")
        
        # Save uploaded file
        resume_path = Path("src/resumes") / resume.name
        with open(resume_path, "wb") as f:
            f.write(resume.getbuffer())
        
        # Calculate output paths
        resume_filename = resume.name.split('.')[0]
        output_json = f"results/{resume_filename}_result.json"
        
        # Run analysis
        cmd = [
            "python", "resume_matcher_impact.py",
            "-r", str(resume_path),
            "-m", model,
            "-o", output_json
        ]
        
        try:
            process = subprocess.run(cmd, check=True, capture_output=True, text=True)
            st.code(process.stdout, language="text")
            
            # Read results
            if os.path.exists(output_json):
                with open(output_json, "r") as f:
                    result = json.load(f)
                    all_results.append(result)
        except subprocess.CalledProcessError as e:
            st.error(f"Error processing {resume.name}: {e.stderr}")
        
        # Update progress
        progress_bar.progress((i + 1) / len(resumes))
    
    # Clear progress indicators
    progress_text.empty()
    progress_bar.empty()
    
    return all_results

def display_results(results_file):
    """Display results from a JSON file"""
    with open(results_file, "r") as f:
        result = json.load(f)
    
    # Determine verdict class
    verdict = result.get("verdict", "").upper()
    verdict_class = "not-qualified"
    if "QUALIFIED" in verdict and "NOT" not in verdict:
        if "UNAVAILABLE" in verdict:
            verdict_class = "qualified-unavailable"
        else:
            verdict_class = "qualified"
    
    st.markdown(f"<div class='report-card {verdict_class}'>", unsafe_allow_html=True)
    
    # Header with name and role
    st.subheader(f"{result.get('name', 'Candidate')} - {result.get('current_role', 'Unknown Role')}")
    
    # Verdict
    verdict_style_class = f"verdict-{verdict_class}"
    st.markdown(f"<div class='verdict {verdict_style_class}'>{verdict}</div>", unsafe_allow_html=True)
    
    # Overall score
    score = result.get("overall_score", 0)
    score_color = "#28A745" if score >= 75 else "#FFC107" if score >= 50 else "#DC3545"
    st.markdown(
        f"""
        <div class='score-container'>
            <div class='score-label'>Overall Score</div>
            <div class='score-bar'>
                <div class='score-bar-fill' style='width:{score}%; background-color:{score_color}'></div>
            </div>
            <div class='score-value'>{score}%</div>
        </div>
        """, 
        unsafe_allow_html=True
    )
    
    # Full markdown report
    st.markdown("### IMPACT-V Assessment Report")
    st.markdown(result.get("report_markdown", "No report available"))
    
    st.markdown("</div>", unsafe_allow_html=True)

def main():
    """Main function for the Streamlit app"""
    
    st.title("IMPACT-V Resume Analyzer")
    
    # Sidebar configuration
    with st.sidebar:
        st.header("Configuration")
        
        analysis_mode = st.radio(
            "Select Mode",
            ["Upload & Analyze", "View Previous Results"]
        )
        
        if analysis_mode == "Upload & Analyze":
            st.subheader("Analysis Settings")
            model = st.selectbox(
                "Choose AI Model",
                ["openai", "openai-fast", "anthropic"],
                index=0,
                help="Select the AI model to use for analysis"
            )
            
            role_type = st.selectbox(
                "Target Role",
                ["Head of Sales", "Sales Manager", "Sales Executive", "Account Manager", "Business Development Manager"],
                index=0,
                help="Select the target role to evaluate candidates against"
            )
    
    # Main content
    if analysis_mode == "Upload & Analyze":
        # Resume upload section
        st.header("Resume Upload")
        uploaded_files = st.file_uploader(
            "Upload resumes (PDF or DOCX)",
            type=["pdf", "docx"],
            accept_multiple_files=True
        )
        
        if uploaded_files:
            st.write(f"Uploaded {len(uploaded_files)} resume(s)")
            
            if st.button("Start Analysis", type="primary"):
                with st.spinner("Analyzing resumes..."):
                    results = analyze_resumes(uploaded_files, model, role_type)
                
                if results:
                    st.success(f"Successfully analyzed {len(results)} resume(s)")
                else:
                    st.warning("No results were generated. Please check the logs.")
                
                # Show the results
                results_files = get_results_files()
                if results_files:
                    st.header("Analysis Results")
                    for result_file in results_files[:len(uploaded_files)]:
                        display_results(result_file)
    
    else:  # View Previous Results mode
        results_files = get_results_files()
        
        if not results_files:
            st.info("No previous results found. Upload and analyze resumes to generate results.")
        else:
            st.header("Previous Analysis Results")
            
            for result_file in results_files:
                display_results(result_file)
                if st.button(f"Delete Result", key=f"delete_{os.path.basename(result_file)}"):
                    if delete_result_file(result_file):
                        st.success("Result deleted successfully")
                        st.experimental_rerun()

if __name__ == "__main__":
    main() 