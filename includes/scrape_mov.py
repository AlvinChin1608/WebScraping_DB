import pytz
from datetime import date, datetime, timedelta
import pandas as pd
import os
import random
import re
import singlestoredb as s2
from dotenv import load_dotenv


# Load the env variables
load_dotenv("/Users/alvinchin/Desktop/Portfolio/includes/.env")

S_HOST = os.getenv("singlestore_host")
S_USER = os.getenv("singlestore_user")
S_PASSWORD = os.getenv("singlestore_password")
S_PORT = int(os.getenv("singlestore_port"))
S_DB = os.getenv("singlestore_database")

# Local imports
from common import gen_ukey

# Playwright imports
import playwright
from playwright.sync_api import sync_playwright
from playwright_stealth import stealth_sync

# Today's Date
local_tz = pytz.timezone('Asia/Kuala_Lumpur')
local_time = datetime.now(local_tz)
DATE_TODAY = local_time.strftime("%Y%m%d")

RAW_PATH = ".data/raw_data/"
LOG_PATH = ".data/logs/"
FILE_NAME = f"{DATE_TODAY}"

def format_duration(duration):
    """Convert '2h 22min' to '2:22' format."""
    match = re.match(r'(?:(\d+)h\s*)?(?:(\d+)min)?', duration)
    if match:
        hours = match.group(1) or "0"
        minutes = match.group(2) or "00"
        return f"{int(hours)}:{int(minutes):02d}"  # Ensures two-digit minutes
    return duration  # Return as-is if no match

def format_stars(stars):
    """Convert 'Brad PittEdward NortonMeat Loaf' to 'Brad Pitt, Edward Norton, Meat Loaf'"""
    return re.sub(r'([a-z])([A-Z])', r'\1, \2', stars)

def scrape_mov():

    # Create log directory if it doesn't exist
    if not os.path.exists(LOG_PATH):
        os.makedirs(LOG_PATH)
    
    # Log file
    log_file = f"{LOG_PATH}/log_{DATE_TODAY}.txt"

    # Function to log errors
    def log_error(error_msg):
        with open(log_file, 'a') as f:
            f.write(f"{datetime.now()} - {error_msg}\n")
        print(error_msg)

    MOVIE_URL = "https://www.imdb.com/chart/top/?ref_=nv_mv_250"
    
    with sync_playwright() as p:
        browser = p.chromium.launch(channel="chrome", headless=False, timeout=20000)
        context = browser.new_context()
        page = context.new_page()
        # stealth_sync(page) 

        # Create an empty DataFrame
        df_mov = pd.DataFrame(columns=[
            "snapshot_date", "title", "rating", "release_year", 
            "genre", "duration", "director", "stars", "short_description"
        ])

        try:
            page.goto(MOVIE_URL)
            page.wait_for_selector('h1:has-text("IMDb Top 250 Movies")')
            print("Page Loaded")

            # Get all movie elements
            movie_items = page.query_selector_all('li.ipc-metadata-list-summary-item')
            print(f"Found {len(movie_items)} movies")

            for index, movie in enumerate(movie_items):
                try:
                    print(f"Processing movie {index+1}")

                    info_button_xpath = f'xpath=//*[@id="__next"]/main/div/div[3]/section/div/div[2]/div/ul/li[{index+1}]/div/div/div/div/div[3]/button'
                    
                    page.mouse.wheel(0,random.randrange(0, 70))
                    page.mouse.wheel(0,random.randrange(50, 100))

                    # Wait for the button to be available and click it
                    page.wait_for_selector(info_button_xpath, timeout=5000)
                    page.locator(info_button_xpath).click()
                    print(f"Clicked info button for movie #{index+1}")

                    # Wait for the dialog to appear
                    page.wait_for_selector('div[role="dialog"]', state='visible', timeout=5000)

                    # Scrape details
                    mov_title = page.locator('xpath=/html/body/div[4]/div[2]/div/div[2]/div/div/div[1]/div[2]/div[1]/a/h3').first.text_content()
                    mov_rating = page.locator('xpath=/html/body/div[4]/div[2]/div/div[2]/div/div/div[1]/div[2]/div[2]/span/span[1]').first.text_content()
                    mov_year = page.locator('xpath=/html/body/div[4]/div[2]/div/div[2]/div/div/div[1]/div[2]/ul[1]/li[1]').first.text_content()
                    mov_genre = page.locator('xpath=/html/body/div[4]/div[2]/div/div[2]/div/div/div[1]/div[2]/ul[2]/li').first.text_content()
                    mov_duration = page.locator('xpath=/html/body/div[4]/div[2]/div/div[2]/div/div/div[1]/div[2]/ul[1]/li[2]').first.text_content()
                    mov_director = page.locator('xpath=/html/body/div[4]/div[2]/div/div[2]/div/div/div[3]/div[1]/ul/li/a').first.text_content()
                    mov_stars = page.locator('xpath=/html/body/div[4]/div[2]/div/div[2]/div/div/div[3]/div[2]').first.text_content()
                    mov_desc = page.locator('xpath=/html/body/div[4]/div[2]/div/div[2]/div/div/div[2]').first.text_content()

                    # Apply regex formatting
                    mov_duration = format_duration(mov_duration)
                    mov_stars = format_stars(mov_stars)
                    cleaned_stars = re.sub(r"^\s*Stars\s*", "", mov_stars) # Remove "Stars" prefix and hidden spaces

                    print(f"Extracted data for {mov_title}")

                    # Close the dialog
                    page.get_by_role("button", name="Close Prompt").click()
                    print(f"Closed dialog for {mov_title}")

                    # Add data to DataFrame
                    df_mov = pd.concat([df_mov, pd.DataFrame([{
                        "snapshot_date": DATE_TODAY,
                        "title": mov_title,
                        "rating": mov_rating,
                        "release_year": mov_year,
                        "genre": mov_genre,
                        "duration": mov_duration,
                        "director": mov_director,
                        "stars": cleaned_stars,
                        "short_description": mov_desc
                    }])], ignore_index=True)

                    # Creating U_KEY
                    df_mov["u_key"] = df_mov.apply(lambda column: gen_ukey(
                        column["snapshot_date"],
                        column["title"],
                        column["genre"],
                        column["release_year"]
                    ), axis=1)  

                    page.wait_for_timeout(1000)

                except Exception as e:
                    print(f"Error processing movie {index+1}: {e}")

            # Save the DataFrame to CSV
            df_mov.to_csv(f"{RAW_PATH}/top_250_movies_{FILE_NAME}.csv", index=False)
            print("Successfully saved all movie data!")

        except Exception as e:
            print(f"Error in scraping process: {e}")

        finally:
            browser.close()

