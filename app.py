from dotenv import load_dotenv
load_dotenv()
import streamlit as st
import os
from PyPDF2 import PdfReader
import google.generativeai as genai
import re
import altair as alt
import pandas as pd

# Configure Gemini AI
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

class ATSAnalyzer:
    @staticmethod
    def get_gemini_response(input_prompt, pdf_text, job_description):
        try:
            model = genai.GenerativeModel('gemini-2.0-flash-exp')
            response = model.generate_content([input_prompt, pdf_text, job_description])
            return response.text
        except Exception as e:
            st.error(f"Error generating response: {str(e)}")
            return None

    @staticmethod
    def extract_text_from_pdf(uploaded_file):
        try:
            pdf_reader = PdfReader(uploaded_file)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text()
            return text
        except Exception as e:
            st.error(f"Error extracting PDF text: {str(e)}")
            return None

def main():
    # Page configuration
    st.set_page_config(
        page_title="ATS Resume Expert",
        page_icon="📄",
        layout="wide"
    )

    # Custom CSS
    st.markdown("""
        <style>
        .stButton>button {
            width: 100%;
            background-color: #0066cc;
            color: white;
            border-radius: 8px;
            font-weight: bold;
        }
        .stButton>button:hover {
            background-color: #0052a3;
        }
        .success-message {
            padding: 0.8rem;
            border-radius: 0.5rem;
            background-color: #d4edda;
            color: #155724;
            font-weight: 500;
        }
        .result-box {
            padding: 1rem;
            border-radius: 10px;
            background-color: #1e1e1e;
            border: 1px solid #444;
            color: #f5f5f5;
            font-size: 15px;
            line-height: 1.6;
        }
        </style>
    """, unsafe_allow_html=True)

    # Header
    st.title("📄 ATS Resume Analyzer")
    st.caption("AI-powered tool to evaluate your resume against job descriptions 🚀")

    # Use tabs for cleaner UI
    tab1, tab2 = st.tabs(["📝 Job Description & Resume", "📊 Analysis"])

    with tab1:
        col1, col2 = st.columns([1, 1])

        with col1:
            st.subheader("📝 Job Description")
            job_description = st.text_area(
                "Paste the job description",
                height=200,
                placeholder="Paste the complete job description here..."
            )

        with col2:
            st.subheader("📎 Resume Upload")
            uploaded_file = st.file_uploader(
                "Upload your resume (PDF format)",
                type=["pdf"],
                help="Upload your resume in PDF format"
            )

            if uploaded_file:
                st.markdown('<p class="success-message">✅ PDF uploaded successfully!</p>', unsafe_allow_html=True)

    with tab2:
        if uploaded_file and job_description:
            st.subheader("🔍 Analysis Options")
            analysis_type = st.radio(
                "Choose analysis type:",
                ["Detailed Resume Review", "Match Percentage Analysis"],
                horizontal=True
            )

            if st.button("🚀 Analyze Resume"):
                with st.spinner("Analyzing your resume... Please wait ⏳"):
                    # Extract PDF text
                    pdf_text = ATSAnalyzer.extract_text_from_pdf(uploaded_file)

                    if pdf_text:
                        if analysis_type == "Detailed Resume Review":
                            prompt = """
                            As an experienced Technical Human Resource Manager, provide a detailed professional evaluation 
                            of the candidate's resume against the job description. Please analyze:
                            1. Overall alignment with the role
                            2. Key strengths and qualifications that match
                            3. Notable gaps or areas for improvement
                            4. Specific recommendations for enhancing the resume
                            5. Final verdict on suitability for the role
                            
                            Format the response with clear headings and professional language.
                            """
                        else:
                            prompt = """
                            As an ATS (Applicant Tracking System) expert, provide:
                            1. Overall match percentage (%)
                            2. Key matching keywords found
                            3. Important missing keywords
                            4. Skills gap analysis
                            5. Specific recommendations for improvement
                            
                            Start with the percentage match prominently displayed.
                            """

                        response = ATSAnalyzer.get_gemini_response(prompt, pdf_text, job_description)

                        if response:
                            # Extract % from response
                            match_percentage = None
                            match = re.search(r"(\d+)%", response)
                            if match:
                                match_percentage = int(match.group(1))

                            if match_percentage is not None:
                                st.subheader("📊 Match Percentage Overview")

                                # Donut chart with Altair
                                df = pd.DataFrame({
                                    'Category': ['Match', 'Gap'],
                                    'Value': [match_percentage, 100 - match_percentage]
                                })

                                chart = alt.Chart(df).mark_arc(innerRadius=70).encode(
                                    theta="Value",
                                    color=alt.Color("Category", scale=alt.Scale(
                                        domain=["Match", "Gap"],
                                        range=["#28a745", "#e0e0e0"]
                                    )),
                                    tooltip=["Category", "Value"]
                                ).properties(width=300, height=300)

                                col1, col2 = st.columns([1, 1])
                                with col1:
                                    st.altair_chart(chart, use_container_width=False)
                                with col2:
                                    st.metric(label="Resume–Job Match", value=f"{match_percentage}%")

                            # Show detailed results
                            st.subheader("📑 Detailed Analysis")
                            st.markdown(f"<div class='result-box'>{response}</div>", unsafe_allow_html=True)

                            # Export option
                            st.download_button(
                                label="📥 Download Analysis",
                                data=response,
                                file_name="resume_analysis.txt",
                                mime="text/plain"
                            )
        else:
            st.info("👆 Upload your resume & provide job description in **Tab 1** to start the analysis.")

    # Footer
    st.markdown("---")
    st.markdown(
        "Made with ❤️ by Karthy | "
        "This tool uses AI for resume analysis but should be used alongside human judgment."
    )

if __name__ == "__main__":
    main()
