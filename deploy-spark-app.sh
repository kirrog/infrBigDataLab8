#!/bin/bash

kubectl create -f configs/spark-namespace.yml

kubectl create serviceaccount spark --namespace=default

kubectl create clusterrolebinding spark-operator-role --clusterrole=cluster-admin --serviceaccount=default:spark --namespace=default

helm repo add spark-operator https://kubeflow.github.io/spark-operator
helm repo update

helm install spark-operator/spark-operator --namespace spark-operator --set sparkJobNamespace=default --set webhook.enable=true --generate-name --set image.tag=v1beta2-1.3.3-3.1.1 --set image.repository=ghcr.io/googlecloudplatform/spark-operator

kubectl apply -f configs/spark-app-datamart.yml
