from PyPDF2 import PdfReader
from sklearn.feature_extraction.text import TfidfVectorizer
import requests
from bs4 import BeautifulSoup
import re
from time import sleep
from random import randint

# Define job roles and associated skills
job_roles = {
    "Software Engineer": ["python", "java", "c++", "javascript", "sql", "html", "css"],
    "Data Scientist": ["python", "r", "sql", "machine learning", "data analysis", "statistics"],
    "Web Developer": ["html", "css", "javascript", "react", "node.js", "sql"],
    "Product Manager": ["market research", "project management", "business analysis", "product design"],
    "UX/UI Designer": ["design thinking", "prototyping", "user research", "figma", "adobe xd"],
    "DevOps Engineer": ["docker", "kubernetes", "aws", "ci/cd", "linux", "python"],
    "Cybersecurity Analyst": ["network security", "penetration testing", "firewalls", "risk assessment"],
    "Cloud Engineer": ["aws", "azure", "gcp", "cloud architecture", "devops", "terraform"],
    "Digital Marketer": ["seo", "content marketing", "social media", "google analytics", "ppc"],
    "Business Analyst": ["data analysis", "business intelligence", "requirements gathering", "stakeholder management"]
}

# Certification links
certification_links = {
    "python": "https://www.coursera.org/specializations/python",
    "java": "https://www.coursera.org/specializations/java-programming",
    "c++": "https://www.udacity.com/course/c-plus-plus--ud258",
    "javascript": "https://www.freecodecamp.org/learn/javascript-algorithms-and-data-structures/",
    "sql": "https://www.codecademy.com/learn/learn-sql",
    "html": "https://www.freecodecamp.org/learn/responsive-web-design/#basic-html-and-html5",
    "css": "https://www.freecodecamp.org/learn/responsive-web-design/#basic-css",
    "r": "https://www.coursera.org/learn/data-analysis-r",
    "machine learning": "https://www.coursera.org/learn/machine-learning",
    "data analysis": "https://www.udacity.com/course/data-analyst-nanodegree--nd002",
    "statistics": "https://www.khanacademy.org/math/statistics-probability",
    "react": "https://www.udemy.com/course/react-the-complete-guide-incl-redux/",
    "node.js": "https://www.udemy.com/course/the-complete-nodejs-developer-course-2/",
    "project management": "https://www.coursera.org/learn/project-management",
    "business analysis": "https://www.udemy.com/course/business-analysis-fundamentals/",
    "design thinking": "https://www.coursera.org/learn/design-thinking",
    "prototyping": "https://www.udemy.com/course/prototyping-with-figma/",
    "user research": "https://www.coursera.org/learn/user-research",
    "figma": "https://www.udemy.com/course/figma-for-ux-ui-design/",
    "adobe xd": "https://www.udemy.com/course/adobe-xd-cc-for-ui-ux-design/",
    "docker": "https://www.udemy.com/course/docker-mastery/",
    "kubernetes": "https://www.udemy.com/course/kubernetes-for-developers/",
    "aws": "https://www.udemy.com/course/aws-certified-solutions-architect-associate/",
    "ci/cd": "https://www.coursera.org/learn/continuous-integration",
    "linux": "https://www.udemy.com/course/linux-for-beginners/",
    "network security": "https://www.coursera.org/learn/network-security",
    "penetration testing": "https://www.udemy.com/course/penetration-testing/",
    "firewalls": "https://www.udemy.com/course/network-security-firewalls/",
    "risk assessment": "https://www.coursera.org/learn/security-risk-management",
    "azure": "https://www.udemy.com/course/azure-certified-solutions-architect/",
    "gcp": "https://www.udemy.com/course/google-cloud-platform-gcp/",
    "cloud architecture": "https://www.udemy.com/course/cloud-architecture/",
    "terraform": "https://www.udemy.com/course/learn-terraform/",
    "seo": "https://www.coursera.org/learn/seo",
    "content marketing": "https://www.udemy.com/course/content-marketing-mastery/",
    "social media": "https://www.coursera.org/learn/social-media-marketing",
    "google analytics": "https://www.udacity.com/course/google-analytics--ud257",
    "ppc": "https://www.udemy.com/course/ppc-marketing/"
}

