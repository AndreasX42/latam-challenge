### Part I
- We choose the XGBoost model from section
    6.b.i. XGBoost with Feature Importance and with Balance
  because it is a nudge better in the F1 scores from the classification_report and
  also the confusion matrix shows considerably more as true positive and true negative
  classified samples.

### Part II
- We use pydantic to validate each request. Every `/predict` request should be a list of 
  SingleFlightPredictionRequests, where we check that `TIPOVUELO`, `MES` and `OPERA` attributes
  are in the expected range. If not, we return status code `400` using the `validation_exception_handler`.

### Part III
- For providing the API endpoints we use the Google Kubernetes Engine and set up a Kubernetes cluster.
The configurations for this are in `challenge/gke_k8s_deploy_[prod/test].yaml`, where we define the deployments, services and the ingress-nginx to open the cluster for external calls and to route the requests according to specific
URLs. The FastAPI endpoints are available under `http://34.42.13.236/api` and the docs under
`http://34.42.13.236/api/docs`.

### Part IV
- Our approach for implementing the Continuous Integration is as follows:
  1. If we push something to the `develop` branch we first run the model and api tests using the `Dockerfile.localtest`.
  2. If tests pass, we build the new API from `Dockerfile.prod` and push it to Docker Hub, here we push two images using the current Github CI workflow run number and the `latest` tags as is considered best practice.
  3. Then we deploy the image to our Kubernetes cluster into a `test-api-deployment` pod that is specifically used to run the stress-test. It is externally accessable with `http://34.42.13.236/test` using the ingress-nginx routing. This extra Kubernetes pod is important as we don't want to deploy the image to a production pod yet or run stress-tests on the production pod.
  4. Run the API stress-test.
  5. Create a pull request on the main branch.
  6. At the end of the CI workflow three artifacts are generated that contain the reports of the model, api and stress tests.
  
- The Continuous Deployment is more straightforward:
  1. When the CI is done and the PR was created we first auto-merge it into main.
  2. We deploy the new API image into our production pod using the `api-deployment`. Here we use the imperative Kubernetes command `kubectl set image` to deploy the new API Docker image with the current Github CD workflow run number tag into the cluster.

All Docker images that are pushed into Docker Hub can be found here:
`https://hub.docker.com/repository/docker/andreasx42/latam-api-challenge`

