from fastapi import APIRouter
from typing import List, Any
import logging

from app.schemas.project import ProjectRead
from app.services import github_service
from app.services.github_service import extract_owner_repo_from_url, get_repo_root_contents

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/home/featured-projects", response_model=List[ProjectRead])
async def read_home_featured_projects() -> Any:
    """Retrieve top 2 pinned GitHub repositories for the Home page."""
    logger.info("[API Home] Reading top 2 pinned projects for homepage")
    
    github_username = "ivanintech"
    limit = 2

    pinned_repos_from_gh = await github_service.get_user_pinned_repositories_graphql(
        username=github_username, 
        limit=limit
    )

    home_featured_projects: List[ProjectRead] = []

    for repo in pinned_repos_from_gh:
        video_url_for_project = None
        # Try to find a GIF in the root for this pinned repo
        if repo.html_url:
            owner_repo_tuple = extract_owner_repo_from_url(str(repo.html_url))
            if owner_repo_tuple:
                owner, repo_name = owner_repo_tuple
                logger.info(f"[API Home] Searching for GIF in root of pinned repo: {owner}/{repo_name}")
                root_contents = await get_repo_root_contents(owner, repo_name)
                for item in root_contents:
                    if item.type == "file" and item.name.lower().endswith(".gif") and item.download_url:
                        video_url_for_project = str(item.download_url)
                        logger.info(f"[API Home] Found GIF for pinned repo {owner}/{repo_name}: {video_url_for_project}")
                        break
            else:
                logger.warning(f"[API Home] Could not extract owner/repo from GitHub URL for pinned repo: {repo.html_url}")
        
        project_data_for_response = {
            "id": str(repo.id), # Using GitHub's repo ID as a unique ID.
            "title": repo.name,
            "description": repo.description,
            "technologies": repo.topics + ([repo.language] if repo.language and repo.language not in repo.topics else []),
            "imageUrl": str(repo.owner.avatar_url) if repo.owner else None,
            "videoUrl": video_url_for_project,
            "githubUrl": str(repo.html_url),
            "liveUrl": repo.homepage,
            "is_featured": True
        }
        try:
            home_featured_projects.append(ProjectRead.model_validate(project_data_for_response))
        except Exception as e:
            logger.error(f"Error validating pinned repo {repo.name} for ProjectRead schema: {e}", exc_info=True)

    if not home_featured_projects:
        logger.info(f"[API Home] No pinned projects found or processed for {github_username}.")
        
    return home_featured_projects 