def analyze_resume(file_path):
    try:
        # Extract text from the PDF
        pdf_reader = PdfReader(file_path)
        text = ''
        for page in pdf_reader.pages:
            text += page.extract_text() or ''
        
        # Debug: Print extracted text (first 1000 characters)
        print("Extracted Text:\n", text[:1000])  

        # Initialize vectorizer
        vectorizer = TfidfVectorizer(lowercase=True, stop_words='english')

        # Combine job roles and skill sets into a single list for TF-IDF vectorization
        skill_set = [skill for skills in job_roles.values() for skill in skills]
        job_descriptions = list(job_roles.keys())

        # Add the resume text and job descriptions to the skill set for comparison
        all_texts = [text] + job_descriptions

        # Vectorize the texts
        X = vectorizer.fit_transform(all_texts)

        # Debug: Print the shapes of the vectors
        print("TF-IDF Matrix Shape:", X.shape)
        
        # Calculate scores for each job role
        scores = {}
        for i, job in enumerate(job_descriptions):
            job_vector = X[i + 1]  # Get the vector for the job description
            score = (X[0] @ job_vector.T).sum()  # Calculate the dot product as score
            scores[job] = score
        
        # Debug: Print scores
        print("Job Scores:\n", scores)

        # Find the best job match based on score
        recommended_job = max(scores, key=scores.get)
        
        # Normalize the score to be out of 100
        max_score = max(scores.values(), default=1)
        total_resume_score = (scores[recommended_job] / max_score) * 100

        # Prepare recommendations for certifications based on the recommended job
        job_skills = job_roles[recommended_job]
        certifications = {skill: certification_links.get(skill, "No certification available") for skill in job_skills}

        # Fetch job openings
        job_openings = fetch_job_openings(recommended_job)
        
        # Determine skill gaps
        resume_skills = {skill for skill in skill_set if skill in text}  # skills found in the resume text
        missing_skills = set(job_skills) - resume_skills
        recommended_skills = list(missing_skills)

        # Determine level based on score
        if total_resume_score < 40:
            level = "Beginner"
        elif 40 <= total_resume_score < 80:
            level = "Intermediate"
        else:
            level = "Advanced"

        return {
            'score': round(total_resume_score, 2),
            'recommended_job': recommended_job,
            'certification_links': certifications,
            'job_openings': job_openings,
            'recommended_skills': recommended_skills,
            'level': level
        }

    except Exception as e:
        return {'error': str(e)}

def fetch_job_openings(job_title):
    job_openings = []
    base_url = "https://www.naukri.com/"
    params = {"q": job_title, "l": "India"}

    try:
        for i in range(0, 2):  # Fetch 2 pages of results
            params["start"] = i * 10
            response = requests.get(base_url, params=params)
            soup = BeautifulSoup(response.content, "html.parser")

            # Debug: Print the page content (first 1000 characters)
            print("Page Content:\n", soup.prettify()[:1000])  

            for div in soup.find_all(name="div", attrs={"class": "jobTuple"}):
                job = {}
                job_title_elem = div.find("a", attrs={"class": "title"})
                company_elem = div.find("a", attrs={"class": "subTitle"})
                
                if job_title_elem:
                    job['title'] = job_title_elem.text.strip()
                    job['url'] = job_title_elem['href'] if job_title_elem else "No URL available"
                
                if company_elem:
                    job['company'] = company_elem.text.strip()
                
                if job:
                    job_openings.append(job)

            sleep(randint(1, 3))  # Avoid hitting the server too frequently

    except Exception as e:
        job_openings.append({'error': str(e)})
    
    return job_openings