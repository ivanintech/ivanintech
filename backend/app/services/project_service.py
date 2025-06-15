import logging
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
import re # Import re for regex matching

from app.services import github_service
from app.services.github_service import (
    get_repo_root_contents, 
    get_file_content, 
    extract_owner_repo_from_url,
    GitHubFileContent # If used for type hinting here
)
from app.crud import crud_project # We will create/update this next
from app.schemas.project import ProjectCreate, ProjectUpdate, ProjectRead # Ensure ProjectRead is imported
from app.db.models.project import Project
from app.db.session import AsyncSessionLocal # Importar AsyncSessionLocal

logger = logging.getLogger(__name__)

async def sync_projects_from_github(github_username: str) -> None:
    """Fetches projects from GitHub and syncs them with the database.
    This function now creates its own database session."""
    logger.info(f"Starting GitHub project sync for user: {github_username}")
    
    async with AsyncSessionLocal() as db:
        github_repos = await github_service.get_user_repositories(github_username)
        
        synced_projects: List[ProjectRead] = []
        newly_added_count = 0
        already_exists_count = 0

        if not github_repos:
            logger.info(f"No repositories found on GitHub for user {github_username}.")
            return # No need to return projects, this is a background task

        for repo in github_repos:
            # Check for duplicates by title first
            existing_project_by_title = await crud_project.get_project_by_title(db=db, title=repo.name)
            if existing_project_by_title:
                logger.info(f"Project with title '{repo.name}' already exists. Skipping.")
                already_exists_count +=1
                continue

            existing_project_by_url = await crud_project.get_project_by_github_url(db=db, github_url=str(repo.html_url))
            if existing_project_by_url:
                logger.info(f"Project with GitHub URL '{repo.html_url}' already exists. Skipping.")
                already_exists_count +=1
                continue

            project_in_data = {
                "title": repo.name,
                "description": repo.description or "N/A", # Provide default if None
                "githubUrl": str(repo.html_url),
                "technologies": repo.topics + ([repo.language] if repo.language else []),
                "imageUrl": None, # Placeholder, can be fetched or set manually later
                "videoUrl": None, # Initialize videoUrl
                "is_featured": False # Default for new projects
            }
            
            # --- Try to find a GIF for videoUrl --- #
            if repo.html_url:
                owner_repo_tuple = extract_owner_repo_from_url(str(repo.html_url))
                if owner_repo_tuple:
                    owner, repo_name = owner_repo_tuple
                    logger.info(f"Searching for GIF in root of {owner}/{repo_name}")
                    root_contents = await get_repo_root_contents(owner, repo_name)
                    gif_file_url_in_root = None
                    for item in root_contents:
                        if item.type == "file" and item.name.lower().endswith(".gif") and item.download_url:
                            gif_file_url_in_root = str(item.download_url)
                            logger.info(f"Found GIF in root: {gif_file_url_in_root}")
                            break
                    if gif_file_url_in_root:
                        project_in_data["videoUrl"] = gif_file_url_in_root
                    #else:
                        # logger.info(f"No GIF found in root of {owner}/{repo_name}. Checking README.md")
                        # readme_filenames = ["README.md", "readme.md", "README.rst", "readme.rst"]
                        # found_gif_in_readme = False
                        # for readme_filename in readme_filenames:
                        #     readme_file_obj = await get_file_content(owner, repo_name, readme_filename)
                        #     if readme_file_obj and readme_file_obj.content:
                        #         logger.info(f"Found and processing {readme_filename} for {owner}/{repo_name}")
                        #         gif_urls_in_readme = re.findall(r"\!\[.*?\]\((.*?\.gif(?:\?raw=true)?)\)", readme_file_obj.content, re.IGNORECASE)
                            
                        #         if gif_urls_in_readme:
                        #             potential_gif_url = gif_urls_in_readme[0]
                        #             logger.info(f"Found potential GIF URL in README: {potential_gif_url} for {owner}/{repo_name}")
                                
                        #             if potential_gif_url.lower().startswith("http://") or potential_gif_url.lower().startswith("https://"):
                        #                 project_in_data["videoUrl"] = potential_gif_url
                        #                 found_gif_in_readme = True
                        #                 logger.info(f"Using absolute GIF URL from README: {potential_gif_url} for {owner}/{repo_name}")
                        #             elif potential_gif_url.startswith(".") or potential_gif_url.startswith("/"):
                        #                 branch = repo.default_branch if repo.default_branch else "main"
                        #                 logger.info(f"Repo default_branch for {owner}/{repo_name}: {repo.default_branch}, using branch: {branch}")
                        #                 clean_relative_path = potential_gif_url.lstrip("./")
                        #                 logger.info(f"Cleaned relative path for {owner}/{repo_name}: {clean_relative_path}")
                        #                 full_gif_url = f"https://raw.githubusercontent.com/{owner}/{repo_name}/{branch}/{clean_relative_path.lstrip('/')}"
                        #                 project_in_data["videoUrl"] = full_gif_url
                        #                 found_gif_in_readme = True
                        #                 logger.info(f"Constructed GIF URL from relative path in README: {full_gif_url} for {owner}/{repo_name}")
                        #             else:
                        #                 branch = repo.default_branch if repo.default_branch else "main"
                        #                 logger.info(f"Repo default_branch for {owner}/{repo_name} (assumed root relative): {repo.default_branch}, using branch: {branch}")
                        #                 full_gif_url = f"https://raw.githubusercontent.com/{owner}/{repo_name}/{branch}/{potential_gif_url.lstrip('/')}"
                        #                 project_in_data["videoUrl"] = full_gif_url
                        #                 found_gif_in_readme = True
                        #                 logger.info(f"Constructed GIF URL from (assumed root) relative path in README: {full_gif_url} for {owner}/{repo_name}")
                        #             break 
                        # if not found_gif_in_readme:
                        #     logger.info(f"No GIF link found in any README for {owner}/{repo_name}.")
                else:
                    logger.warning(f"Could not extract owner/repo from GitHub URL: {repo.html_url}")
            # --- End GIF Search --- #
            
            try:
                project_create_schema = ProjectCreate(**project_in_data)
                new_project = await crud_project.create_project(db=db, project_in=project_create_schema)
                synced_projects.append(ProjectRead.model_validate(new_project))
                newly_added_count += 1
            except Exception as e: # Catch Pydantic validation or DB errors
                logger.error(f"Error creating project for repo {repo.name}: {e}", exc_info=True)
                # Decide if you want to skip this repo or handle error differently
                
        logger.info(f"GitHub project sync completed for {github_username}. Added: {newly_added_count}, Already Existed: {already_exists_count}")
        # The function now returns None, as it's a fire-and-forget background task.
        # No need to re-fetch and return projects.

async def toggle_project_featured_status(db: AsyncSession, project_id: str) -> Optional[ProjectRead]:
    """Toggles the is_featured status of a project."""
    db_project = await crud_project.get_project(db=db, project_id=project_id) # Assumes get_project exists
    if not db_project:
        return None
    
    updated_data = ProjectUpdate(is_featured=not db_project.is_featured)
    
    # We need an update method in crud_project that can handle partial updates
    # or we update the instance directly and commit.
    # For simplicity, let's assume a direct update for now, 
    # but a CRUD update function is cleaner.
    try:
        # This is a simplified direct update. A CRUD function is better.
        db_project.is_featured = not db_project.is_featured
        await db.commit()
        await db.refresh(db_project)
        logger.info(f"Toggled is_featured for project ID {project_id} to {db_project.is_featured}")
        return ProjectRead.model_validate(db_project)
    except Exception as e:
        await db.rollback()
        logger.error(f"Error toggling featured status for project ID {project_id}: {e}", exc_info=True)
        return None 