from google.cloud import pubsub_v1, container_v1
from google.oauth2 import service_account
from kubernetes import client as k8s_client, watch as k8s_watch
import kubernetes
from google.cloud import container_v1
from google.auth.transport.requests import Request
from tempfile import NamedTemporaryFile
import base64
import json
import os

print("EVENT STREAM SERVICE STARTING...")

ENV = os.environ.get("ENV", "DEV")

PROD_KEYFILE_PATH = "/etc/secret/keyfile.json" # mounted this secret in the k8 deployment file

KEYFILE_PATH = "keyfile.json"

if ENV == "production":
    KEYFILE_PATH = PROD_KEYFILE_PATH
    print("PRODUCTION ENVIRONMENT DETECTED")
else:
    print("DEV ENVIRONMENT DETECTED")


PROJECT_ID = "jetrr-cloud"
CLUSTER_LOCATION = "us-central1-f"
CLUSTER_NAME = "gpu-cluster-auto"
NAMESPACE = "default"
TOPIC_NAME = "vertex-job-status-update-topic-sub"

credentials = service_account.Credentials.from_service_account_file(
    filename=KEYFILE_PATH,
    # IMPORTANT: scopes must be set to access the refresh the Token Manually.
    scopes=["https://www.googleapis.com/auth/cloud-platform"],
)

def get_k8s_client():
    credentials.refresh(Request())
    token = credentials.token
    # Create the Cluster Manager Client
    cluster_client = container_v1.ClusterManagerClient(
        credentials=credentials
    )
    request = container_v1.GetClusterRequest(
        name=f'projects/{PROJECT_ID}/locations/{CLUSTER_LOCATION}/clusters/{CLUSTER_NAME}'
    )
    response = cluster_client.get_cluster(request)

    endpoint = response.endpoint
    certificate_authority = response.master_auth.cluster_ca_certificate

    configuration = k8s_client.Configuration()
    configuration.host = f'https://{endpoint}'
    configuration.api_key['authorization'] = 'Bearer ' + token
    configuration.verify_ssl = True
    # Provide a path to a valid certificate authority file.
    with NamedTemporaryFile(delete=False) as cert:
        cert.write(base64.b64decode(certificate_authority))
        configuration.ssl_ca_cert = cert.name

    k8s_client.Configuration.set_default(configuration)

    return k8s_client

k8s_client = get_k8s_client()

publisher = pubsub_v1.PublisherClient(credentials=credentials)

def publish_topic(topic_name, data: dict):
    topic_path = publisher.topic_path(PROJECT_ID, topic_name)
    data = json.dumps(data).encode("utf-8")
    future = publisher.publish(topic_path, data)
    future.result()

while True:
    try:
        # Create a Kubernetes API client
        k8_coreApi = k8s_client.CoreV1Api()
        k8s_client = get_k8s_client()  # Reinitialize the k8s client (with new token)
        # Create a watch object
        watch = k8s_watch.Watch()
        # Start watching for events
        for event in watch.stream(k8_coreApi.list_namespaced_event, namespace=NAMESPACE):
            try:
                
                # bypass all events that are not related to `Job`
                object_kind = event["object"].involved_object.kind # Job
                if object_kind != "Job":
                    continue

                job_name = event["object"].involved_object.name
                reason = event["object"].reason

                print(f"Publishing {job_name} with reason: `{reason}`") # For debugging

                publish_topic(TOPIC_NAME, {
                    "job_name": job_name,
                    "reason": reason
                })

                # print("Published Sucessfully")
            except Exception as e:
                print("Exception Occured:", e)

    except kubernetes.client.exceptions.ApiException as e:
        # After some time the token would expire, so we need to refresh it
        # Handle token expiration
        if e.status == 401:
            print("Token expired, refreshing credentials")
            continue
        # Handle resourceVersion too old
        elif e.status == 410:
            print("Resource Version too old...")
            continue
        # Handle rate limiting
        elif e.status == 429:
            print("Rate Limiting Error Occured...")
            continue
        # Handle server errors
        elif 500 <= e.status < 600:
            print("Server Error At GKE Occured...")
            print(e)
            continue
        else:
            # Handle other ApiException cases...
            raise