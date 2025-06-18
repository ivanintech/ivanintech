# ivanintech/backend/app/services/gemini_service.py
import google.generativeai as genai
import httpx # To get the content of the URL if necessary
import json
import logging
from typing import Optional, Dict, Any, List, Tuple
from datetime import datetime, timezone
from bs4 import BeautifulSoup # To parse HTML if necessary
from pydantic import BaseModel
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from google.api_core.exceptions import ResourceExhausted

from app.core.config import settings

from app.services import youtube_service

logger = logging.getLogger(__name__)

# Configure the Gemini API Key when the module starts
if settings.GEMINI_API_KEY:
    genai.configure(api_key=settings.GEMINI_API_KEY)
else:
    logger.warning("GEMINI_API_KEY is not configured. Gemini service will not work.")

class ExtractedContent(BaseModel):
    text: Optional[str] = None
    og_title: Optional[str] = None
    og_description: Optional[str] = None
    og_image: Optional[str] = None
    og_type: Optional[str] = None
    # New field for the best image found by our logic
    best_image_url: Optional[str] = None

async def get_content_from_url(url: str) -> ExtractedContent:
    """
    Gets the main text content, OpenGraph metadata, and the best possible image URL
    from a URL, with specialized logic for common sites.
    """
    extracted = ExtractedContent()
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
        }
        async with httpx.AsyncClient(timeout=15.0, follow_redirects=True, verify=False) as client:
            response = await client.get(url, headers=headers)
            response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')

        # Extract OpenGraph Metadata
        extracted.og_title = soup.find("meta", property="og:title")["content"] if soup.find("meta", property="og:title") else None
        extracted.og_description = soup.find("meta", property="og:description")["content"] if soup.find("meta", property="og:description") else None
        extracted.og_image = soup.find("meta", property="og:image")["content"] if soup.find("meta", property="og:image") else None
        extracted.og_type = soup.find("meta", property="og:type")["content"] if soup.find("meta", property="og:type") else None
        
        # --- Improved Thumbnail Logic ---
        best_image_found = None
        # 1. Priority: og:image if it exists
        if extracted.og_image:
            best_image_found = extracted.og_image

        # 2. YouTube-specific logic
        elif "youtube.com" in url or "youtu.be" in url:
            video_id = None
            if "watch?v=" in url:
                video_id = url.split("watch?v=")[1].split("&")[0]
            elif "youtu.be/" in url:
                video_id = url.split("youtu.be/")[1].split("?")[0]
            
            if video_id:
                # We use the high-quality thumbnail for videos
                best_image_found = f"https://img.youtube.com/vi/{video_id}/hqdefault.jpg"
            else:
                # For channels, the og:image (already checked) is usually the avatar, which is sufficient.
                pass

        # 3. Amazon-specific logic (example for books)
        elif "amazon." in url:
            img_tag = soup.select_one("#img-canvas img, #landingImage, #ebooks-img-canvas img")
            if img_tag and img_tag.get('src'):
                best_image_found = img_tag.get('src')

        # 4. Generic logic: find the largest image (if nothing has been found yet)
        if not best_image_found:
            largest_image = None
            max_area = 0
            for img in soup.find_all('img'):
                try:
                    width = int(img.get('width', 0))
                    height = int(img.get('height', 0))
                    area = width * height
                    if area > max_area:
                        max_area = area
                        largest_image = img.get('src')
                except (ValueError, TypeError):
                    continue
            if largest_image:
                 best_image_found = largest_image

        extracted.best_image_url = best_image_found
        
        for script_or_style in soup(["script", "style", "header", "footer", "nav", "aside"]):
            script_or_style.decompose()
        
        main_content_tags = ['main', 'article', 'div[role="main"]', 'div[class*="content"]', 'div[id*="content"]']
        text_content = None
        for tag_selector in main_content_tags:
            try:
                element = soup.select_one(tag_selector)
                if element:
                    text_content = element.get_text(separator='\\n', strip=True)
                    break
            except Exception as e:
                logger.warning(f"Selector '{tag_selector}' failed for URL {url}: {e}")
                continue
        
        if not text_content:
            body = soup.find('body')
            if body:
                text_content = body.get_text(separator='\\n', strip=True)
        else:
                text_content = response.text
        
        max_length = 18000
        extracted.text = text_content[:max_length] if text_content else None
        logger.debug(f"Content extracted from {url}: OG Title: {extracted.og_title}, Best Image: {extracted.best_image_url}")
        return extracted

    except httpx.RequestError as e:
        logger.error(f"Network error while accessing URL {url}: {e}")
        return extracted
    except Exception as e:
        logger.error(f"Error extracting text/OG from URL {url}: {e}", exc_info=True)
        return extracted

