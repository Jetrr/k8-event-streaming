# create secret if not exists
kubectl create secret generic sa-keyfile --from-file=keyfile.json