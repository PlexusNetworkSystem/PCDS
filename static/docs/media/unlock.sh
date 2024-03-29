#Client area
token="2cf24dba5fb0a30e26e83b2ac5b9e29e1b161e5c1fa7425e73043362938b9824"
secretKey="123456"
apiEndpoint="http://cds.test.org/api/$token"
unlcokFile=""
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
            unlcokFile="$2"
            shift # past argument
            shift # past value
            ;;
        --sub)
            subDir="$2"
            shift # past argument
            shift # past value
            ;;
        *)
            # Unknown option
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

if [[ -z "$unlcokFile" ]]; then
    echo -e "You have to set file name!"
    exit 1
fi


jsonData=$(cat <<EOF
{
  "secret_key": "$secretKey",
  "file": "$unlcokFile",
  "subDir": "$subDir",
  "procClass": "unlock"
}
EOF
)

# Send the POST request with the JSON data
curl -X POST "$apiEndpoint" \
     -H "Content-Type: application/json" \
     -d "$jsonData"

#Danger zone
