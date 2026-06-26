import os
import sys
import json
import asyncio
import aiohttp
from dotenv import load_dotenv

# Ensure we're in the BACKEND directory for .env loading
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
load_dotenv()

# We need the NVIDIA API Key to run the LLM
api_key = os.environ.get("NVIDIA_API_KEY")
if not api_key:
    print("Error: NVIDIA_API_KEY not found in environment.")
    sys.exit(1)

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

# Limiting to a subset of skills initially for speed if needed, but let's try all.
# Actually, 10 skills * 3 difficulties = 30 calls. Each call generates 10 questions with 500-1000 words each.
# Generating 5,000 - 10,000 words per API call will likely hit max_tokens limits (usually 4096 or 8192).
# Let's break it down to 1 question per call, or 2 questions per call.
# Since we need 10 questions per difficulty, doing 10 separate calls per difficulty * 3 * 10 = 300 calls.
# Let's generate 5 questions per call to fit within max_tokens of 4096.
QUESTIONS_PER_BATCH = 2

async def generate_batch(session, skill, difficulty, batch_index):
    prompt = f"""
You are an expert technical interviewer. Generate exactly {QUESTIONS_PER_BATCH} highly detailed, real interview questions for the skill "{skill['name']}" at the "{difficulty}" difficulty level.

For each question, provide:
1. "question": The exact interview question.
2. "answer": A very long, comprehensive, and highly detailed technical explanation (between 400 to 800 words). Do not hold back on technical details, examples, and edge cases. Make it read like an in-depth tutorial.
3. "isHighlyAsked": A boolean (true or false). Set to true if this is a very common classic question.
4. "difficulty": Exactly "{difficulty}".
5. "id": A unique string like "{skill['id']}-{difficulty}-batch{batch_index}-idx"

Respond ONLY with a valid, raw JSON array of objects. Do not include markdown blocks like ```json or any other text.
Example format:
[
  {{
    "id": "{skill['id']}-{difficulty}-{batch_index}-1",
    "question": "...",
    "answer": "...",
    "difficulty": "{difficulty}",
    "isHighlyAsked": true
  }}
]
"""
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "meta/llama-3.1-70b-instruct",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.5,
        "max_tokens": 4000
    }
    
    url = "https://integrate.api.nvidia.com/v1/chat/completions"
    
    for attempt in range(3):
        try:
            async with session.post(url, json=payload, headers=headers) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    content = data["choices"][0]["message"]["content"].strip()
                    
                    if content.startswith("```json"):
                        content = content[7:-3]
                    elif content.startswith("```"):
                        content = content[3:-3]
                        
                    parsed_data = json.loads(content, strict=False)
                    return parsed_data
                elif resp.status == 429:
                    print(f"Rate limited on {skill['name']} {difficulty}. Waiting...")
                    await asyncio.sleep(10 * (attempt + 1))
                else:
                    text = await resp.text()
                    print(f"Error {resp.status}: {text}")
                    break
        except Exception as e:
            print(f"Exception for {skill['name']} {difficulty}: {e}")
            await asyncio.sleep(2)
            
    return []

async def process_skill(session, skill):
    skill_data = {
        "id": skill["id"],
        "name": skill["name"],
        "icon": "", 
        "questions": []
    }
    
    tasks = []
    # Generate 10 questions total = 5 batches of 2
    for difficulty in difficulties:
        for batch_index in range(1, (10 // QUESTIONS_PER_BATCH) + 1):
            tasks.append(generate_batch(session, skill, difficulty, batch_index))
            
    # Gather all questions for this skill
    results = await asyncio.gather(*tasks)
    
    # Flatten and assign IDs
    question_idx = 1
    for batch_res in results:
        for q in batch_res:
            # Re-index to ensure sequential IDs
            q['id'] = f"{skill['id']}-{q.get('difficulty', 'unknown')}-{question_idx}"
            skill_data["questions"].append(q)
            question_idx += 1
            
    print(f"Finished {skill['name']}: {len(skill_data['questions'])} questions generated.")
    return skill_data

async def main():
    print("Starting generation of long-form interview questions using NVIDIA NIM...")
    final_data = []
    
    # To avoid overwhelming the API, we will process 2 skills concurrently
    semaphore = asyncio.Semaphore(2)
    
    async def sem_process(session, skill):
        async with semaphore:
            return await process_skill(session, skill)
            
    async with aiohttp.ClientSession() as session:
        tasks = [sem_process(session, skill) for skill in skills]
        final_data = await asyncio.gather(*tasks)

    output_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "FRONTEND", "src", "components", "Interview", "realInterviewData.json"))
    
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(final_data, f, indent=2)
        
    print(f"\nSuccessfully generated {sum(len(s['questions']) for s in final_data)} long-form questions.")
    print(f"Saved to {output_path}")

if __name__ == "__main__":
    asyncio.run(main())
