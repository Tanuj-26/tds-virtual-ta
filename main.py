from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, List
import base64
import json
import time

app = FastAPI(title="TDS Virtual Teaching Assistant")

class QuestionRequest(BaseModel):
    question: str
    image: Optional[str] = None

class LinkResponse(BaseModel):
    url: str
    text: str

class AnswerResponse(BaseModel):
    answer: str
    links: List[LinkResponse]

@app.post("/api/", response_model=AnswerResponse)
async def answer_question(request: QuestionRequest):
    """
    Main endpoint to answer student questions
    """
    start_time = time.time()
    
    try:
        # Process the question
        answer = process_question(request.question, request.image)
        
        # Ensure response within 30 seconds
        if time.time() - start_time > 30:
            raise HTTPException(status_code=408, detail="Request timeout")
        
        return answer
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def load_knowledge_base():
    """Load scraped data from file"""
    try:
        with open('knowledge_base.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        # Return empty knowledge base if file doesn't exist
        return {"course_content": [], "forum_posts": []}

knowledge_base = load_knowledge_base()

def search_knowledge_base(question):
    """Search through knowledge base for relevant content"""
    relevant_content = []
    question_lower = question.lower()
    question_words = question_lower.split()
    
    # Search through course content
    for content in knowledge_base.get("course_content", []):
        content_text = content.get("content", "").lower()
        title_text = content.get("title", "").lower()
        
        # Simple keyword matching
        matches = sum(1 for word in question_words if word in content_text or word in title_text)
        
        if matches > 0:
            relevant_content.append({
                'type': 'course',
                'content': content,
                'relevance_score': matches
            })
    
    # Search through forum posts
    for post in knowledge_base.get("forum_posts", []):
        post_text = post.get("content", "").lower()
        post_title = post.get("title", "").lower()
        
        matches = sum(1 for word in question_words if word in post_text or word in post_title)
        
        if matches > 0:
            relevant_content.append({
                'type': 'forum',
                'content': post,
                'relevance_score': matches
            })
    
    # Sort by relevance and return top 5
    relevant_content.sort(key=lambda x: x['relevance_score'], reverse=True)
    return relevant_content[:5]

def process_question(question: str, image: Optional[str] = None):
    """
    Process the student question and generate intelligent response
    """
    # Handle base64 image if provided
    if image:
        try:
            image_data = base64.b64decode(image)
            # For now, just acknowledge the image
            # You could add OCR or image analysis here
        except Exception as e:
            print(f"Error processing image: {e}")
    
    # Search for relevant content
    relevant_content = search_knowledge_base(question)
    
    if not relevant_content:
        answer = "I couldn't find specific information about your question in the available course materials and forum discussions. Please try rephrasing your question or check the course materials directly."
        links = []
    else:
        # Generate answer based on relevant content
        answer_parts = ["Based on the course materials and forum discussions:\n"]
        links = []
        
        for item in relevant_content[:3]:  # Use top 3 most relevant items
            content = item['content']
            
            if item['type'] == 'course':
                answer_parts.append(f"• From course materials: {content.get('title', 'Course Content')}")
                if content.get('url'):
                    links.append(LinkResponse(
                        url=content['url'],
                        text=content.get('title', 'Course Material')[:100]
                    ))
            
            elif item['type'] == 'forum':
                answer_parts.append(f"• From forum discussion: {content.get('title', 'Forum Post')}")
                if content.get('url'):
                    links.append(LinkResponse(
                        url=content['url'],
                        text=content.get('title', 'Forum Discussion')[:100]
                    ))
        
        answer = "\n".join(answer_parts)
    
    return AnswerResponse(answer=answer, links=links)
