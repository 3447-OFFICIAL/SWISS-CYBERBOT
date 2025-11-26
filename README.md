
# Swiss CyberBot – Project Guide

Swiss CyberBot delivers an integrated conversational interface for accessing Swiss cybersecurity regulations, circulars, and threat intelligence. The platform aligns a Python Flask service with a Dialogflow ES agent, enabling a streamlined, scalable, and cloud-ready interaction model.

---

## 📁 Project Structure

```

SwissCyberBot/
│
├── dialogflow_webhook.py      # Primary backend service (Flask)
├── intents.json               # Dialogflow intent reference configuration
└── README.md

````

---

## 🛠️ Step 1: Local Backend Setup

### ✅ Install Dependencies

Ensure Python and pip are configured, then execute:

```bash
pip install flask requests beautifulsoup4 google-generativeai
````

### ✅ Start the Server

```bash
python dialogflow_webhook.py
```

**Expected Output:**

```
 Running on http://127.0.0.1:5000
```

This confirms that the backend service is operational.

---

### 🌐 Expose to Internet (ngrok)

Open a second terminal and run:

```bash
ngrok http 5000
```

Copy the HTTPS URL generated, such as:

```
https://1234abcd.ngrok-free.app
```

---

## 🤖 Step 2: Dialogflow Configuration

1. Access the Dialogflow Console
2. Create an agent named:

```
SwissCyberBot
```

3. Enable webhook functionality:

   * Navigate to **Fulfillment**
   * Toggle **Webhook** to *Enabled*
   * Paste the ngrok URL followed by:

```
/webhook
```

Example:

```
https://1234abcd.ngrok-free.app/webhook
```

4. Click **Save**

---

## 🧠 Step 3: Intent Setup (Manual)

Use `intents.json` as the reference blueprint.

| Intent Name            | Training Phrase Examples                             | Fulfillment |
| ---------------------- | ---------------------------------------------------- | ----------- |
| AskQuestion            | "What is FADP?", "Report incident", "Latest threats" | Webhook     |
| GetCirculars           | "Download PDFs", "Get reports", "Compliance docs"    | Webhook     |
| Default Welcome Intent | "Hi", "Hello"                                        | Webhook     |

> **Important:**
> For each intent, scroll to the bottom of the intent configuration page and check:

```
Enable webhook call for this intent
```

---

## ✅ Step 4: Testing

Use the **Try it now** panel in Dialogflow.

### Expected Results

Query:

```
What is the NCSC?
```

Outcome:

* AI-generated definition response

Query:

```
Get circulars
```

Outcome:

* List of PDF regulatory documents

---

## 🚀 Value Proposition

This architecture enables:

* Modular backend orchestration
* Cloud-ready conversational engagement
* AI-driven regulatory intelligence delivery
* Rapid deployment capability

---

## 📌 Optional Enhancements

* Database integration
* Authentication and access control
* Multi-language support
* Cloud deployment (Render / AWS / GCP)

---





