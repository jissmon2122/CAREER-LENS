# Google OAuth 2.0 Setup Guide

This guide explains step-by-step how to create and configure a **Google OAuth 2.0 Client ID** in Google Cloud Console for the **AI Career Intelligence Platform**.

---

## 📌 Step 1: Create a Google Cloud Project
1. Go to the [Google Cloud Console](https://console.cloud.google.com/).
2. Log in with your Google account.
3. Click the Project Dropdown at the top bar and select **New Project**.
4. Enter Project Name: `Career-Intelligence-Platform`.
5. Click **Create**.

---

## 📌 Step 2: Configure OAuth Consent Screen
1. In the left navigation menu, go to **APIs & Services** → **OAuth consent screen**.
2. Select User Type: **External** and click **Create**.
3. Fill in App Information:
   - **App name**: `Career Intelligence Platform`
   - **User support email**: Your email address
   - **Developer contact information**: Your email address
4. Click **Save and Continue**.
5. On the **Scopes** page, click **Add or Remove Scopes**:
   - Select `.../auth/userinfo.email`
   - Select `.../auth/userinfo.profile`
   - Select `openid`
6. Click **Update** and then **Save and Continue**.
7. Under **Test users**, add your personal Google email address.
8. Click **Save and Continue**.

---

## 📌 Step 3: Create OAuth 2.0 Client ID
1. In the left navigation menu, go to **APIs & Services** → **Credentials**.
2. Click **+ Create Credentials** at the top and select **OAuth client ID**.
3. Application type: Select **Web application**.
4. Name: `Career Intelligence Web Client`.
5. Under **Authorized JavaScript origins**, click **+ ADD URI** and enter:
   ```text
   http://localhost:5173
   ```
6. Under **Authorized redirect URIs**, click **+ ADD URI** and enter:
   ```text
   http://localhost:5173
   ```
7. Click **Create**.
8. A modal will display your **Client ID** (e.g., `123456789012-abc123xyz.apps.googleusercontent.com`).

---

## 📌 Step 4: Configure Environment Variables

### 1. Frontend Configuration
Open `frontend/.env` and update `VITE_GOOGLE_CLIENT_ID`:

```env
VITE_GOOGLE_CLIENT_ID=123456789012-abc123xyz.apps.googleusercontent.com
VITE_API_BASE_URL=http://localhost:5000/api
```

### 2. Backend Configuration
Open `backend/.env` and update `GOOGLE_CLIENT_ID`:

```env
GOOGLE_CLIENT_ID=123456789012-abc123xyz.apps.googleusercontent.com
```

---

## 📌 Step 5: Test Google Sign-In
1. Restart the backend server (`python run.py`).
2. Restart the frontend server (`npm run dev`).
3. Open `http://localhost:5173/login`.
4. Click **Continue with Google**.
5. Select your Google account and verify redirection to the Candidate Dashboard.
