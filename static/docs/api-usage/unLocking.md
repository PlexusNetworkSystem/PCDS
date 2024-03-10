# How to UNLOCK content 

To unlcok content, you have to send JSON values as `json_data`. Here is an example:

```json
                {
                "secret_key": "<secret_key>",
                "file": "<file_you_want_to_unlock>",
                "procClass": "unlock",
                "subDir": "/",
                }
```

| Parameter  | Description                   | Required | 
|------------|-------------------------------|----------|
| secret_key | Your secret key for access    | Yes      |
| procClass  | The process class to use      | Yes      |
| subDir     | The sub-directory path        | Yes      |

When you set the json parameters, you can set file now.

## Usage

- You can use this `unlock.sh` script codes to test.

**Install:** [unlock.sh](/docs/media/unlock.sh)

> `unlock.sh` run code

```bash
bash unlock.sh --file <filename> --sub <path>
```

| Args       | Description                      | Required | 
|------------|----------------------------------|----------|
| --file     | Set file name to unlock          | Yes      |
| --sub      | Set file directory path on server| Yes      |


