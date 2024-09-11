import os
import requests
from bs4 import BeautifulSoup


def scrape_page_text(url):
    try:
        # Send a GET request to the webpage
        response = requests.get(url)

        # Check if the request was successful
        if response.status_code != 200:
            print(f"Failed to retrieve the page. Status code: {response.status_code}")
            return None

        # Parse the page content with BeautifulSoup
        soup = BeautifulSoup(response.content, "html.parser")

        # Find the <main> tag with class "page__main"
        main_content = soup.find("main", {"class": "page__main"})

        if not main_content:
            print("Main content not found.")
            return None

        # Extract all paragraphs and headings within the main content
        text_elements = main_content.find_all(["p", "h1", "h2", "h3", "h4", "h5", "h6"])

        # Collect text from elements, ensuring paragraphs and headings are well separated
        text = "\n\n".join(
            [el.get_text(strip=True) for el in text_elements if el.get_text(strip=True)]
        )

        return text

    except Exception as e:
        print(f"Error occurred while scraping the page: {str(e)}")
        return None


def save_text_to_file(text, output_file):
    try:
        # Save the text to a file with UTF-8 encoding
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(text)
        print(f"Text successfully saved to {output_file}")
    except Exception as e:
        print(f"Error saving text to file: {str(e)}")


if __name__ == "__main__":
    # Define base directory and output paths
    base_dir = os.path.dirname(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    )
    input_dir = os.path.join(base_dir, "data", "raw")
    output_dir = os.path.join(base_dir, "data", "processed")

    # Ensure the output directory exists
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    print(f"Input directory: {input_dir}")
    print(f"Output directory: {output_dir}")

    # List of URLs for the 7 Harry Potter books
    urls = [
        "https://harrypotter.fandom.com/he/wiki/%D7%94%D7%90%D7%A8%D7%99_%D7%A4%D7%95%D7%98%D7%A8_%D7%95%D7%90%D7%91%D7%9F_%D7%94%D7%97%D7%9B%D7%9E%D7%99%D7%9D",
        "https://harrypotter.fandom.com/he/wiki/%D7%94%D7%90%D7%A8%D7%99_%D7%A4%D7%95%D7%98%D7%A8_%D7%95%D7%97%D7%93%D7%A8_%D7%94%D7%A1%D7%95%D7%93%D7%95%D7%AA",
        "https://harrypotter.fandom.com/he/wiki/%D7%94%D7%90%D7%A8%D7%99_%D7%A4%D7%95%D7%98%D7%A8_%D7%95%D7%94%D7%90%D7%A1%D7%99%D7%A8_%D7%9E%D7%90%D7%96%D7%A7%D7%91%D7%90%D7%9F",
        "https://harrypotter.fandom.com/he/wiki/%D7%94%D7%90%D7%A8%D7%99_%D7%A4%D7%95%D7%98%D7%A8_%D7%95%D7%92%D7%91%D7%99%D7%A2_%D7%94%D7%90%D7%A9",
        "https://harrypotter.fandom.com/he/wiki/%D7%94%D7%90%D7%A8%D7%99_%D7%A4%D7%95%D7%98%D7%A8_%D7%95%D7%9E%D7%A1%D7%93%D7%A8_%D7%A2%D7%95%D7%A3-%D7%94%D7%97%D7%95%D7%9C",
        "https://harrypotter.fandom.com/he/wiki/%D7%94%D7%90%D7%A8%D7%99_%D7%A4%D7%95%D7%98%D7%A8_%D7%95%D7%94%D7%A0%D7%A1%D7%99%D7%9A_%D7%97%D7%A6%D7%95%D7%99-%D7%94%D7%93%D7%9D",
        "https://harrypotter.fandom.com/he/wiki/%D7%94%D7%90%D7%A8%D7%99_%D7%A4%D7%95%D7%98%D7%A8_%D7%95%D7%90%D7%95%D7%A6%D7%A8%D7%95%D7%AA_%D7%94%D7%9E%D7%95%D7%95%D7%AA",
    ]

    # Loop through each URL and scrape the corresponding page
    for i, url in enumerate(urls, start=1):
        # Scrape the text from the webpage
        page_text = scrape_page_text(url)

        # Define the output file path for each book
        output_file = os.path.join(output_dir, f"harry_potter{i}.txt")

        if page_text:
            # Save the scraped text to the output directory
            save_text_to_file(page_text, output_file)
        else:
            print(f"Failed to retrieve text from the page for Harry Potter {i}.")
