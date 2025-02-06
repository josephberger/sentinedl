# SentinEDL

## Overview
SentinEDL is a Flask-based web application designed to create, manage, and export **External Dynamic Lists (EDLs)** containing **IP addresses, FQDNs, and URLs**. It supports **user authentication, auditing**, and multiple export formats.

---

## Features
✅ **User Authentication:** Secure login/logout system with password hashing.  
✅ **EDL Management:** Create, edit, and delete EDLs.  
✅ **Entry Management:** Add and remove individual entries within an EDL.  
✅ **User Tracking:** Every EDL and entry includes the **admin who created it**.  
✅ **Export Options:** Export an EDL’s contents as **JSON, CSV, or Plain Text**.  
✅ **Access Control:** Only logged-in users can manage lists or export data.  

---

## Installation
### **1️⃣ Clone the Repository**
```sh
git clone https://github.com/your-repo/sentinedl.git
cd sentinedl
```

### **2️⃣ Create and Activate a Virtual Environment**
```sh
python3 -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate
```

### **3️⃣ Install Dependencies**
```sh
pip install -r requirements.txt
```

### **4️⃣ Initialize the Database**
```sh
python init_db.py  # Creates the default admin user
```

### **5️⃣ Run the Application**
```sh
python run.py
```
Application will be available at:  
➡ **http://127.0.0.1:9000**

---

## Usage Guide
### **Login**
1. Open the browser and go to **http://127.0.0.1:9000**.
2. Log in using the default credentials:
   - **Username:** `admin`
   - **Password:** `password`

### **Creating an EDL**
1. Click **"Create a New EDL"**.
2. Enter a **name** (min. 4 characters, alphanumeric only).
3. Enter an optional **description**.
4. Click **"Create EDL"**.

### **Managing Entries**
1. Click on an **EDL** from the homepage.
2. Add a **new entry** (IPv4, IPv6, FQDN, or URL).
3. Remove an entry if needed.

### **Exporting Data**
On the **EDL details page**, you can export an EDL’s contents in various formats:
- **Plain Text**  (PanOS)
- **JSON**  
- **CSV** (removes commas from values)

## Steps to Run SentinEDL with Gunicorn

Install Gunicorn

```sh
pip install gunicorn
```
Run Gunicorn Use the following command to run the app with Gunicorn:

```sh
gunicorn -w 4 -b 0.0.0.0:9000 run:app
```
---

## Security Considerations
- **Passwords are securely hashed** before storage.
- **Only authenticated users** can manage EDLs.
- **Username tracking** ensures logs show who created EDLs and entries.

---

# License

SentinEDL is distributed under the MIT license (see LICENSE file).

**Enjoy using SentinEDL!**