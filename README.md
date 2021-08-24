# Sportsbook Web Scraper
#### DISCLAIMER: This is an individual research project to test the feasability of using AWS Lambda functions to gather real-time webscraping data across multiple platforms and house it in a central location. This project has absolutely no use case in sports betting and will not help anybody gain an advantage in that practice. Likewise, please follow all of the terms and conditions listed by various sportsbooks, as some expressly prohibit webscraping data. ####
### What is This Project? ###
The goal of this project is to test the speed and reliability of lambda functions. AWS lambda functions are a cheaper alternative to an EC2 instance running 24/7, as they only charge the user per invocation. However the downside to this is speed. Because these functins are recompiled and packaged every time they are run, they have an inherent "Cold-start delay." The question becomes, is this cold start delay enough to cause a significant difference in realtime data.

Here is the thought process. If we use lambda functions to compile this data into a central repository and then compare it with the actual real-time data, The inaccuracy of odds data will tell us how well the lambda functions are performing with a cold start.
### My Findings ###
Webscraping real time data with lambda functions is fast, but not nearly fast enough to be pulling real-time data. The cold start is extremely significant, and is even more significant if your lambda function is packaging significantly memory-intensive modules like selenium or pymysql. 
### How to Use This Project ###
* __Step One: Create an Amazon MySQL RDS.__ This is where you will store the input data, and the schema is defined in the post requests to the database in each python file.
* __Step 1.5: Set your environment variables.__ The environment variables are used by your lambda function to push to the aws mysql rds, populate the host, username, database, and password accordingly.
* __Step Two: Clean and Package Each Module using the Makerfile.__ Pretty self explanatory, each module here is a different lambda function, one for each sportsbook and then a utility function that cleans up the database.
* __Step Three: Upload the Zipped Modules to S3.__ Make a separate lambda function for each module.
* __Step Four: Create Cloudwatch Triggers for Each Lambda Function.__ This part is up to user discretion, you can run these at whatever interval you please, but the functions take about a minute each to run, so try not to run them any more frequent than minute-long intervals or you risk running into errors.
