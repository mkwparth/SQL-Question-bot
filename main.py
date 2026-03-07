import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from google import genai
from dotenv import load_dotenv
from datetime import datetime 
import json

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
        Return the response strictly as a JSON object with the following structure. Do not include markdown formatting or extra text.
        
        {
          "daily_quote": "A short, inspiring motivational quote about coding.",
          "questions": [
            {
              "id": "1",
              "title": "Question Title",
              "context": "A short sentence explaining why this concept matters in real jobs.",
              "schema_html": "Raw HTML table representing the database schema",
              "setup_sql": "Raw SQL CREATE TABLE and INSERT statements",
              "hint": "A helpful hint",
              "chatgpt_url": "The full https://chatgpt.com/?q=... URL with the URL-encoded prompt",
              "solution_sql": "The raw SQL solution query"
            },
            {
              "id": "2",
              "title": "...",
              ...
            }
          ]
        }
    """

    response = client.models.generate_content(
        model="gemini-3-flash-preview", 
        contents=prompt,
        config=genai.types.GenerateContentConfig(
            response_mime_type="application/json",
        )
    )

    # Convert the JSON string into a Python dictionary
    return json.loads(response.text)


def send_email(html_content, sql_content):
    """Sends the HTML content as an email and attaches the SQL solution."""
    today_date = datetime.now().strftime("%b %d, %Y")

    # Changed from 'alternative' to 'mixed' to support file attachments
    msg = MIMEMultipart('mixed')
    msg['Subject'] = f"Daily SQL Practice 🚀 - {today_date}"
    msg['From'] = f"SkyReachSys SQL Mentor <{SENDER_EMAIL}>"
    msg['To'] = RECEIVER_EMAIL

    # 1. Attach the HTML email body
    part = MIMEText(html_content, 'html')
    msg.attach(part)

    # 2. Package the raw SQL text into a .sql file and attach it
    if sql_content:
        # Convert the string to bytes, which MIMEApplication requires
        sql_attachment = MIMEApplication(sql_content.encode('utf-8'))
        
        # Create a dynamic filename using today's date
        filename = f'solutions_{datetime.now().strftime("%Y%m%d")}.sql'
        sql_attachment.add_header('Content-Disposition', 'attachment', filename=filename)
        msg.attach(sql_attachment)

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
        server.login(SENDER_EMAIL, EMAIL_PASSWORD)
        server.sendmail(SENDER_EMAIL, RECEIVER_EMAIL, msg.as_string())

    print("Email sent successfully with .sql attachment!")


def build_html_email(data):
    """Injects the JSON data into your custom SkyReachSys HTML template."""
    
    # This is where your custom, permanent design lives
    html_template = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            /* YOUR CUSTOM BRANDING GOES HERE */
            body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f4f7f6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; background: #ffffff; padding: 20px; border-radius: 8px; }}
            .header {{ background-color: #2c3e50; color: #ffffff; padding: 15px; text-align: center; border-radius: 5px; }}
            .quote {{ font-style: italic; color: #7f8c8d; text-align: center; margin: 20px 0; }}
            .question-block {{ border-left: 4px solid #3498db; padding-left: 15px; margin-bottom: 30px; }}
            .code-block {{ background-color: #f8f9fa; padding: 15px; border-radius: 5px; overflow-x: auto; user-select: all; cursor: pointer; }}
            .chat-btn {{ background-color: #10a37f; color: white; padding: 10px 15px; text-decoration: none; border-radius: 5px; display: inline-block; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h2>SkyReachSys Daily SQL Challenge 🚀</h2>
            </div>
            
            <p class="quote">"{data['daily_quote']}"</p>
            <hr style="border: 0; border-top: 1px solid #eee; margin: 20px 0;">
    """

    # Loop through the questions in the JSON and add them to the template
    for q in data['questions']:
        html_template += f"""
            <div class="question-block">
                <h3>Question {q['id']}: {q['title']}</h3>
                <p><strong>Context:</strong> {q['context']}</p>
                
                <h4>Schema:</h4>
                {q['schema_html']}
                
                <h4>Setup Script:</h4>
                <p><i>💡 Click the code to auto-select, then copy.</i></p>
                <pre class="code-block">{q['setup_sql']}</pre>
                
                <details style="margin: 15px 0; padding: 10px; border: 1px solid #ddd; background: #fafafa; border-radius: 5px;">
                    <summary style="cursor: pointer; font-weight: bold; color: #3498db; outline: none;">💡 Click to reveal hint</summary>
                    <div style="margin-top: 10px;">{q['hint']}</div>
                </details>
                
                <a href="{q['chatgpt_url']}" target="_blank" class="chat-btn">💬 Discuss with ChatGPT</a>
            </div>
        """

    html_template += """
        </div>
    </body>
    </html>
    """
    
    return html_template

if __name__ == "__main__":
    try:
        print("Fetching questions from Gemini...")
        daily_questions_json = get_sql_questions()

        print("Building custom HTML template...")
        final_html = build_html_email(daily_questions_json)
        
        # Combine the raw solutions for the attachment
        solutions_text = f"-- Solution 1\n{daily_questions_json['questions'][0]['solution_sql']}\n\n-- Solution 2\n{daily_questions_json['questions'][1]['solution_sql']}"
        
        print("Sending to Email...")
        send_email(final_html, solutions_text)
        # print("Sending to Email...")
        # send_email(daily_questions_html)   

    except Exception as e:
        print(f"An error occurred: {e}")
