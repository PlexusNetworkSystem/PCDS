
#Client area
token="2cf24dba5fb0a30e26e83b2ac5b9e29e1b161e5c1fa7425e73043362938b9824"
secretKey="123456"
apiEndpoint="http://cds.plexusteam.org/api/$token"
requestFile=""
savePath=""
subDir="/"
outputFile=""
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
            requestFile="$2"
            shift # past argument
            shift # past value
            ;;
        --sub)
            subDir="$2"
            shift # past argument
            shift # past value
            ;;
        --save)
            savePath="${2%/*}"
            outputFile="${2##*/}"
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

if [[ -z "$requestFile" ]]; then
    echo -e "You have to set file name!"
    exit 1
fi

if [[ -z "$savePath" ]]; then
    savePath="$(pwd)"
fi

if [[ -z "$outputFile" ]]; then
    outputFile="$requestFile"
fi



# Create a temporary JSON file with the required data
json_data=$(cat <<EOF
{
  "secret_key": "$secretKey",
  "file": "$requestFile",
  "subDir": "$subDir",
  "procClass": "download"
}
EOF
)
temp_json_file=$(mktemp)
echo "$json_data" > "$temp_json_file"

# Send the file with the temporary JSON file
curl -X POST -H "Content-Type: multipart/form-data" -F "json_data=@$temp_json_file" $apiEndpoint --output "$savePath/$outputFile" &> /dev/null
# Check if the file exists
if ! [[ -f "$savePath/$outputFile" ]] || [[ $(strings "$savePath/$outputFile") =~ ('ERROR'|'Invalid'|'Not Found'|'404'|'message') ]]; then
    cat "$savePath/$outputFile"
    rm "$savePath/$outputFile"
    exit 1
else
    echo -e "\033[32mFile saved as $outputFile to $savePath\033[0m"
fi  
#Danger zone
