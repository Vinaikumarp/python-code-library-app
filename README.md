# Digital Library Application — Python CI/CD Pipeline

## Project Overview

This project implements a CI/CD pipeline for a Python-based Digital Library application using **GitHub, Jenkins, SonarQube, Trivy, Docker, and Docker Hub**.

The pipeline checks out application code, performs code-quality analysis, checks the SonarQube Quality Gate, builds Docker images for the application components, scans the images for known vulnerabilities, pushes images to Docker Hub, and deploys the containers.

## Technology Stack

**Python** — application language
**GitHub** — source-code repository
**Jenkins** — CI/CD automation
**SonarQube / PySonar** — code-quality analysis integration
**Docker** — image build and container runtime
**Trivy** — container-image vulnerability scanning
**Docker Hub** — image registry
**Docker Compose** — intended option for defining and running multiple containers

## Application Components

The Jenkinsfile builds the following images:

| Component | Local image | Docker Hub image |
|---|---|---|
| Database | `dbimage:v1` | `vinaikumarp/db:v1` |
| Authentication service | `authimage:v1` | `vinaikumarp/auth:v1` |
| Book service | `bookimage:v1` | `vinaikumarp/book:v1` |
| Borrow service | `borrowimage:v1` | `vinaikumarp/borrow:v1` |
| Frontend/application | `appimage:v1` | `vinaikumarp/app:v1` |

The build commands expect the repository to contain `database/`, `auth/`, `book/`, and `borrow/` directories, each with an appropriate Dockerfile. The root directory must also contain a Dockerfile for the frontend/application image.

## CI/CD Pipeline Workflow

text
Developer pushes code
        |
        v
GitHub repository
        |
        v
Jenkins pipeline (manager label)
        |
        v
Checkout source code
        |
        v
Install PySonar / scanner dependency
        |
        v
SonarQube code-quality analysis
        |
        v
Quality Gate
   Pass  |  Fail
     |        |
     v        v
Build images  Stop pipeline
     |
     v
Trivy image vulnerability scans
     |
     v
Push images to Docker Hub
     |
     v
Deploy application containers


## Pipeline Stages

### 1. Select the Jenkins agent

The pipeline uses the Jenkins node with the `manager` label:

groovy
agent {
    label 'manager'
}


Make sure the node has Python/pip, Git, Docker, Trivy, and the required Jenkins plugins installed and configured. The Jenkins user must have authorized access to the Docker daemon.

### 2. Checkout code from GitHub

The pipeline checks out the project repository:

groovy
git 'https://github.com/Vinaikumarp/python-code-library-app.git'


If the repository is private, configure Jenkins SCM credentials with a GitHub Personal Access Token (PAT) or SSH key. Do not store the PAT in the Jenkinsfile.

### 3. Install the code-analysis dependency

The provided Jenkinsfile runs:


pip install pysonar


Use a supported Python environment and verify that the installed package actually provides the `pysonar` command and supports the options used in the pipeline. If your SonarQube setup uses the official SonarScanner CLI or another scanner, configure the matching scanner and arguments instead.

### 4. Perform code-quality analysis (CQA)

The pipeline runs the scanner against the configured SonarQube server and project key.

Configuration values in the original example:

- SonarQube project key: `myProject`
- SonarQube server: `http://35.77.62.87:9000`

Check that the server URL is reachable from the Jenkins agent. Store the SonarQube token in Jenkins Credentials (for example, Secret text with ID `sonar-token`) and inject it into the pipeline. Never commit a token to this repository or print it in build logs.

### 5. Enforce the Quality Gate

The Quality Gate stage checks the analysis result configured in SonarQube. Configure a SonarQube webhook to notify Jenkins:

text
http://<JENKINS-URL>:<PORT>/sonarqube-webhook/


The Jenkins server must be reachable from SonarQube at that URL. Use the SonarQube Scanner for Jenkins plugin and the configured SonarQube installation. A failing Quality Gate should stop later stages when `abortPipeline: true` is used.

### 6. Build Docker images

The pipeline builds five images:


docker build -t dbimage:v1 database/
docker build -t authimage:v1 auth/
docker build -t bookimage:v1 book/
docker build -t borrowimage:v1 borrow/
docker build -t appimage:v1 .
docker images


Ensure each build context contains the correct Dockerfile and application files. The database image should follow the database project's intended image and initialization approach.

### 7. Scan images with Trivy

The pipeline scans each locally built image:


trivy image dbimage:v1
trivy image authimage:v1
trivy image bookimage:v1
trivy image borrowimage:v1
trivy image appimage:v1


The original pipeline redirects scan output into text files. For example:


trivy image dbimage:v1 > db-image.txt


