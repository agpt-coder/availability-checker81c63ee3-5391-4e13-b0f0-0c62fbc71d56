---
date: 2024-04-26T20:20:54.408724
author: AutoGPT <info@agpt.co>
---

# Availability Checker

Function that returns the real-time availability of professionals, updating based on current activity or schedule.

**Features**

- **Real-Time Availability Display** This feature visually displays the real-time availability of professionals. It dynamically updates to reflect any changes in their schedules or current activities.

- **Interactive Scheduling Interface** Users can interact with the schedule, selecting available time slots for appointments directly through the interface.

- **Notifications and Alerts** Provides timely notifications and alerts to users about the confirmation of bookings, changes, or cancellations in schedules.

- **User Profile Integration** Integrates personal profiles where users can view their booked appointments, favorite professionals, and history.


## What you'll need to run this
* An unzipper (usually shipped with your OS)
* A text editor
* A terminal
* Docker
  > Docker is only needed to run a Postgres database. If you want to connect to your own
  > Postgres instance, you may not have to follow the steps below to the letter.


## How to run 'Availability Checker'

1. Unpack the ZIP file containing this package

2. Adjust the values in `.env` as you see fit.

3. Open a terminal in the folder containing this README and run the following commands:

    1. `poetry install` - install dependencies for the app

    2. `docker-compose up -d` - start the postgres database

    3. `prisma generate` - generate the database client for the app

    4. `prisma db push` - set up the database schema, creating the necessary tables etc.

4. Run `uvicorn project.server:app --reload` to start the app

## How to deploy on your own GCP account
1. Set up a GCP account
2. Create secrets: GCP_EMAIL (service account email), GCP_CREDENTIALS (service account key), GCP_PROJECT, GCP_APPLICATION (app name)
3. Ensure service account has following permissions: 
    Cloud Build Editor
    Cloud Build Service Account
    Cloud Run Developer
    Service Account User
    Service Usage Consumer
    Storage Object Viewer
4. Remove on: workflow, uncomment on: push (lines 2-6)
5. Push to master branch to trigger workflow
