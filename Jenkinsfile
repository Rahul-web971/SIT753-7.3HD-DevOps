pipeline {
    agent any
    options { timestamps(); disableConcurrentBuilds() }
    environment {
        IMAGE = 'task-api'
        NETWORK = 'task-api-net'
    }
    stages {
        stage('Build') {
            steps {
                sh 'python3 -m compileall -q app'
                sh 'docker build -t "$IMAGE:$BUILD_NUMBER" .'
                sh 'docker save "$IMAGE:$BUILD_NUMBER" -o task-api-image.tar'
                archiveArtifacts artifacts: 'task-api-image.tar', fingerprint: true
            }
        }
        stage('Test') {
            steps {
                sh 'python3 -m unittest discover -s tests -v'
                sh 'docker network inspect "$NETWORK" >/dev/null 2>&1 || docker network create "$NETWORK"'
                sh 'docker rm -f task-api-staging >/dev/null 2>&1 || true'
                sh 'docker run -d --name task-api-staging --network "$NETWORK" -p 18080:8000 -e APP_VERSION="$BUILD_NUMBER" "$IMAGE:$BUILD_NUMBER"'
                sh 'python3 scripts/smoke.py http://127.0.0.1:18080'
            }
        }
        stage('Code Quality') {
            steps {
                sh 'python3 -m ruff check app tests scripts'
            }
        }
        stage('Security') {
            steps {
                sh 'python3 -m bandit -r app -ll'
            }
        }
        stage('Deploy') {
            steps {
                sh 'python3 scripts/smoke.py http://127.0.0.1:18080'
            }
        }
        stage('Release') {
            steps {
                sh 'docker tag "$IMAGE:$BUILD_NUMBER" "$IMAGE:production"'
                sh 'docker rm -f task-api-production >/dev/null 2>&1 || true'
                sh 'docker run -d --restart unless-stopped --name task-api-production --network "$NETWORK" -p 18081:8000 -e APP_VERSION="$BUILD_NUMBER" "$IMAGE:production"'
                sh 'python3 scripts/smoke.py http://127.0.0.1:18081'
            }
        }
        stage('Monitoring') {
            steps {
                sh 'docker run --rm --entrypoint=promtool -v "$PWD/monitoring:/etc/prometheus:ro" prom/prometheus:v2.53.0 check config /etc/prometheus/prometheus.yml'
                sh 'docker rm -f task-api-prometheus >/dev/null 2>&1 || true'
                sh 'docker run -d --restart unless-stopped --name task-api-prometheus --network "$NETWORK" -p 19090:9090 -v "$PWD/monitoring:/etc/prometheus:ro" prom/prometheus:v2.53.0 --config.file=/etc/prometheus/prometheus.yml'
                sh 'python3 scripts/monitor.py'
            }
        }
    }
    post {
        always { sh 'docker rm -f task-api-staging >/dev/null 2>&1 || true' }
    }
}
