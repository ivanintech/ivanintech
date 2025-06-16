import httpx
from typing import List, Optional, Any
from pydantic import BaseModel, HttpUrl, Field, field_validator
import logging

from app.core.config import settings # For potential API key usage later

logger = logging.getLogger(__name__)

class GitHubRepo(BaseModel):
    name: str
    full_name: str
    description: Optional[str] = None
    html_url: HttpUrl
    topics: List[str] = Field(default_factory=list)
    language: Optional[str] = None
    stargazers_count: int = 0
    forks_count: int = 0
    default_branch: Optional[str] = None
    # Add other fields if needed, e.g., created_at, updated_at

    class Config:
        from_attributes = True # orm_mode in Pydantic v1

class GitHubFileContent(BaseModel):
    name: str
    path: str
    type: str  # "file" or "dir"
    download_url: Optional[HttpUrl] = None
    content: Optional[str] = None # Base64 encoded content if type is 'file' and fetched directly
    html_url: Optional[HttpUrl] = None
    
    @field_validator("content", mode="before")
    @classmethod
    def decode_content(cls, value: Optional[str]) -> Optional[str]:
        if value:
            try:
                import base64
                return base64.b64decode(value).decode('utf-8')
            except Exception as e:
                logger.error(f"Error decoding base64 content: {e}")
                return None # Or handle error as appropriate
        return value

async def get_user_repositories(username: str) -> List[GitHubRepo]:
    """Fetches public repositories for a given GitHub username."""
    if not username:
        return []

    api_url = f"https://api.github.com/users/{username}/repos"
    # Consider adding params for pagination, type, sort, direction if needed later
    # params = {"type": "owner", "sort": "updated", "per_page": 100}
    
    headers = {}
    # If you have a GitHub token for higher rate limits, add it here
    # if settings.GITHUB_TOKEN:
    #     headers["Authorization"] = f"token {settings.GITHUB_TOKEN}"

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(api_url, headers=headers) #, params=params)
            response.raise_for_status()  # Raise an exception for HTTP errors (4XX or 5XX)
            
            raw_repos = response.json()
            
            # Validate and parse each repo
            validated_repos: List[GitHubRepo] = []
            for repo_data in raw_repos:
                try:
                    # Map GitHub API fields to our Pydantic model fields if names differ significantly
                    # For now, assuming direct mapping or using Field aliases if set in GitHubRepo
                    repo = GitHubRepo.model_validate(repo_data)
                    validated_repos.append(repo)
                except Exception as e: # Catch Pydantic validation errors or others
                    logger.warning(f"Skipping repository {repo_data.get('full_name', '(unknown name)')} due to validation/parsing error: {e}")
            
            return validated_repos

    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP error fetching GitHub repositories for {username}: {e.response.status_code} - {e.response.text}")
        return []
    except httpx.RequestError as e:
        logger.error(f"Request error fetching GitHub repositories for {username}: {e}")
        return []
    except Exception as e:
        logger.error(f"Unexpected error fetching GitHub repositories for {username}: {e}", exc_info=True)
        return []

async def get_repo_root_contents(owner: str, repo_name: str, token: Optional[str] = None) -> List[GitHubFileContent]:
    """Fetches the contents of the root directory of a GitHub repository."""
    api_url = f"https://api.github.com/repos/{owner}/{repo_name}/contents/"
    headers = {}
    if token or settings.GITHUB_TOKEN:
        headers["Authorization"] = f"token {token or settings.GITHUB_TOKEN}"
    
    logger.debug(f"Fetching root contents for {owner}/{repo_name} from {api_url}")
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(api_url, headers=headers)
            response.raise_for_status()
            raw_contents = response.json()
            
            validated_contents: List[GitHubFileContent] = []
            if isinstance(raw_contents, list): # Root contents should be a list
                for item_data in raw_contents:
                    try:
                        content_item = GitHubFileContent.model_validate(item_data)
                        validated_contents.append(content_item)
                    except Exception as e:
                        logger.warning(f"Skipping item {item_data.get('name', '(unknown name)')} due to validation error: {e}")
            else:
                logger.warning(f"Unexpected format for root contents of {owner}/{repo_name}. Expected a list.")
            return validated_contents
    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP error fetching root contents for {owner}/{repo_name}: {e.response.status_code} - {e.response.text}")
        return []
    except httpx.RequestError as e:
        logger.error(f"Request error fetching root contents for {owner}/{repo_name}: {e}")
        return []
    except Exception as e:
        logger.error(f"Unexpected error fetching root contents for {owner}/{repo_name}: {e}", exc_info=True)
        return []

async def get_file_content(owner: str, repo_name: str, file_path: str, token: Optional[str] = None) -> Optional[GitHubFileContent]:
    """Fetches the content of a specific file in a GitHub repository."""
    api_url = f"https://api.github.com/repos/{owner}/{repo_name}/contents/{file_path.lstrip('/')}"
    headers = {"Accept": "application/vnd.github.v3+json"} # Ensure correct API version
    if token or settings.GITHUB_TOKEN:
        headers["Authorization"] = f"token {token or settings.GITHUB_TOKEN}"

    logger.debug(f"Fetching file content for {owner}/{repo_name}/{file_path} from {api_url}")
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(api_url, headers=headers)
            response.raise_for_status()
            file_data = response.json()
            
            # The GitHub API returns a single object for a file, not a list.
            # The content is base64 encoded.
            if isinstance(file_data, dict) and file_data.get("type") == "file":
                return GitHubFileContent.model_validate(file_data)
            else:
                logger.warning(f"Could not retrieve or validate file content for {file_path} in {owner}/{repo_name}. Data: {file_data}")
                return None
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            logger.info(f"File not found: {owner}/{repo_name}/{file_path}")
        else:
            logger.error(f"HTTP error fetching file content for {owner}/{repo_name}/{file_path}: {e.response.status_code} - {e.response.text}")
        return None
    except httpx.RequestError as e:
        logger.error(f"Request error fetching file content for {owner}/{repo_name}/{file_path}: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error fetching file content for {owner}/{repo_name}/{file_path}: {e}", exc_info=True)
        return None

