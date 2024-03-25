# How to UPLOAD content 

To upload content, you have to send JSON values as `json_data`. Here is an example:

```json
                {
                "secret_key": "<secret_key>",
                "procClass": "upload",
                "subDir": "/",
                "force": "<true/false>"
                }
```

> Content Type: **`multipart/form-data`**


| Parameter  | Description                   | Required | 
|------------|-------------------------------|----------|
| secret_key | Your secret key for access    | Yes      |
| procClass  | The process class to use      | Yes      |
| force      | Change same file on server    | no       |
| subDir     | The sub-directory path        | No       |

When you set the json parameters, you can set file now.

## Usage

- You can use this `upload.sh` script codes to test.

**Install:** [upload.sh](/docs/media/upload.sh)

> `upload.sh` run code

```bash
bash upload.sh --file <filename> --sub <path> --force <true/false>
```

| Args       | Description                      | Required | 
|------------|----------------------------------|----------|
| --file     | Set file name to upload          | Yes      |
| --sub      | Set file save directory on server| No       |
| --force    | Set file change status           | No       |


