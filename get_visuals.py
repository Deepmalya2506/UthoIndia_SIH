import os
import requests
from ddgs.ddgs import DDGS
from PIL import Image

# The main media directory
MEDIA_DIR = "media"
# The specific subdirectory for downloaded images, as per your structure
VISUALS_DIR = os.path.join(MEDIA_DIR, "visuals")

def get_media_visuals(keywords, location, num_images=5):
    """
    Searches for and downloads relevant visuals into the 'media/visuals' directory.
    This function is designed to be called from your core.ipynb notebook.
    """
    # Create the visuals subdirectory if it doesn't exist
    if not os.path.exists(VISUALS_DIR):
        os.makedirs(VISUALS_DIR)

    # Clean up keywords and create a search query
    search_keywords = ' '.join(keywords) if isinstance(keywords, list) else keywords
    search_query = f"{search_keywords} {location}"
    print(f"🎥 Searching for visuals with query: '{search_query}'...")
    downloaded_images = []
    
    try:
        with DDGS() as ddgs:
            results = ddgs.images(
                search_query,
                region="in-en",
                safesearch="on",
                size="Large",
                type_image="photo"
            )
            
            if not results:
                print(f"🛑 No images found for '{search_query}'.")
                return []

            print(f"Downloading up to {num_images} images...")
            # Create a unique prefix for filenames based on the location
            location_prefix = location.split(',')[0].lower().replace(' ', '_')
            for i, r in enumerate(results):
                if i >= num_images:
                    break
                try:
                    image_url = r.get("image")
                    if not image_url:
                        continue
                    
                    image_data = requests.get(image_url, timeout=15).content
                    # Save the file with the location prefix for easy lookup later
                    filename = os.path.join(VISUALS_DIR, f"{location_prefix}_image_{i}.jpg")
                    with open(filename, 'wb') as f:
                        f.write(image_data)
                    Image.open(filename).verify()
                    downloaded_images.append(filename)
                except Exception as e:
                    print(f"  - Could not download or verify an image: {e}")
                    
        print(f"✅ Downloaded {len(downloaded_images)} valid images for {location}.")
        return downloaded_images
        
    except Exception as e:
        print(f"🛑 Error fetching visuals: {e}")
        return []

    