def write_to_singlestore():
    movie_file = f"{RAW_PATH}/top_250_movies_{FILE_NAME}.csv"

    LOG_PATH = ".data/logs/"
    log_file = f"{LOG_PATH}/log_{DATE_TODAY}.txt"

    # Function to log errors
    def log_error(error_msg):
        with open(log_file, 'a') as f:
            f.write(f"{datetime.now()} - {error_msg}\n")
        print(error_msg)

    try:
        # Read CSV file
        df_mov = pd.read_csv(movie_file)
        print(f"Read {len(df_mov)} records from CSV file")
        
        # Connect to SingleStore 
        conn = s2.connect(
            host=S_HOST,
            user=S_USER,
            password=S_PASSWORD,
            port=S_PORT,
            database=S_DB
        )
        
        print("Connected to SingleStore database")
        
        # Create cursor
        cursor = conn.cursor()
        
        # Create table if it doesn't exist
        create_table_query = """
        CREATE TABLE IF NOT EXISTS imdb_top_250 (
            u_key VARCHAR(255) PRIMARY KEY,
            snapshot_date VARCHAR(8),
            title VARCHAR(255),
            rating VARCHAR(10),
            release_year VARCHAR(50),
            genre VARCHAR(255),
            duration VARCHAR(10),
            director VARCHAR(255),
            stars TEXT,
            short_description TEXT
        )
        """
        
        cursor.execute(create_table_query)
        print("Table created or already exists")
        
        # Insert records
        inserted_count = 0
        updated_count = 0
        
        for _, row in df_mov.iterrows():
            # Check if the record already exists
            check_query = "SELECT COUNT(*) FROM imdb_top_250 WHERE u_key = %s"
            cursor.execute(check_query, (row['u_key'],))
            exists = cursor.fetchone()[0] > 0
            
            if exists:
                # Update existing record
                update_query = """
                UPDATE imdb_top_250 SET
                    snapshot_date = %s,
                    title = %s,
                    rating = %s,
                    release_year = %s,
                    genre = %s,
                    duration = %s,
                    director = %s,
                    stars = %s,
                    short_description = %s
                WHERE u_key = %s
                """
                
                cursor.execute(update_query, (
                    row['snapshot_date'],
                    row['title'],
                    row['rating'],
                    row['release_year'],
                    row['genre'],
                    row['duration'],
                    row['director'],
                    row['stars'],
                    row['short_description'],
                    row['u_key']
                ))
                updated_count += 1
            else:
                insert_query = """
                INSERT INTO imdb_top_250 (
                    u_key, snapshot_date, title, rating, release_year,
                    genre, duration, director, stars, short_description
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                
                cursor.execute(insert_query, (
                    row['u_key'],
                    row['snapshot_date'],
                    row['title'],
                    row['rating'],
                    row['release_year'],
                    row['genre'],
                    row['duration'],
                    row['director'],
                    row['stars'],
                    row['short_description']
                ))
                inserted_count += 1
        
        conn.commit()
        print(f"Successfully inserted {inserted_count} and updated {updated_count} records in SingleStore")
        
    except Exception as e:
        log_error(f"Error uploading to SingleStore: {e}")
    finally:
        if 'conn' in locals() and conn:
            conn.close()
            print("Database connection closed")

if __name__ == "__main__":
    scrape_mov()
    write_to_singlestore()
