# SIT753 7.3HD: Task API DevOps pipeline

A small Python task API with `GET /health`, `GET /tasks`, `POST /tasks`, `PATCH /tasks/{id}`, and `GET /metrics`. Data is held in memory and resets when the container restarts. The build artifact is a Docker image saved as `task-api-image.tar` in Jenkins.

## Requirements

A Jenkins machine with Python 3.12, Docker Engine (Jenkins account allowed to run Docker), Git, and network access to Docker Hub and Python package downloads. Install Ruff and Bandit for the Jenkins Python interpreter before running the pipeline: `python3 -m pip install ruff bandit` (use a virtual environment if your OS restricts system pip). Jenkins needs Pipeline and Git plugins and sufficient disk space for archived Docker images. Ports 18080, 18081, and 19090 must be free. This setup assumes Jenkins runs directly on the Docker host; containerised Jenkins requires Docker access and networking adjustments.

## Set up

1. Create an empty GitHub repository. Upload all files in this folder, keeping `Jenkinsfile` at the repository root. Do not upload the original task PDF or template as project source.
2. In Jenkins select **New Item** → name `SIT753-7.3HD` → **Pipeline** → **OK**.
3. Under **Pipeline**, choose **Pipeline script from SCM**. Choose **Git**, enter the repository URL and credentials if private, branch `*/main`, script path `Jenkinsfile`, then **Save**.
4. Select **Build Now**. Open the build → **Console Output** and **Pipeline Steps/Stage View**. Resolve any host setup errors and rerun until all seven stages are green.
5. Inspect `http://localhost:18081/health` on the Jenkins host, `http://localhost:18081/tasks`, and Prometheus at `http://localhost:19090/targets`. If viewing from another computer, substitute the Jenkins machine's host name. Create a task with `curl -X POST http://localhost:18081/tasks -H 'Content-Type: application/json' -d '{"title":"Demo task"}'`.
6. In Prometheus, the `task-api` target must show **UP**. To demonstrate a real alert, stop the production container after the successful build using `docker stop task-api-production`; wait at least 40 seconds, then view `http://localhost:19090/alerts` for **TaskApiDown**. Restart with `docker start task-api-production` and confirm the target returns to **UP**. This simulation is after the pipeline run, not during it.

## Stages and evidence

| Stage | Implementation | Evidence to capture |
|---|---|---|
| Build | Compile Python; build Docker image; archive image tar | Build log and artifact |
| Test | Three automated API integration tests; staging container smoke check | Test log |
| Code Quality | Ruff lint; fails on findings | Ruff console result |
| Security | Bandit scans Python source for high severity issues; fails on findings | Bandit output; discuss any findings |
| Deploy | Rechecks staging application health | Stage output and staging URL |
| Release | Tags same image `production`, starts production container, smoke checks | Production URL |
| Monitoring | Prometheus configuration check, production scrape, `TaskApiDown` alert rule | `/targets` showing UP and `/alerts` demonstration |

## Submission template

- **Video link:** [add after recording; 10 minutes maximum]
- **GitHub repository:** [add your repository URL; grant marker and unit chair access if private]
- **Stage count:** 7, *only if all seven run successfully*; otherwise state the actual count.
- **Project description:** Python task management API with create, list, and complete operations, Docker packaging, Jenkins CI/CD and Prometheus metrics and alerting.
- **Jenkins screenshot:** [insert your own Stage View screenshot]
- **Stage descriptions:** Use the table above and briefly describe what the actual logs show, including any security findings.

Do not claim the pipeline was executed until you have confirmed the real Jenkins run. Local Docker production here is a demonstration environment, not an internet-hosted production service. Alerting is visible in Prometheus; no external notification receiver is configured.

## Video order

Show GitHub repository and cloning command; open Jenkins job configuration showing SCM and `Jenkinsfile`; trigger a run; walk through each stage and its console evidence; open `/health` and Prometheus `/targets`; simulate alert and recovery; keep total runtime under 10 minutes.
