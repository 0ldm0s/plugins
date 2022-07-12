#!/bin/sh
echo "input a domain: "
read -r domain
if [ -z "${domain}" ]; then
  echo "you have not input a domain!"
  exit
fi
openssl genrsa -out "dkim.${domain}.pem" 1024
openssl rsa -in "dkim.${domain}.pem" -out "dkim.${domain}.pub" -pubout
echo "set this to you dns:"
cat "dkim.${domain}.pub"