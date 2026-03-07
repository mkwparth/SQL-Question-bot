import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from google import genai
from dotenv import load_dotenv
from datetime import datetime 

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
        6. Beneath each question, create a "Discuss with AI" section.
        7. CRITICAL: In this section, create a dynamic link to ChatGPT that pre-fills the prompt. The URL must be formatted exactly as: https://chatgpt.com/?q=[YOUR_ENCODED_PROMPT]
        8. The prompt to encode should be exactly this context: "I am trying to solve this SQL problem: [Insert Question Here]. Here is my schema: [Insert Schema Here]. I am stuck. Can you act as my tutor and guide me toward the solution without just giving me the exact code?"
        9. URL-encode that entire prompt string (replace spaces with %20, etc.) and place it in the href of an anchor tag styled like a green ChatGPT button: <a href="https://chatgpt.com/?q=..." target="_blank" style="color: #ffffff; background-color: #10a37f; padding: 8px 15px; text-decoration: none; border-radius: 5px; display: inline-block; margin-top: 10px;">💬 Discuss with ChatGPT</a>
        
        Return ONLY the raw HTML code. Do NOT wrap it in markdown formatting like ```html.
    """

    response = client.models.generate_content(
        model="gemini-3-flash",
        contents=prompt
    )

    html_content = response.text.replace('```html', '').replace('```', '').strip()
    return html_content


def send_email(html_content):
    """Sends the HTML content as an email."""
    today_date = datetime.now().strftime("%b %d, %Y")

    msg = MIMEMultipart('alternative')
    msg['Subject'] = f"Daily SQL Practice 🚀 - {today_date}"
    msg['From'] = f"Your-SQL-AI-Mentor <{SENDER_EMAIL}>"
    msg['To'] = RECEIVER_EMAIL

    part = MIMEText(html_content, 'html')
    msg.attach(part)

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
        server.login(SENDER_EMAIL, EMAIL_PASSWORD)
        server.sendmail(SENDER_EMAIL, RECEIVER_EMAIL, msg.as_string())

    print("Email sent successfully!")

if __name__ == "__main__":
    try:
        print("Fetching questions from Gemini...")
        daily_questions_html = get_sql_questions()

        print("Sending to Email...")
        send_email(daily_questions_html)   

    except Exception as e:
        print(f"An error occurred: {e}")
