# CashnGo Backend API Documentation

This document provides comprehensive documentation for the CashnGo Backend API, designed for the frontend developer. It includes all endpoints, request/response formats, authentication requirements, and example cURL commands.

## Table of Contents
- [Authentication](#authentication)
- [Gigs](#gigs)
- [Payments](#payments)
- [Error Handling](#error-handling)

## Base URL
```
Base url will be provided to the frontend dev
```

## Authentication

All API endpoints except signup and login require authentication via JWT token in the `x-access-token` header.

### Signup

**Endpoint:** `POST /api/auth/signup`

**Description:** Register a new user (Student or Employer).

**Request Body:**
```json
{
  "username": "string",
  "email": "string",
  "password": "string",
  "role": "Student" | "Employer",
  "primary_skill": "string" // Required for Students, optional for Employers
}
```

**Success Response (201):**
```json
{
  "message": "User created successfully!",
  "user_id": "string"
}
```

**Error Responses:**
- `400`: Missing required fields or invalid role
- `409`: User with email already exists

**Example cURL:**
```bash
curl -X POST -H "Content-Type: application/json" -d '{
    "username": "studentuser",
    "email": "student@example.com",
    "password": "password123",
    "role": "Student",
    "primary_skill": "Python Programming"
}' http://127.0.0.1:5000/api/auth/signup
```

### Login

**Endpoint:** `POST /api/auth/login`

**Description:** Authenticate user and receive JWT token.

**Request Body:**
```json
{
  "email": "string",
  "password": "string"
}
```

**Success Response (200):**
```json
{
  "token": "jwt_token_string",
  "message": "Logged in successfully!",
  "user": {
    "_id": "string",
    "username": "string",
    "email": "string",
    "role": "Student" | "Employer",
    "primary_skill": "string" | null,
    "badges": ["string"],
    "wallet_balance": 0.0,
    "verification_status": "Verified" | "Unverified"
  }
}
```

**Error Responses:**
- `400`: Missing required fields
- `401`: Invalid email or password

**Example cURL:**
```bash
curl -X POST -H "Content-Type: application/json" -d '{
    "email": "student@example.com",
    "password": "password123"
}' http://127.0.0.1:5000/api/auth/login
```

### Get User Profile

**Endpoint:** `GET /api/auth/profile`

**Description:** Retrieve current user's profile information.

**Headers:**
```
x-access-token: jwt_token
```

**Success Response (200):**
```json
{
  "_id": "string",
  "username": "string",
  "email": "string",
  "role": "Student" | "Employer",
  "primary_skill": "string" | null,
  "badges": ["string"],
  "wallet_balance": 0.0,
  "verification_status": "Verified" | "Unverified"
}
```

**Error Responses:**
- `401`: Token missing, invalid, or expired

**Example cURL:**
```bash
curl -X GET -H "x-access-token: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." http://127.0.0.1:5000/api/auth/profile
```

### Update User Profile

**Endpoint:** `PATCH /api/auth/profile`

**Description:** Update current user's profile information.

**Headers:**
```
x-access-token: jwt_token
Content-Type: application/json
```

**Request Body:** (any combination of fields)
```json
{
  "username": "string",
  "email": "string",
  "role": "Student" | "Employer",
  "primary_skill": "string" // Only for Students
}
```

**Success Response (200):**
```json
{
  "message": "Profile updated successfully.",
  "user": {
    "_id": "string",
    "username": "string",
    "email": "string",
    "role": "Student" | "Employer",
    "primary_skill": "string" | null,
    "badges": ["string"],
    "wallet_balance": 0.0,
    "verification_status": "Verified" | "Unverified"
  }
}
```

**Error Responses:**
- `400`: No data provided or invalid role
- `409`: Email already in use
- `401`: Token missing, invalid, or expired

### Get Any User Profile

**Endpoint:** `GET /api/auth/users/{user_id}`

**Description:** Retrieve any user's profile information.

**Headers:**
```
x-access-token: jwt_token
```

**URL Parameters:**
- `user_id`: The ID of the user to retrieve

**Success Response (200):**
```json
{
  "_id": "string",
  "username": "string",
  "email": "string",
  "role": "Student" | "Employer",
  "primary_skill": "string" | null,
  "badges": ["string"],
  "wallet_balance": 0.0,
  "verification_status": "Verified" | "Unverified"
}
```

**Error Responses:**
- `404`: User not found
- `401`: Token missing, invalid, or expired
- `403`: Insufficient role

### Update Password

**Endpoint:** `PATCH /api/auth/update_password`

**Description:** Update current user's password.

**Headers:**
```
x-access-token: jwt_token
Content-Type: application/json
```

**Request Body:**
```json
{
  "current_password": "string",
  "new_password": "string"
}
```

**Success Response (200):**
```json
{
  "message": "Password updated successfully."
}
```

**Error Responses:**
- `400`: Missing required fields
- `401`: Current password incorrect or token invalid
- `500`: Unexpected error

## Gigs

### Post Gig

**Endpoint:** `POST /api/gigs/`

**Description:** Create a new gig (Employer only).

**Headers:**
```
x-access-token: jwt_token
Content-Type: application/json
```

**Request Body:**
```json
{
  "title": "string",
  "description": "string",
  "price": 0.0,
  "required_skill_tag": "string"
}
```

**Success Response (201):**
```json
{
  "message": "Gig posted successfully!",
  "gig": {
    "_id": "string",
    "title": "string",
    "description": "string",
    "price": 0.0,
    "required_skill_tag": "string",
    "employer_id": "string",
    "status": "POSTED",
    "applied_students": [],
    "claimed_by": null,
    "created_at": "ISO_date_string"
  }
}
```

**Error Responses:**
- `400`: Missing required fields or invalid price
- `401`: Token missing, invalid, or expired
- `403`: Insufficient role (not Employer)

**Example cURL:**
```bash
curl -X POST -H "Content-Type: application/json" -H "x-access-token: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." -d '{
    "title": "Build a Simple Landing Page",
    "description": "Design and develop a responsive landing page using HTML, CSS, and JavaScript.",
    "price": 50.00,
    "required_skill_tag": "Web Development Basics"
}' http://127.0.0.1:5000/api/gigs
```

### Get All Gigs

**Endpoint:** `GET /api/gigs/`

**Description:** Retrieve all gigs with unlock status for current user.

**Headers:**
```
x-access-token: jwt_token
```

**Success Response (200):**
```json
[
  {
    "_id": "string",
    "title": "string",
    "description": "string",
    "price": 0.0,
    "required_skill_tag": "string",
    "employer_id": "string",
    "status": "POSTED" | "ESCROWED" | "PAID",
    "applied_students": ["string"],
    "claimed_by": "string" | null,
    "created_at": "ISO_date_string",
    "is_unlocked": true | false
  }
]
```

**Error Responses:**
- `401`: Token missing, invalid, or expired

**Example cURL:**
```bash
curl -X GET -H "x-access-token: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." http://127.0.0.1:5000/api/gigs
```

### Get Gig Details

**Endpoint:** `GET /api/gigs/{gig_id}`

**Description:** Retrieve details of a specific gig.

**Headers:**
```
x-access-token: jwt_token
```

**URL Parameters:**
- `gig_id`: The ID of the gig to retrieve

**Success Response (200):**
```json
{
  "_id": "string",
  "title": "string",
  "description": "string",
  "price": 0.0,
  "required_skill_tag": "string",
  "employer_id": "string",
  "status": "POSTED" | "ESCROWED" | "PAID",
  "applied_students": ["string"],
  "claimed_by": "string" | null,
  "created_at": "ISO_date_string",
  "is_unlocked": true | false
}
```

**Error Responses:**
- `404`: Gig not found
- `401`: Token missing, invalid, or expired

**Example cURL:**
```bash
curl -X GET -H "x-access-token: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." http://127.0.0.1:5000/api/gigs/68f21cdaebe6ce6858312809
```

### Apply for Gig

**Endpoint:** `POST /api/gigs/{gig_id}/apply`

**Description:** Apply for and claim a gig (Student only). Automatically claims the gig if eligible.

**Headers:**
```
x-access-token: jwt_token
```

**URL Parameters:**
- `gig_id`: The ID of the gig to apply for

**Success Response (200):**
```json
{
  "message": "Successfully applied for and claimed gig!",
  "gig": {
    "_id": "string",
    "title": "string",
    "description": "string",
    "price": 0.0,
    "required_skill_tag": "string",
    "employer_id": "string",
    "status": "ESCROWED",
    "applied_students": ["string"],
    "claimed_by": "string",
    "created_at": "ISO_date_string"
  }
}
```

**Error Responses:**
- `404`: Gig not found
- `403`: Insufficient skill badge or not a Student
- `400`: Gig not available for application
- `409`: Already applied
- `401`: Token missing, invalid, or expired

### Approve Gig Payment

**Endpoint:** `POST /api/gigs/{gig_id}/approve`

**Description:** Approve payment for completed gig (Employer only).

**Headers:**
```
x-access-token: jwt_token
```

**URL Parameters:**
- `gig_id`: The ID of the gig to approve

**Success Response (200):**
```json
{
  "message": "Payment of {price} approved and transferred to {student_username}.",
  "gig": {
    "_id": "string",
    "title": "string",
    "description": "string",
    "price": 0.0,
    "required_skill_tag": "string",
    "employer_id": "string",
    "status": "PAID",
    "applied_students": ["string"],
    "claimed_by": "string",
    "created_at": "ISO_date_string"
  },
  "student_wallet_balance": 0.0
}
```

**Error Responses:**
- `404`: Gig or student not found
- `403`: Not the employer for this gig
- `400`: Gig not in escrowed state or no student claimed
- `401`: Token missing, invalid, or expired

### Generate Skill Quiz

**Endpoint:** `POST /api/gigs/skill-synth/generate-quiz`

**Description:** Generate a quiz to earn a new skill badge (Student only).

**Headers:**
```
x-access-token: jwt_token
Content-Type: application/json
```

**Request Body:**
```json
{
  "target_skill_gap": "string"
}
```

**Success Response (200):**
```json
{
  "quiz_id": "string",
  "skill_name": "string",
  "questions": [
    {
      "question": "string",
      "options": ["string", "string", "string", "string"],
      "correct_answer_index": 0
    }
  ]
}
```

**Error Responses:**
- `400`: Missing primary skill or target_skill_gap
- `500`: AI service error
- `401`: Token missing, invalid, or expired
- `403`: Insufficient role (not Student)

**Example cURL (when AI fails):**
```bash
curl -X POST -H "Content-Type: application/json" -H "x-access-token: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." -d '{
    "target_skill_gap": "Advanced Excel Charting"
}' http://127.0.0.1:5000/api/gigs/skill-synth/generate-quiz
```

### Submit Skill Quiz

**Endpoint:** `POST /api/gigs/skill-synth/submit-quiz`

**Description:** Submit answers for a skill quiz (Student only).

**Headers:**
```
x-access-token: jwt_token
Content-Type: application/json
```

**Request Body:**
```json
{
  "quiz_id": "string",
  "skill_name": "string",
  "answers": [0, 1, 2] // Array of 3 indices
}
```

**Success Response (200) - Passed:**
```json
{
  "message": "Quiz submitted successfully! You have earned the {skill_name} badge.",
  "badges": ["string"]
}
```

**Success Response (200) - Failed:**
```json
{
  "message": "Quiz failed. You did not earn the badge. Try again."
}
```

**Error Responses:**
- `400`: Missing required fields or invalid answers format
- `404`: Quiz not found
- `403`: Not authorized to submit this quiz
- `401`: Token missing, invalid, or expired

**Example cURL:**
```bash
curl -X POST -H "Content-Type: application/json" -H "x-access-token: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." -d '{
    "quiz_id": "mock_quiz_123",
    "skill_name": "Advanced Excel Charting",
    "answers": [0, 2, 1]
}' http://127.0.0.1:5000/api/gigs/skill-synth/submit-quiz
```

## Payments

### Get Wallet Balance

**Endpoint:** `GET /api/payments/wallet`

**Description:** Retrieve current user's wallet balance.

**Headers:**
```
x-access-token: jwt_token
```

**Success Response (200):**
```json
{
  "user_id": "string",
  "username": "string",
  "wallet_balance": 0.0
}
```

**Error Responses:**
- `401`: Token missing, invalid, or expired
- `403`: Insufficient role

## Error Handling

The API uses standard HTTP status codes and returns error messages in JSON format:

```json
{
  "message": "Error description"
}
```

Common error codes:
- `400`: Bad Request - Invalid input data
- `401`: Unauthorized - Authentication required or invalid token
- `403`: Forbidden - Insufficient permissions
- `404`: Not Found - Resource not found
- `409`: Conflict - Resource already exists or state conflict
- `500`: Internal Server Error - Unexpected server error

## Frontend Integration Notes

1. **Authentication**: Store the JWT token securely (e.g., in localStorage or secure cookies) and include it in the `x-access-token` header for authenticated requests.

2. **Error Handling**: Always check response status and handle errors appropriately in your React components.

3. **State Management**: Consider using React state or a state management library (like Redux or Context API) to manage user authentication state and API responses.

4. **API Calls**: Use `fetch` or libraries like `axios` for making HTTP requests. Example:

```javascript
const response = await fetch('/api/auth/profile', {
  headers: {
    'x-access-token': token
  }
});
const data = await response.json();
```

5. **File Uploads**: If implementing file uploads in the future, use `FormData` for multipart requests.

6. **Real-time Updates**: For features requiring real-time updates (e.g., gig status changes), consider implementing WebSocket connections or polling mechanisms.

7. **Validation**: Validate user input on the frontend before sending requests to match backend validation rules.

8. **Loading States**: Implement loading indicators for better user experience during API calls.

9. **Token Refresh**: Implement token refresh logic(redirect to login page) if tokens expire during user sessions.

10. **Environment Variables**: Use environment variables for API base URLs to easily switch between development and production environments.