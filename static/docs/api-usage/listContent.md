# How to LIST contents 

Send json values as `json_data`.
Ex:
```json
                {
                "secret_key": "<secret_key>",
                "procClass": "list",
                "subDir": "/"
                }
```
> Content Type: **`application/json`**

---

## Usage

- You can use this `list.sh` script codes to test.

**Install:** [list.sh](/docs/media/list.sh)


> `list.sh` run code

```bash
bash list.sh --sub <path>
```

| Args       | Description                                  | Required | 
|------------|----------------------------------------------|----------|
| --sub      | Set file sub-directory path on server        | No       |
