# infrBigDataLab8

## Run
`minikube start`

`ssh -i $(minikube ssh-key) docker@$(minikube ip)`
`scp -i $(minikube ssh-key) sql/init.sql docker@$(minikube ip):/ITMO_Big_Data_lab8/sql/`
`scp -i $(minikube ssh-key) data/openfood.csv docker@$(minikube ip):/ITMO_Big_Data_lab8/data/`
`./deploy-mssql.sh`

`./deploy-spark-app.sh`