# Utility function to extract owner and repo name from URL
def extract_owner_repo_from_url(github_url: str) -> Optional[tuple[str, str]]:
    """Extracts owner and repository name from a GitHub URL."""
    try:
        parsed_url = httpx.URL(github_url)
        path_parts = parsed_url.path.strip('/').split('/')
        if len(path_parts) >= 2:
            owner = path_parts[0]
            repo_name = path_parts[1]
            # Remove .git if present
            if repo_name.endswith('.git'):
                repo_name = repo_name[:-4]
            return owner, repo_name
    except Exception as e:
        logger.error(f"Error parsing GitHub URL {github_url}: {e}")
    return None

async def get_user_pinned_repositories_graphql(username: str, limit: int = 2, token: Optional[str] = None) -> List[GitHubRepo]:
    """Fetches a user's pinned repositories using GitHub GraphQL API and maps them to GitHubRepo objects."""
    if not username:
        return []

    actual_token = token or settings.GITHUB_TOKEN
    if not actual_token:
        logger.error("GITHUB_TOKEN is not configured. Cannot fetch pinned repositories via GraphQL.")
        return []

    graphql_query = {
        "query": """
            query($username: String!, $limit: Int!) {
              user(login: $username) {
                pinnedItems(first: $limit, types: REPOSITORY) {
                  nodes {
                    ... on Repository {
                      name
                      nameWithOwner # e.g., "owner/repo"
                      description
                      url # This is the html_url
                      owner {
                        login
                      }
                      stargazerCount # Renamed from stargazers_count
                      forksCount # Renamed from forks_count
                      languages(first: 3, orderBy: {field: SIZE, direction: DESC}) {
                        nodes {
                          name
                        }
                      }
                      defaultBranchRef { # To get the default branch name
                        name
                      }
                      # openGraphImageUrl # Could be useful for a static image if available
                    }
                  }
                }
              }
            }
        """,
        "variables": {"username": username, "limit": limit}
    }

    headers = {
        "Authorization": f"bearer {actual_token}",
        "Content-Type": "application/json"
    }
    
    api_url = "https://api.github.com/graphql"
    logger.info(f"Fetching {limit} pinned repositories for {username} via GraphQL from {api_url}")

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(api_url, json=graphql_query, headers=headers)
            response.raise_for_status()
            response_data = response.json()

            if "errors" in response_data:
                logger.error(f"GraphQL errors for {username}: {response_data['errors']}")
                return []

            pinned_items_nodes = response_data.get("data", {}).get("user", {}).get("pinnedItems", {}).get("nodes", [])
            
            validated_repos: List[GitHubRepo] = []
            for item_data in pinned_items_nodes:
                if not item_data:  # Skip if item_data is None (e.g. if a pinned item is not a repo)
                    continue
                try:
                    # Manual mapping from GraphQL fields to GitHubRepo fields
                    # owner_login, repo_name_only = item_data.get("nameWithOwner","").split('/') if "/" in item_data.get("nameWithOwner","") else (item_data.get("owner",{}).get("login"), item_data.get("name"))

                    repo_data_for_model = {
                        "name": item_data.get("name"),
                        "full_name": item_data.get("nameWithOwner"), # Matches GitHubRepo full_name
                        "description": item_data.get("description"),
                        "html_url": item_data.get("url"), # GraphQL 'url' is html_url
                        "topics": [], # GraphQL pinned items don't directly list topics in this simple query, would need another field or processing
                        "language": item_data.get("languages", {}).get("nodes", [{}])[0].get("name") if item_data.get("languages", {}).get("nodes") else None,
                        "stargazers_count": item_data.get("stargazerCount", 0),
                        "forks_count": item_data.get("forksCount", 0),
                        "default_branch": item_data.get("defaultBranchRef", {}).get("name") if item_data.get("defaultBranchRef") else None,
                    }
                    # Filter out None values before validation if model fields are not Optional but GraphQL might return null
                    repo_data_for_model = {k: v for k, v in repo_data_for_model.items() if v is not None or k in GitHubRepo.model_fields and GitHubRepo.model_fields[k].is_required() is False}


                    repo = GitHubRepo.model_validate(repo_data_for_model)
                    validated_repos.append(repo)
                except Exception as e:
                    logger.warning(f"Skipping pinned repository {item_data.get('nameWithOwner', '(unknown name)')} due to validation/parsing error: {e}", exc_info=True)
            
            return validated_repos

    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP error fetching pinned repositories for {username}: {e.response.status_code} - {e.response.text}")
        return []
    except httpx.RequestError as e:
        logger.error(f"Request error fetching pinned repositories for {username}: {e}")
        return []
    except Exception as e:
        logger.error(f"Unexpected error fetching pinned repositories for {username}: {e}", exc_info=True)
        return []

# Example usage (can be removed or used for testing)
# if __name__ == "__main__":
#     import asyncio
#     async def main():
#         # Replace 'octocat' with the desired GitHub username for testing
#         repos = await get_user_repositories("ivanintech") 
#         if repos:
#             for repo in repos:
#                 print(f"Name: {repo.name}, URL: {repo.html_url}, Desc: {repo.description}, Topics: {repo.topics}")
#         else:
#             print("No repositories found or error occurred.")
#     asyncio.run(main()) 