import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from google import genai
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

GEMINI_KEY = os.environ.get("GEMINI_API_KEY")
SENDER_EMAIL = os.environ.get("SENDER_EMAIL")
EMAIL_PASSWORD = os.environ.get("EMAIL_PASSWORD")
RECEIVER_EMAIL = os.environ.get("RECEIVER_EMAIL")


def get_sql_questions():
    """Ask Gemini for HTML formatted SQL questions."""
    
    client = genai.Client(api_key = GEMINI_KEY)
    prompt = """
        You are an expert SQL instructor. Generate 2 medium-hard SQL practice questions. 
        Format the entire response in clean, well-structured HTML so it looks professional in an email. Use inline CSS.
    
        1. Use an HTML table for the dataset schema.
        2. Use <h3> tags for the question titles.
        3. Include a small, subtle "Hint" section for each question.
        4. Do NOT provide the answers.
        5. Provide the full SQL setup script (CREATE TABLE and INSERT statements) inside a visually distinct <pre style="background-color: #f8f9fa; padding: 15px; border-radius: 5px; overflow-x: auto;"> block.
        6. Beneath each question, create a "Discuss with Gemini" section.
        7. CRITICAL: In this section, you MUST include a functional HTML hyperlink using exactly this format: <a href="https://gemini.google.com" target="_blank" style="color: #ffffff; background-color: #1a73e8; padding: 8px 15px; text-decoration: none; border-radius: 5px; display: inline-block; margin-bottom: 10px;">💬 Click here to open Gemini AI</a>
        8. Below the button, provide a pre-written prompt inside a <pre style="background-color: #e8f0fe; padding: 10px; border-left: 4px solid #1a73e8; white-space: pre-wrap;"> block. The prompt should include the schema context and the question, asking Gemini to act as a tutor to help find mistakes without giving the final answer.
    
        Return ONLY the raw HTML code. Do NOT wrap it in markdown formatting like ```html.
    """

    response = client.models.generate_content(
        model="gemini-3-flash-preview",
        contents=prompt
    )

    html_content = response.text.replace('```html', '').replace('```', '').strip()
    return html_content

def get_sql_questions_from_chatGPT():
    """Ask Gemini for HTML formatted SQL questions."""
    
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    prompt = """
        You are an expert SQL instructor.

        Generate 2 medium-hard SQL practice questions.

        Return clean HTML formatted for email.

        Requirements:

        1 Use an HTML table for schema
        2 Use <h3> for question title
        3 Include small Hint section
        4 Do NOT give answers
        5 Provide SQL setup script in a styled <pre> block
        6 Add a "Discuss with ChatGPT" section

        In this section include this button:

        <a href="https://chat.openai.com/?q=SQL%20question%20help" target="_blank"
        style="color:#ffffff;background:#10a37f;padding:8px 15px;text-decoration:none;border-radius:5px;">
        💬 Discuss with ChatGPT
        </a>

        Below the button include a <pre> block containing a prompt the user can copy that asks ChatGPT to help debug their SQL without revealing the answer.
        """

    response = client.responses.create(
        model="gpt-5-mini",
        input=prompt
    )

    return response.output_text


def send_email(html_content):
    """Sends the HTML content as an email."""
    msg = MIMEMultipart('alternative')
    msg['Subject'] = "Your Daily SQL Practice Questions 🚀"
    msg['From'] = SENDER_EMAIL
    msg['To'] = RECEIVER_EMAIL

    part = MIMEText(html_content, 'html')
    msg.attach(part)

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
        server.login(SENDER_EMAIL, EMAIL_PASSWORD)
        server.sendmail(SENDER_EMAIL, RECEIVER_EMAIL, msg.as_string())

    print("Email sent successfully!")

if __name__ == "__main__":
    try:
        # print("Fetching questions from Gemini...")
        # daily_questions_html = get_sql_questions()

        # print("Sending to Email...")
        # send_email(daily_questions_html)   

        daily_questions_html = get_sql_questions_from_chatGPT()

        with open("index.html", 'w') as file:
            file.write(daily_questions_html)
    except Exception as e:
        print(f"An error occurred: {e}")