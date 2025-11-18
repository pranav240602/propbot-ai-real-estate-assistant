# GCP Push Commands
gcloud auth activate-service-account --key-file=$GCP_CREDENTIALS
gcloud config set project $GCP_PROJECT_ID
gcloud artifacts repositories create propbot-models --repository-format=docker --location=us-central1
docker tag propbot-model:latest us-central1-docker.pkg.dev/$GCP_PROJECT_ID/propbot-models/propbot:20251112_150901
docker push us-central1-docker.pkg.dev/$GCP_PROJECT_ID/propbot-models/propbot:20251112_150901
