import requests
from bs4 import BeautifulSoup
import os


def extract_text_from_wikipedia(url, output_file):
    try:
        # Send a GET request to the URL
        response = requests.get(url)
        response.raise_for_status()  # Check for request errors

        # Parse the HTML content using BeautifulSoup
        soup = BeautifulSoup(response.content, "html.parser")

        # Extract the main content text (usually within <p> tags for Wikipedia pages)
        content = soup.find(id="mw-content-text")
        paragraphs = content.find_all("p")

        # Concatenate all the paragraphs' text
        text = "\n\n".join(p.get_text() for p in paragraphs)

        # Write the extracted text to the output file with UTF-8 encoding
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(text)

        print(f"Text extracted and saved to {output_file}")
        print(f"First 100 characters: {text[:100]}")
        return True
    except Exception as e:
        print(f"Error extracting text: {str(e)}")
        return False


if __name__ == "__main__":
    # Get the path to the root of the project (one level above "src")
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    # Define the path to "data/processed" directory outside the "src" folder
    output_dir = os.path.join(base_dir, "data", "processed")

    # Ensure the directory exists
    os.makedirs(output_dir, exist_ok=True)

    # Define the output file path
    output_file = os.path.join(output_dir, "harry_potter_hebrew.txt")

    url = "https://he.wikipedia.org/wiki/%D7%94%D7%90%D7%A8%D7%99_%D7%A4%D7%95%D7%98%D7%A8_%D7%95%D7%90%D7%91%D7%9F_%D7%94%D7%97%D7%9B%D7%9E%D7%99%D7%9D"
    extract_text_from_wikipedia(url, output_file)
