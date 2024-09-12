import requests
from operator import itemgetter
from datetime import datetime
import os
from dotenv import load_dotenv
import subprocess

load_dotenv()

username = os.getenv("GITHUB_USERNAME")
token = os.getenv("GITHUB_TOKEN")

url = f"https://api.github.com/users/{username}/repos"

all_repos = []
page = 1
per_page = 30

language_colors = {
    "HTML": "🔴",
    "JavaScript": "🟡",
    "Python": "🔵",
    "TypeScript": "🔵",
    "PHP": "🟣"
}

while True:
    response = requests.get(
        f"{url}?page={page}&per_page={per_page}", auth=(username, token)
    )

    if response.status_code == 200:
        repos = response.json()
        if repos:
            all_repos.extend(repos)
            page += 1
        else:
            break

    else:
        print(f"Failed to fetch repositories: {response.status_code}")
        break

sorted_repos = sorted(all_repos, key=itemgetter('created_at'), reverse=True)

# Static README content you want to keep above your repo list
readme_content = """
# Hi, I'm Sean 👋

<table>
<tr>
<td>
I have a demonstrated proficiency in software development, with a proven track record of delivering high-quality solutions from ideation to deployment. My expertise includes developing and optimizing web applications, enhancing data pipelines, and implementing analytics to generate actionable insights. I possess a deep understanding of full-stack development, particularly in Python, JavaScript, React.js, and database management. My polished communication skills enable me to effectively articulate complex technical strategies.
</td>
</tr>
</table>

### Skills/Tools:

![My Skills](https://skillicons.dev/icons?i=js,react,express,mongodb,nodejs,nextjs,threejs,tailwind,python,django,flask,postgres,postman,vercel,git)

### [Skip to Contributions](#contributions)

### Repositories sorted by date created:

"""

repos_per_page = 30
total_pages = (len(sorted_repos) + repos_per_page - 1) // repos_per_page

for page_num in range(total_pages):
    readme_content += f"## Page {page_num + 1}\n\n"
    
    start_index = page_num * repos_per_page
    end_index = start_index + repos_per_page
    page_repos = sorted_repos[start_index:end_index]
    
    for index, repo in enumerate(page_repos):
        # Parse the UTC creation date
        utc_time = datetime.strptime(repo['created_at'], "%Y-%m-%dT%H:%M:%SZ")

        # Format the date in MM-DD-YYYY format
        formatted_date = utc_time.strftime("%m-%d-%Y")

        # Get the primary language and its color
        language = repo['language']
        language_color = language_colors.get(language, "")

        # Add the repository to the README content
        readme_content += f"### [{repo['name']}]({repo['html_url']})\n"
        readme_content += f"{language_color} {language} • Created on {formatted_date}\n\n"
        
        # Only add the line if it's not the last repository on the page
        if index < len(page_repos) - 1:
            readme_content += "---\n\n"

# Add an anchor tag at the end for "Skip to Contributions"
readme_content += "\n<a name='contributions'></a>\n"

# Write the generated content to the README.md file
with open("README.md", "w") as readme_file:
    readme_file.write(readme_content)

print("README.md updated with static content and paginated repositories.")

# Stage the changes, commit, and push to GitHub using subprocess
subprocess.run(["git", "add", "README.md"], check=True)
subprocess.run(["git", "commit", "-m", "updated sorted repos"], check=True)
subprocess.run(["git", "push"], check=True)

print("Changes committed and pushed to GitHub.")