 echo "magicpigdocker/otmoic-lpnode-exchange-adapter:v$1"

 docker buildx  build --platform linux/amd64  . -t  magicpigdocker/otmoic-lpnode-exchange-adapter:v$1 -f Dockerfile
 docker push magicpigdocker/otmoic-lpnode-exchange-adapter:v$1