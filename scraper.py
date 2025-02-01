from pathlib import Path
import inquirer
from bs4 import BeautifulSoup
from selenium import webdriver

def extract_songs_and_artists(content) -> tuple[list,list]:
    """Extract songs and artists from the anghami queue.

    Args:
        content (str): HTML body to extract classes from.

    Returns:
        list, list: Two lists for songs and artist respectively.
    """
    soup = BeautifulSoup(content, 'html.parser')
    class_lst = ["item-title-primary align-collection-item"]
    song_divs = soup.find_all("a", class_=class_lst)
    artist_divs = soup.find_all("div", {"class": "item-title-secondary"})
    songs = [div.find("span").text for div in song_divs]
    artists = [div.text for div in artist_divs]
    return songs, artists

def Scrape_Anghami():
    """Extract songs from anghami playlist
    1 - opens a new broswer window on Anghami.com
    2 - waits for user to authenticate and navigate to the required playlist.
    3 - Extracts all songs present in the queue (user needs to open the queue beforehand).
    4 - Present user with option to save songs in txt format or save page html
    5 - repeat 3 and 4 until user exits
    """
    # Set up the WebDriver
    # todo add support for chrome
    geckodriver_path = "/snap/bin/geckodriver"
    driver_service = webdriver.FirefoxService(executable_path=geckodriver_path)
    driver = webdriver.Firefox(service=driver_service)

    # Navigate to the webpage
    # Replace with your target URL
    driver.get('https://play.anghami.com/likes')
    input("Navigate to the playlist that you would like to extract then press enter.")

    while True:
        page_html = driver.page_source
        songs, artists = extract_songs_and_artists(page_html)

        if len(songs) != len(artists):
            print("WARNING! Number of songs and artist do not match!")
        
        print(f"Found {len(songs)} songs")
        print("\n".join(songs[:5]),".\n"*3,"\n".join(songs[-5:]))

        selection = inquirer.checkbox("Save to (space to select):",
                              choices=['txt', 'html'])
        if "html" in selection:
            save_file(page_html,".html")
        if "txt" in selection:
            content = "\n".join([f"{song} - {artist}" for song, artist in zip(songs,artists)])
            save_file(content,".txt")

        another_round = inquirer.confirm("Extract another playlist?", default=True)
        if not another_round:
            break
        
    driver.quit()

def save_file(content,ext):
    """Save the file to the output folder with the provided extension

    Args:
        content (str): file content
        ext (str): file extension
    """
    folder = "input"
    filename = "anghami"+ext
    # Ensure the folder exists
    Path(folder).mkdir(parents=True, exist_ok=True)

    # Define the path object for the file
    base_path = Path(folder) / filename

    # Split the base name and extension
    base_name, ext = base_path.stem, base_path.suffix
    file_path = base_path

    # Generate unique filename by checking existence
    counter = 1
    while file_path.exists():
        file_path = Path(folder) / f"{base_name}{counter}{ext}"
        counter += 1
    
    # Write the content to the file
    with open(file_path, 'w') as file:
        file.write(content)

    print(f"File saved as: {file_path}")

if __name__ == "__main__":
    Scrape_Anghami()