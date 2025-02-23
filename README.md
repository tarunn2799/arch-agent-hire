# arch-agent

This tool helps generate personalized cold emails (and optionally cover letters) targeted at architecture firms. It leverages two main APIs:

- **Perplexity (pplx)** for firm research  
- **Gemini (Google’s API)** for text generation

With just your resume, portfolio information, and (optionally) a job description, the app drafts tailored outreach content to give you a professional edge in your applications. You can then download the generated email/cover letter as a `.txt` file.

---

## Table of Contents
1. [Project Description](#project-description)  
2. [How It Works](#how-it-works)  
3. [Requirements](#requirements)  
   - [Perplexity API Key](#perplexity-api-key)  
   - [Gemini API Key](#gemini-api-key)  
4. [Workflow Overview](#workflow-overview)  
5. [Usage Instructions](#usage-instructions)  
6. [Sample Files](#sample-files)  
7. [Notes](#notes)

---

## Project Description

This project is a **Streamlit application** designed for job seekers in the architectural field. It automatically gathers key information about a chosen architecture firm (e.g., firm description, recruiting email address) and generates:

- A **personalized recruiter email** showcasing your background and alignment.  
- An optional **cover letter**, specific to a provided job description if available—or a generic one if the job description is left blank.

---

## How It Works

1. **Input**: You paste your **resume** and **portfolio details** into the app’s sidebar, along with valid **Perplexity** and **Gemini** API keys.  
2. **Firm Name**: Specify the architecture firm you want to approach.  
3. **Data Fetching** (via Perplexity):  
   - **Firm Description**: The app queries Perplexity to gather a short summary of the firm.  
   - **Recruiting Email** (optional): The app queries Perplexity to find a publicly available contact email.  
4. **Pointers Generation** (via Gemini): Based on your resume, portfolio, and firm details, the app generates bullet-point highlights to mention in your outreach.  
5. **Email/Letter Drafting** (via Gemini):  
   - **Email**: A concise email is composed using the pointers, ready to be sent to the recruiter.  
   - **Cover Letter**: If selected, a cover letter is generated using the same context, plus an optional job description (for personalized references).  
6. **Download**: The final text (including firm description, contact info, email draft, and optional cover letter) can be downloaded as a `.txt` file.

---

## Requirements

### Perplexity API Key

The app requires a **Perplexity (pplx)** API key to fetch firm descriptions and recruiting emails.

1. **Obtain Free Access**: If you have a [University of Washington (UW) email](https://www.washington.edu/), you get $5/month in API credits plus premium features.  
2. **Login to Perplexity**: Go to [perplexity.ai](https://www.perplexity.ai/) and sign in with your UW email.  
3. **Generate/Copy API Key**:  
   - Click the gear icon (⚙️) in the bottom-left corner.  
   - Select **“API”** in the menu.  
   - **Generate** (for new users) or **Copy** (for existing users) your key.  
4. **Security**: Treat this key like a password—never expose it publicly.

### Gemini API Key

The app uses **Gemini** (Google’s API) to generate text for emails and cover letters.

1. **Visit Google AI Studio**: Sign in at [Google AI Studio](https://ai.google/) (or the relevant Gemini console).  
2. **Create API Key**: Click **“Get API key”** → **“Create API key.”**  
   - Create/select a project as needed.  
3. **Securely Store**: Copy the generated API key into your environment variables or app settings.  
4. **Free Tier**: 15 requests/min, 1,500 requests/day. If you exceed this usage, enable billing in the Google Cloud Console.

---

## Workflow Overview

Below is a high-level flow of the application:

1. **User Inputs**: Resume, Portfolio, Perplexity API key, Gemini API key.  
2. **Firm Name**: The user specifies which architecture firm they want to target.  
3. **Fetch & Cache Firm Data**:  
   - The app checks a Google Sheet cache (via `gspread_utils`) to see if the firm was previously researched.  
   - If found, it retrieves the cached description and email. Otherwise, it calls Perplexity to fetch new info and caches the result for future use.  
4. **Pointers Generation**: Gemini processes the firm description + user’s resume and portfolio to create bullet-point highlights.  
5. **Email/Letter Creation**:  
   - A tailored email is drafted with the pointers.  
   - If “Write a Cover Letter?” is checked, a job description can be optionally added for a more personalized letter. If the job description is left blank, a generic letter is generated.  
6. **Download**: The user can download all results as a `.txt` file.


---

## Sample Files

Inside the `sample` folder, you’ll find:
- **Sample Resumes**  
- **Sample Portfolios**  

Use these as references for the format/level of detail you can provide. Adjust them or replace them with your own data.

---

## Running this locally (ignore if you're not technical)

1. **Clone or Download** this repository.  
2. **Install Dependencies**:  
   ```bash
   pip install -r requirements.txt
   ```
3. **Set Up API Keys**:  
   - Have your Perplexity API key and Gemini API key ready.  
   - Store them securely (e.g., in your `secrets.toml` file or environment variables).  
4. **Run the App**:  
   ```bash
   streamlit run main.py
   ```
5. **Enter Your Details**: In the app’s sidebar, paste your **resume** text, **portfolio** highlights, and **API keys**.  
6. **Enter Firm Details**: Provide the architecture firm name.  
7. **(Optional) Check “Write a Cover Letter?”** and paste a **Job Description** if you want a highly targeted cover letter.  
8. **Generate**: Click **“Generate Output”** to fetch data, compose the email (and cover letter), then download the results as `.txt`.


## Notes

- If **Job Description** is provided, the cover letter will be **tailored** to that specific role.  
- If **Job Description** is **not** provided, the cover letter will be **generic**, highlighting your background and interest in future roles at the firm.  
- Ensure your **Perplexity** and **Gemini** API keys remain **private**.  
- Cached data in your Google Sheet will speed up subsequent queries for the same firms.

---

**Happy Writing!** Use this tool to streamline your architecture job outreach and make a great impression on potential employers.