@retry(
    retry=retry_if_exception_type(ResourceExhausted),
    wait=wait_exponential(multiplier=2, min=5, max=60),
    stop=stop_after_attempt(3)
)
async def generate_resource_details(
    url: str, 
    user_title: Optional[str] = None,
    user_personal_note: Optional[str] = None
) -> Optional[Dict[str, Any]]:
    if not settings.GEMINI_API_KEY:
        logger.error("Gemini service is not configured.")
        return None

    # 1. Try to get data from the YouTube API first
    yt_details = youtube_service.get_youtube_resource_details(url)
    
    # 2. If it is a YouTube resource, we process it in a special way
    if yt_details:
        logger.info(f"YouTube resource detected: '{yt_details.title}'. Skipping Gemini call for main details.")
        
        # We generate a default set of details without calling Gemini
        # to avoid quota issues. This is a quick fix.
        final_details = {
            "title": yt_details.title,
            "ai_generated_description": yt_details.description[:300], # Use the YouTube description
            "personal_note": user_personal_note or "A new resource added from YouTube.",
            "resource_type": yt_details.kind.capitalize(), # "Video" or "Channel"
            "tags": ["youtube", yt_details.kind],
            "thumbnail_url_suggestion": yt_details.thumbnail_url
        }
        logger.info(f"Final details generated for {url}: {final_details}")
        return final_details

    # --- The original flow is executed only if it is NOT a YouTube resource ---
    logger.info(f"URL is not from YouTube, proceeding with Gemini analysis.")

    # 3. Extract content from the web (as fallback or complement)
    extracted_data = await get_content_from_url(url)
    
    title_for_prompt = user_title or extracted_data.og_title
    description_for_prompt = extracted_data.og_description
    thumbnail_url_for_prompt = extracted_data.best_image_url
    
    text_for_prompt = extracted_data.text
    if not text_for_prompt:
        logger.warning(f"Could not extract text content from URL: {url}. Using description as fallback.")
        text_for_prompt = description_for_prompt or "Could not extract text content."

    model = genai.GenerativeModel("gemini-1.5-flash-latest")

    prompt_parts = [
        f"You are an expert technology and AI assistant for the ivanintech.com blog. Analyze the following web resource and generate details in JSON format.",
        f"Resource URL: {url}",
    ]
    if title_for_prompt:
        prompt_parts.append(f"Known title: {title_for_prompt}")
    
    prompt_parts.extend([
        "Text content (or description) extracted from the resource:\n---\n",
        text_for_prompt[:18000], # Limit just in case
        "\n---",
        "Considering all the information, generate the following:",
        f"1. `title`: Use or improve this title: '{title_for_prompt}'. It should be concise and engaging (max 15 words).",
        "2. `ai_generated_description`: A brief description (2-4 sentences in English).",
        "3. `personal_note`: A 'personal note' (1-2 sentences, in a friendly tone and in English).",
        "4. `resource_type`: A resource type (e.g., Video, Article, GitHub, Documentation, Tool, Course, Podcast, News).",
        "5. `tags`: A list of 2-5 relevant tags (lowercase strings, e.g., [\"python\", \"ai\"]).",
        f"6. `thumbnail_url_suggestion`: The preview image URL is **{thumbnail_url_for_prompt or 'not found'}**. Return this same URL in the JSON. If it's 'not found', return null.",
        "7. `is_related_to_tech`: A boolean (`true` or `false`). It must be `true` if the content is about software development, AI, or technology. `false` otherwise.",
        "Return ONLY a valid JSON object with these keys."
    ])

    if user_personal_note:
        prompt_parts.insert(len(prompt_parts) - 3, f"User's personal note (you can use it as inspiration): {user_personal_note}")
    
    complete_prompt = "\n".join(prompt_parts)
    logger.debug(f"Sending prompt to Gemini for URL {url}:\n{complete_prompt[:1000]}...")

    try:
        response = await model.generate_content_async(complete_prompt)
        cleaned_response_text = response.text.strip().removeprefix('```json').removesuffix('```').strip()
        
        details = json.loads(cleaned_response_text)
        
        is_related = details.get("is_related_to_tech", False)
        if not is_related:
            raise ValueError("The resource content does not seem to be related to AI or technology.")
        
        final_title = details.get("title")
        final_thumbnail = details.get("thumbnail_url_suggestion")

        final_details = {
            "title": final_title,
            "ai_generated_description": details.get("ai_generated_description"),
            "personal_note": details.get("personal_note"),
            "resource_type": details.get("resource_type"),
            "tags": details.get("tags"),
            "thumbnail_url_suggestion": final_thumbnail
        }
        
        logger.info(f"Final details generated for {url}: {final_details}")
        return final_details
    except json.JSONDecodeError as e:
        logger.error(f"Error decoding JSON from Gemini for {url}. Response: \n{response.text}\nError: {e}", exc_info=True)
        raise ValueError("The AI service returned a response with an invalid format.")
    except Exception as e:
        logger.error(f"Error calling Gemini API for {url}: {e}", exc_info=True)
        raise e

# This file will contain the logic to interact with the Gemini API. 