To fail a build when HIGH or CRITICAL vulnerabilities are found, configure an explicit policy such as:


trivy image --severity HIGH,CRITICAL --exit-code 1 dbimage:v1


Apply the same policy to the other images if that is your team's requirement. A scan that only writes a report does not automatically fail the pipeline based on findings. Archive the generated reports in Jenkins if you need to retain them.

### 8. Push images to Docker Hub

The pipeline uses the Jenkins Docker registry credential ID `dockerhub`. Configure this credential in Jenkins with a Docker Hub account and a token that has the required push permissions.

The pipeline tags and pushes:


docker tag dbimage:v1 vinaikumarp/db:v1
docker tag authimage:v1 vinaikumarp/auth:v1
docker tag bookimage:v1 vinaikumarp/book:v1
docker tag borrowimage:v1 vinaikumarp/borrow:v1
docker tag appimage:v1 vinaikumarp/app:v1

docker push vinaikumarp/db:v1
docker push vinaikumarp/auth:v1
docker push vinaikumarp/book:v1
docker push vinaikumarp/borrow:v1
docker push vinaikumarp/app:v1


Confirm that the Docker Hub repositories exist or that your account can create them, and ensure the credential has write access.

### 9. Deploy the containers

The current Jenkinsfile uses `docker run`, not Docker Compose. It expects the `mynet` Docker network to exist and starts the components with these port mappings:

| Container | Host port | Container port |
|---|---:|---:|
Database - 3306 - 3306
Authentication - 5001 - 5001
Book - 5002 - 5002
Borrow - 5003 - 5003
Frontend/application - 5000 - 5000

The commands in the pipeline are:

docker run -d --name db -p 3306:3306 --network mynet dbimage:v1
docker run -d --name auth_service --network mynet -p 5001:5001 authimage:v1
docker run -d --name book_service -p 5002:5002 --network mynet bookimage:v1
docker run -d --name borrow_service -p 5003:5003 --network mynet borrowimage:v1
docker run -d --name frontend -p 5000:5000 --network mynet appimage:v1

Create the network idempotently before deployment:

docker network inspect mynet >/dev/null 2>&1 || docker network create mynet

**Deployment note:** These `docker run` commands will fail if containers with the same names already exist. A repeatable pipeline should stop/remove old containers or use Docker Compose to manage updates. Publishing the database port exposes it on the host; only do this if needed and restrict access with firewall/security-group rules.

## Docker Compose note

The project description mentions Docker Compose, but the supplied Jenkinsfile deploys containers individually with `docker run`. To use Compose, add a `compose.yaml` file describing the five services, their image names, ports, environment configuration, dependencies, networks, and persistent volumes, then deploy with:

docker compose up -d
docker compose ps
docker compose logs

Do not describe the current deployment as Compose-based until the Jenkinsfile actually runs Docker Compose.

## Jenkins Configuration Checklist
Before running the job, verify:

Jenkins node label `manager` exists and the node is online.
Git is installed and the private GitHub repository credentials are configured, if required.
Python and pip are available.
The SonarQube server installation is configured in Jenkins (the example uses `mysonar`).
SonarQube token is stored in Jenkins Credentials.
The SonarQube webhook points to the correct Jenkins URL.
Docker is installed and Jenkins can access the Docker daemon.
Trivy is installed.
Docker Hub credential ID `dockerhub` is configured with push permissions.
Docker network `mynet` is created if using the supplied `docker run` commands.
All image build contexts and Dockerfiles exist.

## Troubleshooting Commands

# Check Jenkins agent identity and installed tools
hostname
whoami
python3 --version
pip3 --version
docker --version
docker compose version
trivy --version

# Check Docker network and containers
docker network ls
docker network inspect mynet
docker ps -a

# Inspect application logs
docker logs db
docker logs auth_service
docker logs book_service
docker logs borrow_service
docker logs frontend

# Check Docker Hub images after push
docker pull vinaikumarp/app:v1


## Security Recommendations

- Store GitHub, SonarQube, and Docker Hub credentials in Jenkins Credentials.
- Rotate any token that has been exposed in chat, logs, or source control.
- Avoid committing passwords, PATs, or `.env` files.
- Use restricted firewall rules for database and application ports.
- Pin trusted base images and update dependencies regularly.
- Treat Trivy results as a policy gate when required; saving scan output alone does not enforce a pass/fail threshold.
- Use a proper secrets-management approach for database passwords.

## Outcome

This project demonstrates an automated CI/CD workflow for a Python Digital Library application: source checkout, code-quality analysis, Quality Gate enforcement, Docker image creation, vulnerability scanning, registry publishing, and container deployment.
