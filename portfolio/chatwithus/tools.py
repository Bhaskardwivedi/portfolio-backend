from langchain.agents import Tool
from .agent import get_profile

def profile_tool():
    def _run(query: str) -> str:
        data = get_profile()
        query = query.lower()

        if "intro" in query:
            return data.get("intro", "No intro available")
        elif "skill" in query:
            return ", ".join(data.get("skills", []))
        elif "project" in query:
            return "\n".join([p["title"] for p in data.get("projects", [])])
        elif "service" in query:
            return "\n".join([s["title"] for s in data.get("services", [])])
        else:
            return f"Profile data:\nIntro: {data['intro']}\nSkills: {', '.join(data['skills'])}"
        
    return Tool(
        name = "ProfileFetcher",
        func=_run,
        description="Fetches Bhaskar's profile information such as intro, skills, projects, services."
    )    

if __name__ == "__main__":
    tool = profile_tool()
    print(tool.run("intro"))
    print(tool.run("skills"))
    print(tool.run("projects"))