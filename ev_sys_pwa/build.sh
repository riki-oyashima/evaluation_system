#!/bin/bash

# 引数表示
getops_help(){
  echo "-l : Run the build on your local machine."
  exit 1
}

# 引数確認
local=0
while getopts "lh" opts
do
  case $opts in
    l)
      local=1
      ;;
    h)
      getops_help
      ;;
    \?)
      getops_help
      ;;
  esac
done

CURRENT=$(cd $(dirname $0); pwd)
cd ${CURRENT}

# バージョン取得
version=`cat ../version.txt`

# プロジェクト選択
proj=`cat ../project.txt`

# Docker Image取り込み用サービスアカウントキー取得
gsutil cp -rp gs://${proj}-sa-master/service.json .

# DebugモードをFalseに設定
#debug_before=`grep -e "^DEBUG\s*=" api/settings.py`
#sed -i -e "s/^DEBUG\s*=.*/DEBUG = False/g" api/settings.py

# build実行
image_name="asia.gcr.io/${proj}/evaluation-system-server"
if [ $local -eq 1 ]; then
  docker build -t ${image_name}:latest .
else
  gcloud builds submit --tag asia.gcr.io/${proj}/evaluation-system-server --project ${proj}
  if [ "$?" -eq 0 ]; then
    gcloud container images add-tag asia.gcr.io/${proj}/evaluation-system-server:latest asia.gcr.io/${proj}/evaluation-system-server:${version} -q
  fi
fi

# サービスアカウントキー削除
rm -rf service.json

# Debugモードを変更前の値に巻き戻し
#sed -i -e "s/^DEBUG\s*=.*/${debug_before}/g" api/settings.py

