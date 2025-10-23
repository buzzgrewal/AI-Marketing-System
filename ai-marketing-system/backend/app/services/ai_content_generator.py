import httpx
import json
import os
import base64
from typing import Optional, Dict, Any
from datetime import datetime
from app.core.config import settings


class AIContentGenerator:
    """Service for generating marketing content using OpenRouter API"""

    def __init__(self):
        self.api_key = settings.OPENROUTER_API_KEY
        self.base_url = settings.OPENROUTER_BASE_URL
        self.text_model = settings.AI_MODEL_TEXT
        self.image_model = settings.AI_MODEL_IMAGE

    async def generate_social_post(
        self,
        topic: str,
        platform: str,
        tone: str = "professional",
        target_audience: str = "cyclists and triathletes",
        additional_context: Optional[str] = None
    ) -> Dict[str, str]:
        """Generate a social media post"""

        platform_guidelines = {
            "facebook": "Facebook post (max 400 chars recommended)",
            "instagram": "Instagram post (max 2200 chars, focus on visual storytelling)",
            "twitter": "Twitter/X post (max 280 chars)",
            "linkedin": "LinkedIn post (professional, max 3000 chars)"
        }

        prompt = f"""Generate an engaging social media post for {platform}.

Topic: {topic}
Target Audience: {target_audience}
Tone: {tone}
Platform Guidelines: {platform_guidelines.get(platform, 'General social media post')}
{f'Additional Context: {additional_context}' if additional_context else ''}

Generate:
1. A compelling caption/text for the post
2. 5-10 relevant hashtags (as a single string separated by spaces)
3. A brief title or hook

The business sells cycling, triathlon, and running products directly to consumers.
Focus on benefits, engagement, and call-to-action.

Return the response ONLY as valid JSON in this exact format (no markdown, no extra text):
{{
    "title": "catchy title or hook",
    "caption": "main post text",
    "hashtags": "#hashtag1 #hashtag2 #hashtag3"
}}

IMPORTANT: Return ONLY the JSON object, nothing else before or after it.
"""

        result = await self._call_openrouter(prompt, self.text_model)
        return self._parse_json_response(result)

    async def generate_email_content(
        self,
        subject_topic: str,
        purpose: str,
        tone: str = "professional",
        target_audience: str = "cyclists and triathletes",
        additional_context: Optional[str] = None
    ) -> Dict[str, str]:
        """Generate email marketing content"""

        prompt = f"""Generate a compelling marketing email.

Purpose: {purpose}
Subject Topic: {subject_topic}
Target Audience: {target_audience}
Tone: {tone}
{f'Additional Context: {additional_context}' if additional_context else ''}

The business sells cycling, triathlon, and running products directly to consumers.
Include a clear call-to-action and ensure compliance with email marketing best practices.

Return the response ONLY as valid JSON in this exact format (no markdown, no extra text):
{{
    "subject": "email subject line (max 60 chars)",
    "preview_text": "preview text (max 90 chars)",
    "body": "full email body in HTML format with proper structure",
    "call_to_action": "main CTA text"
}}

IMPORTANT: Return ONLY the JSON object, nothing else before or after it.
"""

        result = await self._call_openrouter(prompt, self.text_model)
        return self._parse_json_response(result)

    async def generate_ad_copy(
        self,
        product_name: str,
        product_description: str,
        platform: str = "facebook",
        tone: str = "enthusiastic",
        target_audience: str = "cyclists and triathletes"
    ) -> Dict[str, str]:
        """Generate ad copy for paid advertising"""

        prompt = f"""Generate compelling ad copy for {platform} advertising.

Product: {product_name}
Description: {product_description}
Target Audience: {target_audience}
Tone: {tone}

Platform: {platform} ({self._get_ad_specs(platform)})

Create attention-grabbing ad copy that highlights benefits and drives conversions.
Include a strong call-to-action.

Return the response ONLY as valid JSON in this exact format (no markdown, no extra text):
{{
    "headline": "main headline (max 40 chars)",
    "primary_text": "primary ad text",
    "description": "brief description (max 125 chars)",
    "call_to_action": "CTA button text"
}}

IMPORTANT: Return ONLY the JSON object, nothing else before or after it.
"""

        result = await self._call_openrouter(prompt, self.text_model)
        return self._parse_json_response(result)

    async def generate_image_prompt(
        self,
        content_topic: str,
        style: str = "professional product photography",
        additional_details: Optional[str] = None
    ) -> str:
        """Generate an optimized prompt for image generation"""

        prompt = f"""Create a detailed image generation prompt for AI image generators.

Topic: {content_topic}
Style: {style}
{f'Additional Details: {additional_details}' if additional_details else ''}

Context: This is for a cycling, triathlon, or running products company.

Generate a detailed, professional prompt that will produce a high-quality marketing image.
Include details about composition, lighting, colors, and mood.

Return only the image prompt text, nothing else.
"""

        result = await self._call_openrouter(prompt, self.text_model)
        return result.strip()

    async def generate_image(
        self,
        prompt: str,
        aspect_ratio: str = "1:1"
    ) -> str:
        """Generate an actual image using OpenRouter's image generation API

        Uses the chat completions endpoint with modalities parameter.
        Model: google/gemini-2.5-flash-image-preview
        Returns: URL path to saved image file
        """

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": settings.BACKEND_URL,
            "X-Title": settings.APP_NAME
        }

        payload = {
            "model": self.image_model,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "modalities": ["image", "text"],
            "image_config": {
                "aspect_ratio": aspect_ratio  # Options: 1:1, 3:4, 4:3, 16:9, 9:16, 21:9
            }
        }

        async with httpx.AsyncClient(timeout=120.0) as client:
            try:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers=headers,
                    json=payload
                )
                response.raise_for_status()
                result = response.json()

                print(f"Image generation response: {json.dumps(result, indent=2)}")

                # OpenRouter returns images in choices[0].message.images array
                if "choices" in result and len(result["choices"]) > 0:
                    message = result["choices"][0].get("message", {})
                    images = message.get("images", [])

                    if images and len(images) > 0:
                        image_data = images[0]

                        # Image is returned as base64 data URL: data:image/png;base64,xxxxx
                        if "image_url" in image_data:
                            data_url = image_data["image_url"]["url"]
                            return await self._save_data_url_image(data_url)

                raise Exception("No image data in API response")

            except httpx.HTTPError as e:
                print(f"Image generation API error: {str(e)}")
                if 'response' in locals():
                    print(f"Response status: {response.status_code}")
                    print(f"Response body: {response.text}")
                raise Exception(f"Image generation error: {str(e)}")
            except Exception as e:
                print(f"Unexpected error in image generation: {str(e)}")
                raise Exception(f"Image generation error: {str(e)}")

    async def enhance_product_image(
        self,
        product_image_base64: str,
        enhancement_prompt: str,
        aspect_ratio: str = "1:1"
    ) -> str:
        """Enhance or edit a product image using AI
        
        Takes a user's product image and enhances it based on the prompt.
        Can add backgrounds, improve lighting, add effects, etc.
        
        Args:
            product_image_base64: Base64 encoded product image (can include data URL prefix or raw base64)
            enhancement_prompt: Description of how to enhance/edit the image
            aspect_ratio: Desired aspect ratio for the output
            
        Returns:
            URL path to saved enhanced image file
        """
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": settings.BACKEND_URL,
            "X-Title": settings.APP_NAME
        }
        
        # Prepare the image data URL if it's raw base64
        if not product_image_base64.startswith("data:"):
            # Determine image format from base64 header (default to PNG)
            image_format = "png"
            if product_image_base64.startswith("/9j/"):
                image_format = "jpeg"
            elif product_image_base64.startswith("iVBORw0KGgo"):
                image_format = "png"
            
            product_image_base64 = f"data:image/{image_format};base64,{product_image_base64}"
        
        # Build the multimodal message with image + text
        payload = {
            "model": self.image_model,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": product_image_base64
                            }
                        },
                        {
                            "type": "text",
                            "text": enhancement_prompt
                        }
                    ]
                }
            ],
            "modalities": ["image", "text"],
            "image_config": {
                "aspect_ratio": aspect_ratio
            }
        }
        
        print(f"Enhancing product image with prompt: {enhancement_prompt[:100]}...")
        
        async with httpx.AsyncClient(timeout=120.0) as client:
            try:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers=headers,
                    json=payload
                )
                response.raise_for_status()
                result = response.json()
                
                print(f"Image enhancement response status: {response.status_code}")
                
                # OpenRouter returns images in choices[0].message.images array
                if "choices" in result and len(result["choices"]) > 0:
                    message = result["choices"][0].get("message", {})
                    images = message.get("images", [])
                    
                    if images and len(images) > 0:
                        image_data = images[0]
                        
                        # Image is returned as base64 data URL
                        if "image_url" in image_data:
                            data_url = image_data["image_url"]["url"]
                            return await self._save_data_url_image(data_url)
                
                raise Exception("No enhanced image data in API response")
                
            except httpx.HTTPError as e:
                print(f"Image enhancement API error: {str(e)}")
                if 'response' in locals():
                    print(f"Response status: {response.status_code}")
                    print(f"Response body: {response.text}")
                raise Exception(f"Image enhancement error: {str(e)}")
            except Exception as e:
                print(f"Unexpected error in image enhancement: {str(e)}")
                import traceback
                traceback.print_exc()
                raise Exception(f"Image enhancement error: {str(e)}")

    async def _download_and_save_image(self, image_url: str) -> str:
        """Download image from URL and save to uploads directory"""
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.get(image_url)
                response.raise_for_status()

                # Generate unique filename
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"generated_{timestamp}.png"
                filepath = os.path.join(settings.UPLOAD_DIR, filename)

                # Save image
                with open(filepath, "wb") as f:
                    f.write(response.content)

                # Return relative URL path
                return f"/uploads/{filename}"

        except Exception as e:
            print(f"Error downloading image: {str(e)}")
            raise Exception(f"Failed to download image: {str(e)}")

    async def _save_base64_image(self, base64_data: str) -> str:
        """Save base64 encoded image to uploads directory"""
        try:
            # Decode base64 data
            image_bytes = base64.b64decode(base64_data)

            # Generate unique filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"generated_{timestamp}.png"
            filepath = os.path.join(settings.UPLOAD_DIR, filename)

            # Save image
            with open(filepath, "wb") as f:
                f.write(image_bytes)

            # Return relative URL path
            return f"/uploads/{filename}"

        except Exception as e:
            print(f"Error saving base64 image: {str(e)}")
            raise Exception(f"Failed to save image: {str(e)}")

    async def _save_data_url_image(self, data_url: str) -> str:
        """Save base64 data URL image (format: data:image/png;base64,xxxxx) to uploads directory"""
        try:
            # Extract base64 data from data URL
            # Format: data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAA...
            if "base64," in data_url:
                base64_data = data_url.split("base64,")[1]
            else:
                raise Exception("Invalid data URL format - no base64 data found")

            # Decode base64 data
            image_bytes = base64.b64decode(base64_data)

            # Generate unique filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"generated_{timestamp}.png"
            filepath = os.path.join(settings.UPLOAD_DIR, filename)

            # Save image
            with open(filepath, "wb") as f:
                f.write(image_bytes)

            print(f"Image saved successfully to: {filepath}")

            # Return relative URL path
            return f"/uploads/{filename}"

        except Exception as e:
            print(f"Error saving data URL image: {str(e)}")
            raise Exception(f"Failed to save image: {str(e)}")

    async def improve_content(
        self,
        original_content: str,
        content_type: str,
        improvement_focus: str = "engagement"
    ) -> str:
        """Improve existing content"""

        prompt = f"""Improve the following {content_type} marketing content.

Original Content:
{original_content}

Improvement Focus: {improvement_focus}

Enhance the content while maintaining the core message. Make it more engaging, clear, and action-oriented.

Return only the improved content, nothing else.
"""

        result = await self._call_openrouter(prompt, self.text_model)
        return result.strip()

    async def _call_openrouter(
        self,
        prompt: str,
        model: str,
        max_tokens: int = 2000,
        temperature: float = 0.7
    ) -> str:
        """Make a call to OpenRouter API"""

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": settings.BACKEND_URL,
            "X-Title": settings.APP_NAME
        }

        payload = {
            "model": model,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "max_tokens": max_tokens,
            "temperature": temperature
        }

        print(f"Making OpenRouter API call to model: {model}")
        print(f"Prompt length: {len(prompt)} chars")

        async with httpx.AsyncClient(timeout=60.0) as client:
            try:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers=headers,
                    json=payload
                )
                response.raise_for_status()
                result = response.json()
                
                print(f"API Response status: {response.status_code}")
                print(f"API Response keys: {result.keys()}")
                
                if "choices" not in result or len(result["choices"]) == 0:
                    print(f"Full API response: {json.dumps(result, indent=2)}")
                    raise Exception("No choices in API response")
                
                content = result["choices"][0]["message"]["content"]
                
                if not content or content.strip() == "":
                    print(f"Full API response: {json.dumps(result, indent=2)}")
                    raise Exception("API returned empty content")
                
                print(f"Content received: {len(content)} chars")
                print(f"Content preview: {content[:200]}...")
                
                return content
            except httpx.HTTPError as e:
                print(f"OpenRouter API HTTP error: {str(e)}")
                print(f"Response status: {response.status_code if 'response' in locals() else 'N/A'}")
                print(f"Response body: {response.text if 'response' in locals() else 'N/A'}")
                raise Exception(f"OpenRouter API error: {str(e)}")
            except Exception as e:
                print(f"Unexpected error in OpenRouter call: {str(e)}")
                import traceback
                traceback.print_exc()
                raise Exception(f"OpenRouter API error: {str(e)}")

    def _parse_json_response(self, response: str) -> Dict[str, str]:
        """Parse JSON response from AI, handling potential markdown code blocks"""
        try:
            print(f"Parsing JSON response, length: {len(response)}")
            print(f"Response preview: {response[:300]}...")
            
            # Remove markdown code blocks if present
            if "```json" in response:
                response = response.split("```json")[1].split("```")[0]
            elif "```" in response:
                response = response.split("```")[1].split("```")[0]

            parsed = json.loads(response.strip())
            print(f"Successfully parsed JSON: {parsed.keys()}")
            return parsed
        except json.JSONDecodeError as e:
            print(f"JSON parsing failed: {str(e)}")
            print(f"Response that failed to parse: {response}")
            # If JSON parsing fails, return the raw response
            return {"content": response.strip()}

    def _get_ad_specs(self, platform: str) -> str:
        """Get platform-specific ad specifications"""
        specs = {
            "facebook": "Headline 40 chars, Primary text 125 chars",
            "instagram": "Primary text 125 chars, focus on visual",
            "google": "Headlines 30 chars each, Descriptions 90 chars each",
            "linkedin": "Headline 70 chars, Description 150 chars"
        }
        return specs.get(platform, "Standard ad format")


# Singleton instance
ai_content_generator = AIContentGenerator()
