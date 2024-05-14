# Google Drive Tools

Script collection for using google drive api.

## Clone

This script clones an google drive folder to hard drive and can be used e.g. for build pipelines. 

Works only with authenticated google service accounts.

### Preperations

1. Register a google developer account
2. Create an service account
3. Add the service account to google drive
4. Download Service account auth data (json)

### Usage

1. Configure in a folder the source folder(you can extract it from google drive share link option):
   ```
   {
    "sourceFolder":"aaaaaaaa" 
   }
   ```
2. Configure in ENV as base64 object the service account json(optional under tmp/google_service_account.json)
```
  {
    "type": "service_account",
    "project_id": "my id",
    "private_key_id": "xyyyyy",
    "private_key": "-----BEGIN PRIVATE KEY-----mmmmmmmmmmmmmmmmmJ\n-----END PRIVATE KEY-----\n",
    "client_email": "myone.iam.gserviceaccount.com",
    "client_id": "2828222",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/myone.iam.gserviceaccount.com",
    "universe_domain": "googleapis.com"
  }
```
3. Run the script, content will be placed under "content"


### Flags

- cF : changes the config folder location
- sAF: changes the service account file location
