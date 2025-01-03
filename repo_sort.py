import requests
from operator import itemgetter
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
    "HTML": "🟠",
    "CSS": "🟣",
    "JavaScript": "🟡",
    "TypeScript": "🔵",
    "Python": "🔵",
    "PHP": "🟣",
    "C++": "🔴",
    "C#": "🟢",
    "C": "⚪️"
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

readme_content = """
<a name="top"></a>

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
        formatted_date = repo['created_at'][:10]
    
        year, month, day = formatted_date.split('-')
        formatted_date = f"{month}-{day}-{year}"

        language = repo['language']
        language_color = language_colors.get(language, "")

        if repo['fork']:

            if 'parent' not in repo:
                repo_details_url = repo['url']
                repo_details_response = requests.get(repo_details_url, auth=(username, token))
                
                if repo_details_response.status_code == 200:
                    repo_details = repo_details_response.json()
                    if 'parent' in repo_details:
                        parent = repo_details['parent']['full_name']
                        fork_info = f"🍴 Forked from [{parent}](https://github.com/{parent})"
                    else:
                        fork_info = "🍴 Forked from unknown"
                else:
                    print(f"Failed to fetch parent details: {repo_details_response.status_code}")
                    fork_info = "🍴 Forked from unknown"
            else:
                parent = repo['parent']['full_name']
                fork_info = f"🍴 Forked from [{parent}](https://github.com/{parent})"
        else:
            fork_info = ""

        readme_content += f"### [{repo['name']}]({repo['html_url']})\n"
        readme_content += f"{language_color} {language} • Created on {formatted_date}  \n{fork_info}\n\n"

        if index < len(page_repos) - 1:
            readme_content += "---\n\n"

readme_content += "\n<a name='contributions'></a>\n"

readme_content += """
### [Back to Top](#top)
"""

with open("README.md", "w") as readme_file:
    readme_file.write(readme_content)

print("README.md updated with static content and paginated repositories.")

subprocess.run(["git", "add", "README.md"], check=True)
subprocess.run(["git", "commit", "-m", "updated sorted repos"], check=True)
subprocess.run(["git", "push"], check=True)

print("Changes committed and pushed to GitHub.")