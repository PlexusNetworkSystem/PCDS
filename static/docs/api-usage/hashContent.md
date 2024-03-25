# How to get HASH of a content 

Send json values as `json_data`.
Ex:
```json
                {
                "secret_key": "<secret_key>",
                "procClass": "hash",
                "subDir": "/",
                "file": "<file>"
                }
```
> Content Type: **`application/json`**

---

## Usage

- You can use this `hash.sh` script codes to test.

**Install:** [hash.sh](/docs/media/hash.sh)


> `hash.sh` run code

```bash
bash hash.sh --sub <path> --file <path>
```

| Args       | Description                                  | Required | 
|------------|----------------------------------------------|----------|
| --file     | Set file you want to get hash                | Yes      |
| --sub      | Set file sub-directory path on server        | No       |
