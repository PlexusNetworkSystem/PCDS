# PCDS API Structure and Functioning

The **PCDS API** is based on the [JSON](/docs/api-usage/WhatIsJson) format to organize interactions and ensure successful communication. Three basic values are required to use the API:

- **API Token**: The API token is a special identifier for authentication of requests. This token is used to verify that the user is authorized and the request is valid.

- **Secret Key**: The secret key is an important element used to secure communication and encrypt data. API requests and responses are securely transmitted through this secret key.

- **Class**: The process class specifies the type of operation the user wants to do.

- **Content**: The content in requests specifies the type of resource the user is requesting. This resource can encompass various types of content, such as images, documents or text.

- **Locking**: When you call a content, it is decrypting on server side and locking for one more time requests. For using content again you have to unlock request blocking with encrypting content.
[unlock.sh](/docs/media/unlock.sh) | [usage documentation](/docs/api-usage/unLocking)

- **Hash check**: If you want to get contents hash value you have to use 'hash' class. 
[hash.sh](/docs/media/hash.sh) | [usage documentation](/docs/api-usage/hashContent)

The API provides data in JSON format for text-based responses. If file-based responses are required, the API optionally delivers the content as a file. If the content is not available, it provides an error response in JSON format even in case of error.

This structure is intended to ensure a secure, consistent and user-friendly interaction with the PCDS API. The API token and secret key provide secure authentication and communication encryption, while the content parameter allows users to specify their requests in a specific way. Responses in JSON format standardize data exchange and increase compatibility between systems.

## JSON Struct

```bash
                {
                "secret_key": "$secretKey",
                "procClass": "download",
                "file": "<path:file / null>"
                }
```

When the `download` procClass is called with an empty `file` value, it will perform a `ping-pong` operation, as demonstrated in the `ping.sh` example:

**Install:** [ping.sh](/docs/media/ping.sh)

We'll get this response:


```json
                {
                "Api token": "2cf24dba5fb0a30e26e83b2ac5b9e29e1b161e5c1fa7425e73043362938b9824",
                "Secret key": "123456",
                "message": "PCDS API Ping Request Success!"
                }
```

---

