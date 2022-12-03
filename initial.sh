#!/bin/bash

add_iam_policy(){
    gcloud projects add-iam-policy-binding $1 --member serviceAccount:$2@$1.iam.gserviceaccount.com --role roles/$3
}

create_bucket(){
    gcloud storage buckets create gs://$1-$3 --project $1 --location $2
}

make_key_file(){
    gcloud iam service-accounts keys create $2.json --iam-account $2@$1.iam.gserviceaccount.com
    gsutil cp -rp $2.json gs://$1-sa-master/
    rm -rf $2.json
}

api_available(){
    gcloud services enable $2 --project $1
}

# プロジェクト選択
proj=`gcloud projects list --format="value(project_id)" | fzf --header "[GCP Project]"`
echo $proj > project.txt

# リージョン選択
region=`gcloud compute regions list --format "value(name)" | fzf --header "[Region]"`
echo $region > region.txt

# サービスアカウント作成
sa_service=service
sa_terraform=terraform
gcloud iam service-accounts create $sa_service --project $proj
gcloud iam service-accounts create $sa_terraform  --project $proj

# 権限追加
while read line; do
    add_iam_policy $proj $sa_service $line
done << END
datastore.user
storage.objectAdmin
END

while read line; do
    add_iam_policy $proj $sa_terraform $line
done << END
run.admin
editor
END

# キーファイル格納用バケット作成
create_bucket $proj $region sa-master

# キーファイル作成
make_key_file $proj $sa_service
make_key_file $proj $sa_terraform

# staticファイル格納用バケット作成
create_bucket $proj $region evaluation-system-static
gsutil iam ch allUsers:objectViewer gs://$proj-evaluation-system-static

# terraform保存ファイル格納用バケット作成
create_bucket $proj $region terraform

# API有効化
api_available $proj run.googleapis.com
api_available $proj cloudbuild.googleapis.com
api_available $proj cloudkms.googleapis.com

