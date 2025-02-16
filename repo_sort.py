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

# 1. Fetch all repositories, handling pagination.
while True:
    response = requests.get(
        f"{url}?page={page}&per_page={per_page}", 
        auth=(username, token)
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

# 2. Sort repositories by creation date (newest first).
sorted_repos = sorted(all_repos, key=itemgetter('created_at'), reverse=True)

# 3. Start building the readme content.
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

# 4. Calculate pagination details.
repos_per_page = 30
total_pages = (len(sorted_repos) + repos_per_page - 1) // repos_per_page

# 5. Build output for each page of repos.
for page_num in range(total_pages):
    # Create an anchor for this page.
    readme_content += f'\n<a name="page{page_num + 1}"></a>\n'

    # Build the pagination line on a single line in the same font.
    # - Current page in bold
    # - Other pages as links
    pagination_links = []
    for i in range(1, total_pages + 1):
        if i == (page_num + 1):
            pagination_links.append(f"**{i}**")  # current page in bold
        else:
            pagination_links.append(f"[{i}](#page{i})")  # link to other pages

    # Example output: Page 1 **1** [2](#page2) [3](#page3) [4](#page4)
    readme_content += f"**Page {page_num + 1}** " + " ".join(pagination_links) + "\n\n"

    # Gather the repos for this page:
    start_index = page_num * repos_per_page
    end_index = start_index + repos_per_page
    page_repos = sorted_repos[start_index:end_index]
    
    # 6. Add repository listings for this page.
    for index, repo in enumerate(page_repos):
        formatted_date = repo['created_at'][:10]
        year, month, day = formatted_date.split('-')
        formatted_date = f"{month}-{day}-{year}"

        language = repo['language']
        language_color = language_colors.get(language, "")

        # Handle fork info
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

        # Only add a separator if it's not the last repo on this page
        if index < len(page_repos) - 1:
            readme_content += "---\n\n"

# 7. Add the "Contributions" anchor and back-to-top link.
readme_content += "\n<a name='contributions'></a>\n"
readme_content += """
### [Back to Top](#top)
"""

# 8. Write out the README file.
with open("README.md", "w") as readme_file:
    readme_file.write(readme_content)

print("README.md updated with static content, paginated repositories, and single-line pagination links.")

# 9. Commit/push changes.
subprocess.run(["git", "add", "README.md"], check=True)
subprocess.run(["git", "commit", "-m", "updated sorted repos with single-line pagination"], check=True)
subprocess.run(["git", "push"], check=True)

print("Changes committed and pushed to GitHub.")