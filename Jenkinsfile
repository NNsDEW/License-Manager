pipeline {
    agent any

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Set up Python') {
            steps {
                sh 'python -m venv .venv || true'
                sh '.venv/bin/pip install --upgrade pip'
                sh '.venv/bin/pip install -r requirements.txt'
            }
        }

        stage('Tests') {
            steps {
                sh '.venv/bin/python manage.py test'
            }
        }

        stage('Build Docker image') {
            steps {
                sh 'docker build -t licensing-backend:latest .'
            }
        }
    }
}

