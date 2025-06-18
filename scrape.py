import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
import time

def scrape_course_content():
    """
    Scrape TDS course content
    """
    course_data = []
    
    # Add your course content URLs here
    course_urls = [
        "https://tds.s-anand.net/",  # Main course page
        # Add more specific course content URLs
    ]
    
    for url in course_urls:
        try:
            response = requests.get(url)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract course content
            content = {
                'url': url,
                'title': soup.find('title').text if soup.find('title') else '',
                'content': soup.get_text(),
                'headings': [h.text for h in soup.find_all(['h1', 'h2', 'h3'])],
                'scraped_date': datetime.now().isoformat()
            }
            
            course_data.append(content)
            time.sleep(1)  # Be respectful to the server
            
        except Exception as e:
            print(f"Error scraping {url}: {e}")
    
    return course_data

def scrape_discourse_posts():
    """
    Scrape Discourse forum posts (simplified version)
    """
    # Since forum-dl didn't work, we'll use a simpler approach
    # This is a basic implementation - you may need to adapt based on the actual forum structure
    
    forum_posts = []
    
    # Example forum URLs (you'll need to find the actual URLs)
    base_url = "https://discourse.onlinedegree.iitm.ac.in"
    
    # This is a simplified example - actual implementation would need
    # to handle pagination, authentication, etc.
    
    return forum_posts

def create_knowledge_base():
    """
    Create a comprehensive knowledge base
    """
    print("Scraping course content...")
    course_content = scrape_course_content()
    
    print("Scraping forum posts...")
    forum_posts = scrape_discourse_posts()
    
    knowledge_base = {
        'course_content': course_content,
        'forum_posts': forum_posts,
        'created_date': datetime.now().isoformat()
    }
    
    # Save to file
    with open('knowledge_base.json', 'w') as f:
        json.dump(knowledge_base, f, indent=2)
    
    print(f"Knowledge base created with {len(course_content)} course items and {len(forum_posts)} forum posts")
    return knowledge_base

if __name__ == "__main__":
    create_knowledge_base()
