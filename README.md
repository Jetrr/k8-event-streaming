# Event Streaming

This repository contains the code for an event streaming application. The application is written in Python and is designed to be deployed to a Google Kubernetes Engine (GKE) cluster.

## Repository Structure

Here's a brief explanation of the key files and directories in this repository:

- [`main.py`](command:_github.copilot.openRelativePath?%5B%22main.py%22%5D "main.py"): This is the main Python script for the event streaming application. It uses the Google Cloud Pub/Sub and Kubernetes Python clients to interact with GKE and Pub/Sub.

- [`requirements.txt`](command:_github.copilot.openRelativePath?%5B%22requirements.txt%22%5D "requirements.txt"): This file lists the Python dependencies that need to be installed for the application to run.

- [`Dockerfile`](command:_github.copilot.openRelativePath?%5B%22Dockerfile%22%5D "Dockerfile") and [`Dockerfile.dev`](command:_github.copilot.openRelativePath?%5B%22Dockerfile.dev%22%5D "Dockerfile.dev"): These files are used to build the Docker images for the application. The [`Dockerfile`](command:_github.copilot.openRelativePath?%5B%22Dockerfile%22%5D "Dockerfile") is used for production builds, while [`Dockerfile.dev`](command:_github.copilot.openRelativePath?%5B%22Dockerfile.dev%22%5D "Dockerfile.dev") is used for development builds.

- [`docker-compose.yml`](command:_github.copilot.openRelativePath?%5B%22docker-compose.yml%22%5D "docker-compose.yml"): This file is used to define and run the application's services using Docker Compose. It's particularly useful for local development.

- [`deploy.yml`](command:_github.copilot.openRelativePath?%5B%22deploy.yml%22%5D "deploy.yml"): This is a Kubernetes deployment configuration file. It defines a Deployment for the application on a GKE cluster.

- [`create-secret.sh`](command:_github.copilot.openRelativePath?%5B%22create-secret.sh%22%5D "create-secret.sh"): This shell script creates a Kubernetes Secret from a JSON key file. This Secret is used to authenticate the application with Google Cloud services.

- [`.github/workflows/main.yml`](command:_github.copilot.openRelativePath?%5B%22.github%2Fworkflows%2Fmain.yml%22%5D ".github/workflows/main.yml"): This is a GitHub Actions workflow that automates the building, pushing, and deploying of the application to GKE whenever changes are pushed to the `main` branch.

## Getting Started

To get started with development:

1. Install the Python dependencies:

```sh
pip install -r requirements.txt
```

2. Build the Docker image for development:

```sh
docker-compose build
```

3. Run the application's services:

```sh
docker-compose up
```

## Deployment

To deploy the application to GKE, you'll need to set up a service account on Google Cloud with the necessary permissions, and create a JSON key file for it. Then, run the [`create-secret.sh`](command:_github.copilot.openRelativePath?%5B%22create-secret.sh%22%5D "create-secret.sh") script to create a Kubernetes Secret from the key file.

The GitHub Actions workflow in [`.github/workflows/main.yml`](command:_github.copilot.openRelativePath?%5B%22.github%2Fworkflows%2Fmain.yml%22%5D ".github/workflows/main.yml") will automatically handle the rest of the deployment process whenever changes are pushed to the `main` branch. It builds a new Docker image, pushes it to the Google Artifact Registry, and updates the Deployment on GKE.

Please ensure that the necessary secrets (`GCP_SA_KEY`) are set in your GitHub repository's settings for the GitHub Actions workflow to work.