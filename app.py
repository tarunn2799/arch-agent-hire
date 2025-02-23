import streamlit as st
import json
import requests
import concurrent.futures
from pydantic import BaseModel, Field
from typing import Optional
from litellm import completion
from arch_prompts import PROMPTS
import gspread_utils
from uuid import uuid4
from thefuzz import fuzz
import re

# -------------------------------------------------------------------
# 1. Pydantic model for parsing the perplexity email response
# -------------------------------------------------------------------
class ArchFirm(BaseModel):
    recruiting_email: Optional[str] = Field(
        None, 
        description="What is the recruiting or careers contact email address listed on the firm's website or careers page?"
    )

# -------------------------------------------------------------------
# 2. LLM Agent for calls to the Gemini / GPT endpoints
# -------------------------------------------------------------------
class Agent:
    def __init__(self, sys_prompt: str, model: str = "gpt-4o"):
        self.sys_prompt = sys_prompt
        self.messages = [{"role": "system", "content": sys_prompt}]
        self.model = model

    def llm_call(self, prompt: str, response_format=None) -> str:
        self.messages.append({"role": "user", "content": prompt})
        try:
            response = completion(
                model=self.model,
                messages=self.messages,
                temperature=0.1,
                response_format=response_format
            )
            response_content = response.choices[0].message.content
            self.messages.append({"role": "assistant", "content": response_content})
            return response_content
        except Exception as e:
            st.warning(f"LLM call failed: {e}")
            return ""


# -------------------------------------------------------------------
# Helper functions to fetch from Perplexity in parallel
# -------------------------------------------------------------------
def get_firm_description(firm_name: str, pplx_api_key: str):
    """Calls Perplexity to get the firm description and extracts the reasoning."""
    url = "https://api.perplexity.ai/chat/completions"
    headers = {"Authorization": f"Bearer {pplx_api_key}"}

    payload = {
        "model": "sonar-reasoning-pro",
        "messages": [
            {
                "role": "system",
                "content": (
                    "For a given architecture firm, your task is to extract "
                    "a complete description about the firm including their focus areas, "
                    "specializations, notable projects, design philosophy, and overall "
                    "approach to architecture? Be precise and concise."
                )
            },
            {"role": "user", "content": f"Please extract info for : {firm_name}"},
        ],
    }

    response = requests.post(url, headers=headers, json=payload).json()
    full_content = response["choices"][0]["message"]["content"]

    try:
        firm_desc_reasoning = full_content.split("<think>")[1].split("</think>")[0]
    except:
        firm_desc_reasoning = "No reasoning available."
    firm_desc = full_content.split("</think>")[-1].strip()

    return firm_desc, firm_desc_reasoning


def get_recruiting_email(firm_name: str, pplx_api_key: str):
    """Calls Perplexity to get the recruiting email, returns (email, email_reasoning)."""
    url = "https://api.perplexity.ai/chat/completions"
    headers = {"Authorization": f"Bearer {pplx_api_key}"}

    payload = {
        "model": "sonar-reasoning-pro",
        "messages": [
            {
                "role": "system",
                "content": (
                    "For a given architecture firm, your task is to extract "
                    "their recruiting email address as listed on their careers/contact page. "
                    "Be precise. You must ONLY output a JSON object with the result."
                )
            },
            {
                "role": "user",
                "content": (
                    f"Recruiting email for : {firm_name}"
                    "\nPlease output a JSON object containing the following field: recruiting_email"
                ),
            },
        ],
        "response_format": {
            "type": "json_schema",
            "json_schema": {"schema": ArchFirm.model_json_schema()},
        },
    }

    response = requests.post(url, headers=headers, json=payload).json()
    full_content = response["choices"][0]["message"]["content"]

    try:
        recr_email_reasoning = full_content.split("<think>")[1].split("</think>")[0]
    except:
        recr_email_reasoning = "No reasoning available."

    try:
        json_str = full_content.split("```json")[-1].split("```")[0].strip()
        recruiting_email_data = json.loads(json_str)
        recruiting_email = recruiting_email_data.get("recruiting_email", None)
    except:
        recruiting_email = None

    return recruiting_email, recr_email_reasoning


# -------------------------------------------------------------------
# Cover letter + Email drafting
# -------------------------------------------------------------------
def generate_pointers(firm_desc: str, resume: str, portfolio: str) -> str:
    """Generate bullet points to highlight in the final email/cover letter."""
    agent = Agent(sys_prompt=PROMPTS["generate_pointers"], model="gemini/gemini-2.0-flash")
    prompt = f"""
For the given architecture firm, and my resume and portfolio details, generate a detailed bullet-point list of all the key alignment areas that should be mentioned in a personalized email to the recruiter.

Firm Details:
{firm_desc}

Resume:
{resume}

Portfolio details:
{portfolio}
"""
    return agent.llm_call(prompt)


def write_email(email_pointers: str, resume: str) -> str:
    """Write the final email based on pointers and resume."""
    agent = Agent(sys_prompt=PROMPTS["write_email"], model="gemini/gemini-2.0-flash")
    prompt = f"""
Using the pointers provided and my resume as context, write a concise, personalized email to a recruiter at an architectural firm for an entry-level position.

Pointers:
{email_pointers}

Resume:
{resume}
"""
    return agent.llm_call(prompt)


def write_cover_letter(email_pointers: str, resume: str, job_description: str) -> str:
    """Write a cover letter based on pointers, resume, and job description."""
    agent = Agent(sys_prompt=PROMPTS["write_cover_letter"], model="gemini/gemini-2.0-flash")
    prompt = f"""
Using the job description, personalized pointers provided, and my resume as context, write the perfect cover letter for a candidate applying to an architectural firm. 
If no job description is provided, just write a generic cover letter highlighting my education, professional/technical background, and alignment with the firm for future opportunities.

Job Description:
{job_description}

Pointers:
{email_pointers}

Resume:
{resume}
"""
    return agent.llm_call(prompt)


