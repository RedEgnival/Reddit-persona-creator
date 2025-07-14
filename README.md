# Reddit User Persona Generator 🚀

*A sophisticated AI-powered tool that analyzes Reddit users and generates comprehensive behavioral personas.*

---

## 🛠 Technical Skills Demonstrated

- **API Integration**: Seamless Reddit API access via PRAW with OAuth 2.0
- **Natural Language Processing**: Persona generation powered by a local LLM (Ollama with Phi-3)
- **Data Handling**: Scrapes and analyzes 100+ user comments and posts
- **Robust Python Architecture**: Modular OOP design with built-in error handling
- **CI/CD Ready**: GitHub workflow-compatible with secure secret management
- **Clean Documentation**: Professional persona output in TXT and Markdown formats

---

## ✨ Key Features

- **Privacy-First**: Runs entirely offline with no external API calls after setup
- **Flexible Analysis**: Configurable post/comment limits (5 to 100+)
- **Evidence-Based**: Each persona trait includes citation to source content
- **Multiple Output Formats**: Plain text and GitHub-friendly Markdown personas

---
## 📄 Sample Output

**Reddit Username**: [u/kojied](https://www.reddit.com/user/kojied/)  
**Profile Summary**: A culturally aware, socially engaged New Yorker with strong views on immigration, fairness, and intergenerational dynamics.

---

### 🧠 Persona Summary

- **Age Estimate**: Early to mid-30s (based on references to nightlife, life experience, and tone)  
- **Occupation**: Possibly unemployed or involved in entertainment (mentions nightlife and casual routines)  
- **Relationship Status**: Single  
- **Location**: New York City, United States  
- **Reddit Archetype**: *The Observer*, with occasional tendencies toward *The Debater* (especially in controversial discussions)

---

### 🎯 Motivations

- Desire for authentic human connection through open dialogue  
- Engagement with social justice issues, particularly those affecting immigrant populations (e.g., H1B visa holders)  
- Pride in NYC’s cultural complexity and long-standing community spirit

---

### 🧍 Behavior & Habits

- Regularly contributes to Reddit threads discussing identity, fairness, and generational gaps  
- Shows consistent empathy and a thoughtful communication style  
- Engages respectfully, even when tackling emotionally charged topics (e.g., food insecurity, displacement, immigration)

---

### 📌 Goals & Needs

- Seeks deeper understanding of urban diversity and the immigrant experience  
- Aims to build cross-cultural awareness and mutual respect  
- Advocates for fairness and equity, particularly within NYC’s evolving population

---

### ⚠️ Frustrations

- Expresses discontent with younger users who ignore cultural and generational nuances  
- Concerned with stereotyping and ignorance around intern culture and age-based assumptions  
- Frustrated by censorship (e.g., TikTok bans) and inconsistent systems (e.g., sports refereeing)

---

### 🔍 Supporting Citations

- **Archetype Identification**  
  Derived from patterns in multiple long-form comments across subreddits such as r/newyorkcity and r/nba

- **Empathy & Cultural Commentary**  
  Source: [/r/newyorkcity/comments/1lykkqf/i_feel_violated_by_intern_season/](https://www.reddit.com/r/newyorkcity/comments/1lykkqf/i_feel_violated_by_intern_season/)  
  Excerpt: *"There's this bar that I frequent a few blocks away from my house... It’s not about the noise, it’s about respect..."*

- **Frustration Over Stereotypes**  
  Source: Same as above  
  Excerpt: *"Interns just don’t get it. There’s a history here, and it’s being ignored..."*

- **Advocacy for Immigrant Issues**  
  Source: Comments referencing H1B holders and immigrant community struggles  
  Threads: Multiple across r/immigration, r/newyorkcity, r/politics

## 🚀 Setup (Under 2 Minutes)

```bash
# Clone the repository and install dependencies
git clone https://github.com/RedEgnival/Reddit-persona-creator.git
cd Reddit-persona-creator
pip install -r requirements.txt

# Download the local AI model for persona generation
ollama pull phi3
