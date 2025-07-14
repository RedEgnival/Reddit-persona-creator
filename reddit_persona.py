import praw
import ollama  
import os
import re
import time
import requests
from requests.exceptions import RequestException
from datetime import datetime
import configparser
from collections import defaultdict
from pathlib import Path

class RedditPersonaGenerator:
    def __init__(self):
        # Load configuration
        self.ollama_host = self.start_ollama()
        self.client = ollama.Client(host=self.ollama_host)
        self.config = configparser.ConfigParser()
        self.config.read('config.ini')
        
        # Initialize Reddit API
        self.reddit = praw.Reddit(
            client_id=self.config['REDDIT']['client_id'],
            client_secret=self.config['REDDIT']['client_secret'],
            user_agent=self.config['REDDIT']['user_agent']
        )
        
        # Persona template
        self.persona_template = """# {username}

**AGE OCCUPATION STATUS LOCATION REDDIT_ARCHETYPE**

{age} {occupation} {status} {location} {archetype}

---

## {top_traits}

### {secondary_traits}

---

## MOTIVATIONS

- {motivations}

---

## BEHAVIOR & HABITS

{habits}

---

## GOALS & NEEDS

{goals}

---

## FRUSTRATIONS

{frustrations}

---

"{quote}"

---

## CITATIONS

{citations}
"""

    def clean_username(self, url):
        #Extract username from URL
        pattern = r'https?://www\.reddit\.com/user/([^/]+)/?'
        match = re.search(pattern, url)
        if not match:
            raise ValueError("Invalid Reddit profile URL")
        return match.group(1)

    def get_user_data(self, username):
        #Fetch user data from Reddit
        user = self.reddit.redditor(username)
        
        try:
            account_age = (datetime.now() - datetime.fromtimestamp(user.created_utc)).days / 365
            account_age = round(account_age, 1)
            
            posts = list(user.submissions.new(limit=15))
            comments = list(user.comments.new(limit=15))
            
            return {
                'username': user.name,
                'account_age': account_age,
                'karma': user.link_karma + user.comment_karma,
                'verified': hasattr(user, 'has_verified_email') and user.has_verified_email,
                'posts': posts,
                'comments': comments,
                'trophies': [trophy.name for trophy in user.trophies()] if hasattr(user, 'trophies') else []
            }
        except Exception as e:
            raise Exception(f"Error fetching user data: {str(e)}")

    def analyze_content(self, content, username):
        #Use local LLM to analyze content
        print("\n[1/4] Starting analysis...")
        prompt = f"""Create a detailed user persona for Reddit user '{username}' based on their content.
        Follow this EXACT format:

        **Basic Information**
        Age: [estimate]
        Occupation: [inferred]
        Status: [Single/Married/Unknown]
        Location: [country/region]
        Reddit Archetype: [The Creator, The Critic, The Helper, The Observer, The Debater, The Enthusiast]

       ---

        ## [Primary Trait 1] [Primary Trait 2]

        ### [Secondary Trait 1] [Secondary Trait 2]

        ---

        ## MOTIVATIONS

        - [MOTIVATION 1]
        - [MOTIVATION 2]
        - [MOTIVATION 3]

        ---

        ## BEHAVIOR & HABITS

        - [Habit 1]
        - [Habit 2]
        - [Habit 3]

        ---

        ## GOALS & NEEDS

        - [Goal 1]
        - [Goal 2]
        - [Goal 3]

        ---

        ## FRUSTRATIONS

        - [Frustration 1]
        - [Frustration 2]
        - [Frustration 3]

        ---

        **Signature Quote**
        [representative quote]

        Content to analyze:
        {content}"""
        print("[2/4] Sending to LLM (usually takes 30-90 seconds)...")
        try:
            response = ollama.chat(
                model='phi3',
                messages=[{'role': 'user', 'content': prompt}],
                options={'temperature': 0.7, 'timeout': 120}
            )
            print("[3/4] Received LLM response!")
            return response['message']['content']
        except Exception as e:
            print(f"[4/4] ERROR: {str(e)}")
            print(f"Error in LLM analysis: {str(e)}")
            return None

    def parse_analysis(self, analysis_text):
        #Parse the LLM response
        sections = {
            'age': self.extract_value(analysis_text, "Age:"),
            'occupation': self.extract_value(analysis_text, "Occupation:"),
            'status': self.extract_value(analysis_text, "Status:"),
            'location': self.extract_value(analysis_text, "Location:"),
            'archetype': self.extract_value(analysis_text, "Reddit Archetype:"),
            'top_traits': self.extract_value(analysis_text, "Top Traits"),
            'secondary_traits': self.extract_value(analysis_text, "Secondary Traits"),
            'motivations': self.extract_section(analysis_text, "Motivations"),
            'habits': self.extract_section(analysis_text, "Behavior & Habits"),
            'goals': self.extract_section(analysis_text, "Goals & Needs"),
            'frustrations': self.extract_section(analysis_text, "Frustrations"),
            'quote': self.extract_value(analysis_text, "Signature Quote")
        }
        return sections

    def extract_value(self, text, key):
        #Extract a single value
        pattern = rf"{key}\s*(.*?)(?:\n|$)"
        match = re.search(pattern, text)
        return match.group(1).strip() if match else "Unknown"

    def extract_section(self, text, section_header):
        #Extract a multi-line section
        start = text.find(section_header)
        if start == -1:
            return "- Not available"
        
        end = text.find("\n\n", start)
        if end == -1:
            section = text[start:]
        else:
            section = text[start:end]
        
        return section.replace(section_header, "").strip()

    def generate_citations(self, analysis_sections, posts, comments):
        #Generate citations with sources
        citations = []
        all_content = [(p.title + " " + (p.selftext if hasattr(p, 'selftext') else ""), p.permalink) for p in posts] + \
                     [(c.body, f"https://reddit.com{c.permalink}") for c in comments]
        
        # Citation for archetype
        archetype = analysis_sections.get('archetype', 'Unknown')
        if archetype != 'Unknown':
            citations.append(f"- Archetype '{archetype}' determined based on overall posting patterns")
        
        # Citations for habits
        habits = analysis_sections.get('habits', '').split('\n')
        for habit in habits[:3]:
            if habit.strip() and not habit.strip().startswith('- Not available'):
                clean_habit = habit.replace('-', '').strip()
                best_match = self.find_best_match(clean_habit, all_content)
                if best_match:
                    citations.append(f"- Habit: {clean_habit}\n  Source: {best_match[1]}\n  Excerpt: '{best_match[0][:100]}...'")
        
        return '\n'.join(citations) if citations else "No specific citations available"

    def find_best_match(self, text, content_list):
        #Find best matching content
        best_match = None
        best_score = 0
        
        for content, link in content_list:
            score = len(set(text.lower().split()) & set(content.lower().split()))
            if score > best_score:
                best_score = score
                best_match = (content, link)
        
        return best_match

    def generate_persona(self, url):
        #Main function to generate persona
        try:
            username = self.clean_username(url)
            user_data = self.get_user_data(username)
            
            # Prepare content samples
            content_samples = []
            for post in user_data['posts'][:20]:
                content_samples.append(f"POST [{post.subreddit}]: {post.title}\n{post.selftext if hasattr(post, 'selftext') else ''}")
            
            for comment in user_data['comments'][:20]:
                content_samples.append(f"COMMENT [{comment.subreddit}]: {comment.body}")
            
            analysis_text = self.analyze_content("\n\n".join(content_samples), username)
            if not analysis_text:
                raise Exception("Failed to analyze user content")
            
            analysis_sections = self.parse_analysis(analysis_text)
            citations = self.generate_citations(analysis_sections, user_data['posts'], user_data['comments'])
            
            # Format the persona
            persona = self.persona_template.format(
                username=user_data['username'],
                age=analysis_sections['age'],
                occupation=analysis_sections['occupation'],
                status=analysis_sections['status'],
                location=analysis_sections['location'],
                archetype=analysis_sections['archetype'],
                top_traits=analysis_sections['top_traits'],
                secondary_traits=analysis_sections['secondary_traits'],
                motivations=analysis_sections['motivations'],
                habits=analysis_sections['habits'],
                goals=analysis_sections['goals'],
                frustrations=analysis_sections['frustrations'],
                quote=analysis_sections['quote'],
                citations=citations
            )
            
            # Save to file
            filename = f"persona_{user_data['username']}.txt"
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(persona)
            
            print(f"Persona generated and saved to {filename}")
            return persona
            
        except Exception as e:
            print(f"Error generating persona: {str(e)}")
            return None
        
        if persona:
            save_persona_file(persona, username)
            if not Path("personas/persona_EXAMPLE.txt").exists():
                update_readme_example(persona, username)
            return persona
    def start_ollama(self):
        """Handle Ollama server connection"""
        try:
            # Check if Ollama is already running
            if not self.check_ollama_running():
                print("Starting Ollama server...")
                os.system("start /B ollama serve > nul 2>&1")
                time.sleep(3)  # Wait for server to initialize
            return 'http://localhost:11434'
        except Exception as e:
            print(f"Ollama startup warning: {str(e)}")
            return 'http://localhost:11434'

    def check_ollama_running(self):
        #Check if Ollama is already running
        try:
            response = requests.get('http://localhost:11434/api/tags', timeout=2)
            return response.status_code == 200
        except:
            return False
    def save_persona_file(self, persona, username):
        #Save to personas/ directory
        os.makedirs("personas", exist_ok=True)
        filename = f"personas/{username}_persona.txt"
        
        with open(filename, "w", encoding="utf-8") as f:
            f.write(persona)
        print(f"Persona saved to {filename}")
        
        # Update README with first example
        if not os.path.exists("personas/EXAMPLE_persona.txt"):
            self.update_readme_example(persona, username)
            os.link(filename, "personas/EXAMPLE_persona.txt")
        
    def update_readme_example(self, persona, username):
        #Update README.md with formatted example"""
        readme_content = f"""# Reddit Persona Generator
        
    ## Example Output

    {persona}

    > Generated from analysis of u/{username}
    > Full personas available in the `personas/` directory"""
        
        with open("README.md", "w", encoding="utf-8") as f:
            f.write(readme_content)
    

