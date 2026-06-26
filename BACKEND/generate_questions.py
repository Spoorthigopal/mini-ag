import os
import sys
import json
import asyncio
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate

# Ensure we're in the BACKEND directory for .env loading
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
load_dotenv()

# We need the Google API Key to run the LLM
api_key = os.environ.get("GOOGLE_API_KEY")
if not api_key:
    print("Error: GOOGLE_API_KEY not found in environment.")
    sys.exit(1)

# Initialize the LLM (using the fast flash model for bulk generation)
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    google_api_key=api_key,
    temperature=0.7
)

prompt_template = PromptTemplate.from_template("""
You are an expert technical interviewer. Generate a list of {count} real, high-quality interview questions for the skill "{skill}" at the "{difficulty}" difficulty level.
These should be actual questions commonly asked in tech interviews (like those found on GeeksforGeeks, LeetCode, or standard industry interviews).

For each question, provide:
1. "question": The exact interview question.
2. "simpleAnswer": A brief, easy-to-understand explanation or answer (1-3 sentences).
3. "technicalAnswer": A deep, technical explanation that an experienced engineer would give (3-5 sentences, can include technical terms).
4. "isHighlyAsked": A boolean (true or false). Set to true if this is a very common classic question, false otherwise.
5. "difficulty": Exactly "{difficulty}".
6. "id": A unique string like "{skill}-{difficulty}-" followed by an index number.

Respond ONLY with a valid, raw JSON array of objects. Do not include markdown blocks like ```json or any other text.
Example format:
[
  {{
    "id": "{skill}-{difficulty}-1",
    "question": "...",
    "simpleAnswer": "...",
    "technicalAnswer": "...",
    "difficulty": "{difficulty}",
    "isHighlyAsked": true
  }}
]
""")

skills = [
    {"id": "javascript", "name": "JavaScript"},
    {"id": "python", "name": "Python"},
    {"id": "react", "name": "React"},
    {"id": "nodejs", "name": "Node.js"},
    {"id": "sql", "name": "SQL / Databases"},
    {"id": "dsa", "name": "Data Structures & Algorithms"},
    {"id": "system-design", "name": "System Design"},
    {"id": "git-devops", "name": "Git & DevOps"},
    {"id": "ml", "name": "Machine Learning Basics"},
    {"id": "os", "name": "Operating Systems"}
]

difficulties = ["easy", "moderate", "difficult"]
QUESTIONS_PER_DIFFICULTY = 10

async def generate_questions_for_skill_difficulty(skill, difficulty):
    print(f"Generating {QUESTIONS_PER_DIFFICULTY} {difficulty} questions for {skill['name']}...")
    prompt = prompt_template.format(
        count=QUESTIONS_PER_DIFFICULTY,
        skill=skill['id'],
        difficulty=difficulty
    )
    try:
        response = await llm.ainvoke(prompt)
        content = response.content.strip()
        if content.startswith("```json"):
            content = content[7:-3]
        elif content.startswith("```"):
            content = content[3:-3]
        
        parsed_data = json.loads(content)
        # Ensure correct indexing
        for idx, item in enumerate(parsed_data):
            item['id'] = f"{skill['id']}-{difficulty}-{idx + 1}"
            
        return parsed_data
    except Exception as e:
        print(f"Failed to generate/parse for {skill['name']} - {difficulty}: {e}")
        return []

async def main():
    final_data = []
    
    for skill in skills:
        skill_data = {
            "id": skill["id"],
            "name": skill["name"],
            "icon": "", # Will be added back in frontend map
            "questions": []
        }
        
        for difficulty in difficulties:
            questions = await generate_questions_for_skill_difficulty(skill, difficulty)
            skill_data["questions"].extend(questions)
            # Small delay to avoid rate limits
            await asyncio.sleep(2)
            
        final_data.append(skill_data)

    # Save to the frontend directory
    output_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "FRONTEND", "src", "components", "Interview", "realInterviewData.json"))
    
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(final_data, f, indent=2)
        
    print(f"\nSuccessfully generated {sum(len(s['questions']) for s in final_data)} questions.")
    print(f"Saved to {output_path}")

if __name__ == "__main__":
    asyncio.run(main())
