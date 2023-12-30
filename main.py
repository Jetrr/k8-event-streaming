from google.cloud import pubsub_v1, container_v1
from google.oauth2 import service_account
from kubernetes import client as k8s_client, watch as k8s_watch
from google.cloud import container_v1
from google.auth.transport.requests import Request
from tempfile import NamedTemporaryFile
import base64
import json

KEYFILE_PATH = "/etc/secrets" # mounted this secret in the k8 deployment file

PROJECT_ID = "jetrr-cloud"
CLUSTER_LOCATION = "us-central1-f"
CLUSTER_NAME = "gpu-cluster-auto"
NAMESPACE = "default"

credentials = service_account.Credentials.from_service_account_file(
    filename=KEYFILE_PATH,
    # IMPORTANT: scopes must be set to access the refresh the Token Manually.
    scopes=["https://www.googleapis.com/auth/cloud-platform"],
)
credentials.refresh(Request())

def get_k8s_client():
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

# Create a Kubernetes API client
k8_coreApi = k8s_client.CoreV1Api()

# Create a watch object
watch = k8s_watch.Watch()

while True:
    try:
        # Start watching for events
        for event in watch.stream(k8_coreApi.list_namespaced_event, namespace=NAMESPACE):
            print(event)

    except Exception as e:
        print(e)