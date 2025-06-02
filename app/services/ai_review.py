from openai import OpenAI
import os

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY"),
)

def review_resume_ai(resume_text: str, job_desc: str = None):
    prompt = (
        "You are a resume reviewer. Analyze the following resume and return a JSON object with the following fields:\n"
        "\"score\": integer (score out of 100),\n"
        "\"suggestions\": list of 3 suggestions to improve the resume for a Software Engineering role,\n"
        "\"summary\": a brief summary of the resume's strengths and weaknesses.\n"
        "Format your response as valid JSON only.\n\n"
        f"Resume:\n{resume_text}"
    )
    if job_desc:
        prompt += (
            f"\n\nJob Description:\n{job_desc}\n"
            "Also include a field \"job_match_suggestions\": list of suggestions to better align the resume with the job description."
        )

    completion = client.chat.completions.create(
        extra_headers={
            # Optionally set these for openrouter.ai analytics/rankings
            # "HTTP-Referer": "<YOUR_SITE_URL>",
            # "X-Title": "<YOUR_SITE_NAME>",
        },
        extra_body={},
        model="deepseek/deepseek-r1-0528:free",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )
    return completion.choices[0].message.content