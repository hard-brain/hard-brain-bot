# Hard Brain Bot  

A service which runs a Discord bot for playing IIDX song quizzes. Connects to the Hard Brain API to fetch 
song data and audio files.

# Usage  

This service depends on Python 3.11 and Poetry 1.7.1, and Docker is strongly recommended.

## Running within Docker  

For running within Docker, please refer to the 
[hard-brain-deploy](https://github.com/hard-brain/hard-brain-deploy) 
repo, which will run all services required by Hard Brain.

## Running locally  

This service is designed to be run alongside the Hard Brain API. If those services are running, do the following:  

1. Set an environment variable `DISCORD_TOKEN` as your Discord bot API token
2. Create a new Poetry environment and run `poetry install`
3. Run `python hard_brain_bot/__main__.py`

# Contribution & Feedback
Issues and PRs are welcome, and any general feedback for Hard Brain as a whole can be submitted 
[here](https://github.com/orgs/hard-brain/discussions/categories/song-title-changes).
