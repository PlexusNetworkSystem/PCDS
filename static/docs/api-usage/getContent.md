# How to GET content 

Send json values as `json_data`.

```json
                {
                "secret_key": "<secret_key>",
                "procClass": "download",
                "file": "<file_you_want_to_get>",
                "subDir": "/"
                }
```
> Content Type: **`application/json`**

| Parameter  | Description                   | Required | 
|------------|-------------------------------|----------|
| secret_key | Your secret key for access    | Yes      |
| procClass  | The process class to use      | Yes      |
| file       | The name of the file to get   | Yes      |
| subDir     | The sub-directory path        | No       |

---

## Usage

- You can use this `request.sh` script codes to test.

**Install:** [request.sh](/docs/media/request.sh)


> `request.sh` run code

```bash
bash request.sh --file <filename> --sub <path> --save <path>
```

| Args       | Description                      | Required | 
|------------|----------------------------------|----------|
| --file     | Set file name to download        | Yes      |
| --sub      | Set file sub-directory path on server        | Yes      |
| --save     | Set download path                | No       |