if __name__ == "__main__":
    print("Reddit User Persona Generator (Local LLM Version)")
    print("------------------------------------------------")
    def start_ollama():
        """Handle Ollama server connection"""
        try:
            # Check if server responds
            try:
                response = ollama.Client().list()
                return 'http://localhost:11434'
            except:
                # Start the server if not running
                import os
                os.system("start /B ollama serve > nul 2>&1")
                import time; time.sleep(3)  # Wait for initialization
                return 'http://localhost:11434'
        except Exception as e:
            print(f"Ollama warning: {str(e)}")
            print("Please ensure Ollama is installed and run 'ollama serve' manually")
            return 'http://localhost:11434'

    
    # Initialize Ollama connection
    ollama_host = start_ollama()
    client = ollama.Client(host='http://localhost:11435')  
    
    while True:
        try:
            url = input("Enter Reddit profile URL (or 'quit' to exit): ").strip()
            if url.lower() == 'quit':
                break
                
            generator = RedditPersonaGenerator()
            persona = generator.generate_persona(url)
            
            if persona:
                print("\nGenerated Persona:")
                print("-----------------")
                print(persona)
                
        except Exception as e:
            print(f"Error: {str(e)}")
            print("Please try again with a valid Reddit profile URL\n")
    while True:
        try:
            url = input("Enter Reddit profile URL (or 'quit' to exit): ").strip()
            if url.lower() == 'quit':
                break
                
            generator = RedditPersonaGenerator()
            persona = generator.generate_persona(url)
            
            if persona:
                print("\nGenerated Persona:")
                print("-----------------")
                print(persona)
                
        except Exception as e:
            print(f"Error: {str(e)}")
            print("Please try again with a valid Reddit profile URL\n")