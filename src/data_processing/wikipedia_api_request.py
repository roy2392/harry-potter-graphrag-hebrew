import wikipediaapi
import os

# Initialize the Wikipedia API for Hebrew with a valid user agent
user_agent = "harry-potter-rag/1.0 (roey.zalta@gmail.com)"
wiki_wiki = wikipediaapi.Wikipedia(language="he", user_agent=user_agent)


def extract_text_from_wikipedia(url, output_file):
    try:
        # Get the article
        article = wiki_wiki.page("הארי פוטר ואבן החכמים")

        # Process the article content
        title = article.title
        summary = article.summary

        # Predefined sections to look for
        characters = ["הארי פוטר", "רון ויזלי", "הרמיוני גריינג'ר", "לורד וולדמורט"]
        objects = ["אבן החכמים", "שרביט", "גלימת היעלמות"]
        locations = ["הוגוורטס", "סמטת דיאגון", "גרינגוטס"]
        events = ["גילוי הארי שהוא קוסם", "קרב עם וולדמורט"]
        institutions = ["הוגוורטס", "גרינגוטס"]

        # Prepare the structured data as text
        data = f"""
        title: "{title}"
        author: ג'יי קיי רולינג
        summary: {summary}
        characters: {', '.join(characters)}
        objects: {', '.join(objects)}
        locations: {', '.join(locations)}
        events: {', '.join(events)}
        institutions: {', '.join(institutions)}
        """

        # Write the structured data to a .txt file
        with open(output_file, "w", encoding="utf-8") as txtfile:
            txtfile.write(data)

        print("Structured TXT file created successfully.")
        return True
    except Exception as e:
        print(f"Error extracting text: {str(e)}")
        return False


if __name__ == "__main__":
    base_dir = os.path.dirname(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    )
    input_dir = os.path.join(base_dir, "data", "raw")
    output_dir = os.path.join(base_dir, "data", "processed")

    print(f"Input directory: {input_dir}")
    print(f"Output directory: {output_dir}")

    output_file = os.path.join(output_dir, "harry_potter.txt")
    extract_text_from_wikipedia("הארי פוטר ואבן החכמים", output_file)