# -------------------------------------------------------------------
# Streamlit App
# -------------------------------------------------------------------
def main():
    st.title("Architecture Firm Outreach App")
    st.write("Generate a personalized recruiter email (and optionally a cover letter) for architecture firms.")

    with st.sidebar:
        st.header("Your Details")
        resume_text = st.text_area("Paste your Resume text here:", height=200)
        portfolio_text = st.text_area("Paste your Portfolio details here:", height=200)

        if st.button("Reset All"):
            for key in st.session_state.keys():
                del st.session_state[key]
            st.experimental_rerun()

    if "resume" not in st.session_state:
        st.session_state["resume"] = resume_text
    if "portfolio" not in st.session_state:
        st.session_state["portfolio"] = portfolio_text

    st.session_state["resume"] = resume_text
    st.session_state["portfolio"] = portfolio_text

    st.subheader("Firm Input")
    firm_name = st.text_input("Enter the firm's name here:")

    fetch_email = st.checkbox("Fetch Recruiting Email from the firm?", value=True)
    write_cover = st.checkbox("Write a Cover Letter?", value=False)
    job_description = ""
    if write_cover:
        job_description = st.text_area("Paste the Job Description (Optional)", height=150)

    if st.button("Generate Output"):
        if not firm_name.strip():
            st.warning("Please enter a firm name.")
            return
        if not st.session_state["resume"].strip():
            st.warning("Please paste your Resume in the sidebar.")
            return

        # Initialize Google Sheets connection
        utils = gspread_utils.GSpreadUtils()
        utils.open_by_key(st.secrets["gspread"]["sheet_key"])
        worksheet_name = st.secrets["gspread"]["sheet_name"]
        records = utils.get_all_records(worksheet_name)

        # Fuzzy match checking
        def clean_name(name):
            name = name.lower()
            name = re.sub(r'[^\w\s]', '', name)
            return name.strip()

        cleaned_input = clean_name(firm_name)
        matched_record = None
        threshold = 80

        # Check for existing matches
        for record in records:
            cleaned_record = clean_name(record['Firm Name'])
            similarity = fuzz.ratio(cleaned_input, cleaned_record)
            if similarity >= threshold:
                matched_record = record
                st.info(f"Found cache match with {similarity}% similarity.")
                break

        if matched_record:
            # Use cached data
            firm_desc = matched_record['Firm Description']
            firm_desc_reasoning = "Retrieved from cache."
            
            if fetch_email:
                recruiting_email = matched_record['Firm Recruiter Email']
                recr_email_reasoning = "Retrieved from cache."
            else:
                recruiting_email = None
                recr_email_reasoning = "Email fetch disabled."
        else:
            # Call Perplexity API
            pplx_api_key = st.secrets["PERPLEXITY_API_KEY"]
            with st.spinner("Fetching data from Perplexity..."):
                if fetch_email:
                    with concurrent.futures.ThreadPoolExecutor() as executor:
                        f1 = executor.submit(get_firm_description, firm_name, pplx_api_key)
                        f2 = executor.submit(get_recruiting_email, firm_name, pplx_api_key)
                        firm_desc, firm_desc_reasoning = f1.result()
                        recruiting_email, recr_email_reasoning = f2.result()
                else:
                    firm_desc, firm_desc_reasoning = get_firm_description(firm_name, pplx_api_key)
                    recruiting_email = None
                    recr_email_reasoning = ""

            # Cache new data
            new_id = str(uuid4())
            row_data = [new_id, firm_name, firm_desc, recruiting_email or ""]
            utils.append_row(worksheet_name, row_data)
            st.success("New firm data cached successfully!")

        # Generate pointers
        with st.spinner("Generating alignment pointers..."):
            pointers = generate_pointers(
                firm_desc,
                st.session_state["resume"],
                st.session_state["portfolio"]
            )

        # Write email
        with st.spinner("Drafting your email..."):
            email_draft = write_email(pointers, st.session_state["resume"])

        # Write cover letter
        cover_letter = ""
        if write_cover:
            with st.spinner("Drafting your cover letter..."):
                cover_letter = write_cover_letter(
                    pointers,
                    st.session_state["resume"],
                    job_description
                )

        # Display results
        st.success("Done! See your results below:")
        st.write("---")

        st.header("Output Overview")
        st.subheader("Firm Description")
        st.write(firm_desc)

        if fetch_email:
            st.subheader("Recruiting Email")
            st.write(recruiting_email if recruiting_email else "No email found.")
            with st.expander("Show Email Extraction Reasoning"):
                st.write(recr_email_reasoning)

        st.subheader("Email to Recruiter")
        st.write(email_draft)

        if write_cover:
            st.subheader("Cover Letter")
            st.write(cover_letter)

        with st.expander("Show Firm Description Reasoning"):
            st.write(firm_desc_reasoning)

        # Download button
        output_text = [
            "# Firm Description\n" + firm_desc,
            "# Recruiting Email\n" + (recruiting_email if recruiting_email else "No email found."),
            "# Email Draft\n" + email_draft,
        ]
        if write_cover:
            output_text.append("# Cover Letter\n" + cover_letter)

        final_txt = "\n\n".join(output_text)
        st.download_button(
            label="Download All Results as .txt",
            data=final_txt,
            file_name=f"{firm_name.replace(' ', '_')}_output.txt",
            mime="text/plain"
        )


if __name__ == "__main__":
    main()