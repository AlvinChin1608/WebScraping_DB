# IMDB Top 250 Movies Scraper, ETL, DB

This project is a data pipeline that automatically scrapes the IMDB Top 250 Movies list, processes the data, and stores it in a SingleStore database. It's designed to track changes in movie rankings and details over time by taking daily snapshots of the IMDB Top 250 list.

## Features
- ***Web Scraping***: Automates using Playwright to extract data from IMDB's Top 250 Movies page
- ***Data Processing***: Cleans and formats movie information including titles, ratings, duration, directors, stars, and descriptions
- ***Database Storage***: Stores data in SingleStore with support for both inserting new records and updating existing ones
- ***Unique Identification***: Generates unique keys for each movie to track changes over time
- ***Error Handling***: Comprehensive logging system to capture and record any issues during execution
- ***Daily Snapshots***: Captures the state of the IMDB Top 250 list on a specific date

## Technologies Used

- ***Python:*** Core programming language
- ***Playwright:*** Web automation and scraping
- ***Pandas:*** Data manipulation and CSV handling
- ***SingleStoreDB:*** SQL database for data storage
- ***dotenv:*** Environment variable management for secure credential handling


## How It Works

1. ***Data Collection:*** The script uses Playwright to navigate to IMDB's Top 250 Movies page and clicks on each movie's information button to extract detailed data
2. ***Data Processing:*** Movie details are formatted consistently (e.g., duration is standardized to "H:MM" format, actor names are properly separated)
3. ***CSV Storage:*** Processed data is saved as a CSV file with the current date in the filename
4. ***Database Storage:***
  - Data is loaded from the CSV into the SingleStore database
  - For each movie, the script checks if it already exists in the database (using the unique key)
  - New records are inserted and existing ones are updated if necessary

### Future Enhancements
- Build a dashboard to visualize changes in movie rankings over time
- Implement scheduling for automatic daily updates such as using Apache Airflow (Next project)
- Add notifications for significant ranking changes
- Expand to include more movie details and other IMDB lists
