#!/bin/bash

kubectl apply -f configs/mssql-service.yml
kubectl apply -f configs/mssql-statefulset.yml