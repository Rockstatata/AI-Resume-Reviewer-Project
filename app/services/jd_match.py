from openai import OpenAI
import os

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY"),
)

def match_resume_with_job_desc(resume_text: str, job_desc: str):
    prompt = (
        "You are an expert resume reviewer. Compare the following resume and job description.\n"
        "Respond ONLY with a valid JSON object, no explanations, no markdown, no code block, no extra text.\n"
        "The JSON must have these keys:\n"
        "  \"matching_keywords\": (list of keywords/skills present in both),\n"
        "  \"missing_keywords\": (list of important keywords from the job description missing in the resume),\n"
        "  \"suggestions\": (list of 3 suggestions to better align the resume with the job description).\n"
        "Example:\n"
        "{\n"
        "  \"matching_keywords\": [\"Python\", \"project management\"],\n"
        "  \"missing_keywords\": [\"AWS\", \"Docker\"],\n"
        "  \"suggestions\": [\n"
        "    \"Add AWS experience to your resume.\",\n"
        "    \"Highlight any Docker usage.\",\n"
        "    \"Emphasize relevant project management achievements.\"\n"
        "  ]\n"
        "}\n"
        "Now, here is the data:\n"
        f"Resume:\n{resume_text}\n\nJob Description:\n{job_desc}"
    )
    completion = client.chat.completions.create(
        model="deepseek/deepseek-r1-0528:free",
        messages=[{"role": "user", "content": prompt}]
    )
    return completion.choices[0].message.content