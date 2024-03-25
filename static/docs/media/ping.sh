
#Client area
token="2cf24dba5fb0a30e26e83b2ac5b9e29e1b161e5c1fa7425e73043362938b9824"
secretKey="123456"
apiEndpoint="http://cds.plexusteam.org/api/$token"
#Client area

#Danger zone
# Check connection with the server
ping -c 1 cds.plexusteam.org > /dev/null 2>&1
if [ $? -ne 0 ]; then
    echo -e "Failed to connect to the server."
    exit 1
fi

# Create a temporary JSON file with the required data
jsonData=$(cat <<EOF
{
  "secret_key": "$secretKey",
  "file": "",
  "procClass": "download"
}
EOF
)

# Send the POST request with the JSON data
curl -X POST "$apiEndpoint" \
     -H "Content-Type: application/json" \
     -d "$jsonData"

#Danger zone

