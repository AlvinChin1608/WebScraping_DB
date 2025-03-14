# IMDB Top 250 Movies Scraper, ETL, DB

This project is a data pipeline that automatically scrapes the IMDB Top 250 Movies list, processes the data, and stores it in a SingleStore database. It's designed to track changes in movie rankings and details over time by taking daily snapshots of the IMDB Top 250 list.

## Features
- ***Web Scraping***: Automates browser interaction using Playwright to extract data from IMDB's Top 250 Movies page
- ***Data Processing***: Cleans and formats movie information including titles, ratings, duration, directors, stars, and descriptions
- ***Database Storage***: Stores data in SingleStore with support for both inserting new records and updating existing ones
- ***Unique Identification***: Generates unique keys for each movie to track changes over time
- ***Error Handling***: Comprehensive logging system to capture and record any issues during execution
- ***Daily Snapshots***: Captures the state of the IMDB Top 250 list on a specific date
