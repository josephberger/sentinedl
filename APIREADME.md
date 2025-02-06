# SentinEDL API Documentation

## Overview
The SentinEDL API is a RESTful service for managing External Dynamic Lists (EDLs). It supports authentication via JWT tokens and provides endpoints to create, retrieve, update, and delete EDLs and their entries.

## Base URL
```
http://127.0.0.1:9000/api
```

## Authentication
The API requires authentication for creating, deleting, and modifying EDLs and entries. Authentication is handled via JWT tokens.

### **Login & Obtain Token**
```
POST /auth/api/login
```
#### **Request Body:**
```json
{
    "username": "admin",
    "password": "password"
}
```
#### **Response:**
```json
{
    "access_token": "your_jwt_token_here"
}
```

Use this token in the `Authorization` header for requests requiring authentication:
```
-H "Authorization: Bearer <TOKEN>"
```

## EDL Management
### **List All EDLs**
```
GET /edls
```
#### **Response:**
```json
[
    {"name": "test_edl", "description": "My test list"},
    {"name": "malicious_ips", "description": "Blacklist for bad actors"}
]
```

### **Create a New EDL** (🔒 Requires Token)
```
POST /edls
```
#### **Request Body:**
```json
{
    "name": "testEDL",
    "description": "Valid description"
}
```
#### **Response:**
```json
{
    "message": "EDL created successfully!",
    "name": "testEDL"
}
```

### **Get a Specific EDL**
```
GET /edls/{edl_name}
```
#### **Response:**
```json
{
    "name": "testEDL",
    "description": "Valid description"
}
```

### **Delete an EDL** (🔒 Requires Token)
```
DELETE /edls/{edl_name}
```
#### **Response:**
```json
{
    "message": "EDL 'testEDL' deleted successfully"
}
```

## Entry Management
### **Get All Entries in an EDL**
```
GET /edls/{edl_name}/entries
```
#### **Response:**
```json
[
    {"id": 1, "value": "1.1.1.1", "description": "Cloudflare DNS", "created_at": "2025-02-05 14:32:10"},
    {"id": 2, "value": "example.com", "description": "Test domain", "created_at": "2025-02-05 14:35:45"}
]
```

### **Add an Entry to an EDL** (🔒 Requires Token)
```
POST /edls/{edl_name}/entries
```
#### **Request Body:**
```json
{
    "value": "1.1.1.1",
    "description": "Cloudflare DNS"
}
```
#### **Response:**
```json
{
    "message": "Entry added successfully!",
    "value": "1.1.1.1"
}
```

### **Delete an Entry** (🔒 Requires Token)
```
DELETE /entries/{entry_id}
```
#### **Response:**
```json
{
    "message": "Entry deleted successfully!"
}
```

## Error Handling
If an invalid request is made, the API returns an error message with an appropriate status code:
#### **Example Error Response:**
```json
{
    "error": "EDL name must be at least 4 characters long."
}
```

## Authentication Summary
| API Endpoint                         | Method  | Requires JWT Token? |
|--------------------------------------|---------|--------------------|
| `/auth/api/login`                     | POST    | No |
| `/edls`                               | GET     | No |
| `/edls`                               | POST    | Yes |
| `/edls/{edl_name}`                    | GET     | No |
| `/edls/{edl_name}`                    | DELETE  | Yes |
| `/edls/{edl_name}/entries`            | GET     | No |
| `/edls/{edl_name}/entries`            | POST    | Yes |
| `/entries/{entry_id}`                  | DELETE  | Yes |

🚀 **Enjoy using the SentinEDL API!**

