# How to DELETE content

Send json values as `json_data`.
Ex:
```json
                {
                "secret_key": "<secret_key>",
                "file": "<file_you_want_to_delete>",
                "subDir": "/",
                "procClass": "delete"
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

- You can use this `delete.sh` script codes to test.

**Install:** [delete.sh](/docs/media/delete.sh)


> `delete.sh` run code

```bash
bash delete.sh --file <filename> --sub <path>
```
| Args       | Description                                  | Required | 
|------------|----------------------------------------------|----------|
| --file     | Set file name to download                    | Yes      |
| --sub      | Set file sub-directory path on server        | No       |
