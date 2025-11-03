# Firebase Setup for FitConnect

Follow these steps to configure Firebase for the `fitconnect-{ENV}` environment (e.g., `fitconnect-dev`).

### Create Firebase Project

- Go to [Firebase Console](https://console.firebase.google.com/)
- Create a new project named: `fitconnect-{ENV}`

### Configure Admin SDK for Server-side Access

- Go to Project Settings > Service accounts
- Under Firebase Admin SDK, select Python
- Click **Generate new private key**
- Save the JSON and set it as an environment variable in `.env`:

```bash
FIREBASE_SERVICE_ACCOUNT_JSON='{ "type": "service_account", "project_id": "fitconnect-xxxx", "private_key_id": "xxxx", "private_key": "xxxx", "client_email": "xxxx@fitconnect-xxxx.iam.gserviceaccount.com", "client_id": "xxxx", "auth_uri": "https://accounts.google.com/o/oauth2/auth", "token_uri": "https://oauth2.googleapis.com/token", "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs", "client_x509_cert_url": "xxxx", "universe_domain": "googleapis.com" }'
```

> ⚠️ Make sure the JSON is compact and no line breaks inside the value.

### Register Web App

- In Firebase Console, go to Project Settings > General
- Scroll to Your apps > Click “</>” (Web) to add a web app
- Set App nickname: `Demo` (Do not enable Firebase Hosting)
- Select **Use a \<script\> tag**
- Copy the `firebaseConfig` object and set it in `.env`:

```bash
FIREBASE_DEMO_WEB_CONFIG_JSON='{ "apiKey": "xxxx", "authDomain": "fitconnect-xxxx.firebaseapp.com", "projectId": "fitconnect-xxxx", "storageBucket": "fitconnect-xxxx.firebasestorage.app", "messagingSenderId": "xxxx", "appId": "xxxx", "measurementId": "xxxx" }'
```

### Configure Web Push Notifications

- In Firebase Console, go to Project Settings > Cloud Messaging
- Scroll to Web Push certificates
- Click **Generate Key Pair**
- Copy the Public Key and add to `.env`

```bash
FIREBASE_DEMO_WEB_VAPID_KEY=xxxx
```
