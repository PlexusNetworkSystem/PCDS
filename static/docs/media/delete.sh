
#Client area
token="2cf24dba5fb0a30e26e83b2ac5b9e29e1b161e5c1fa7425e73043362938b9824"
secretKey="123456"
apiEndpoint="http://cds.plexusteam.org/api/$token"
deleteFile=""
subDir="/"
#Client area
# Check connection with the server
ping -c 1 cds.plexusteam.org > /dev/null 2>&1
if [ $? -ne 0 ]; then
    echo -e "Failed to connect to the server."
    exit 1
fi
#Danger zone
# Parse command line arguments
 while [[ $# -gt 0 ]]; do
     key="$1"

     case $key in
         --file)
             deleteFile="$2"
             shift
             ;;
        --sub)
             subDir="$2"
             shift
             ;;
         *)
             # Unknown option
             echo "Unknown option: $1"
             exit 1
             ;;
     esac
     shift
 done

[[ -z "$deleteFile" ]]  && echo -e "You have to set file name!" && exit 1

# Create a temporary JSON file with the required data
json_data=$(cat <<EOF
{
  "secret_key": "$secretKey",
  "file": "$deleteFile",
  "subDir": "$subDir",
  "procClass": "delete"
}
EOF
)
temp_json_file=$(mktemp)
echo "$json_data" > "$temp_json_file"

# Send the file with the temporary JSON file
curl -X POST -H "Content-Type: multipart/form-data" -F "json_data=@$temp_json_file" $apiEndpoint
#Danger zone

