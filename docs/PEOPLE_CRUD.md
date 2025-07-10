# People CRUD API Documentation

## Overview

The People CRUD API provides comprehensive functionality for managing personal identity information. The system uses UUID fields for all ID references and includes extensive search and filtering capabilities.

## Features

- ✅ **Full CRUD Operations**: Create, Read, Update, Delete people records
- ✅ **UUID-based IDs**: All IDs use UUID format for better security and scalability
- ✅ **Advanced Search**: Search by name, citizenship identity, and multiple criteria
- ✅ **Flexible Filtering**: Filter by gender, religion, citizenship, marital status, etc.
- ✅ **Statistics**: Get demographic statistics and distributions
- ✅ **Audit Trail**: Track who created, updated, or deleted records
- ✅ **Data Validation**: Comprehensive validation with check constraints
- ✅ **Soft Delete**: Records are soft deleted (marked as deleted) rather than hard deleted

## Database Schema

### People Table Structure

| Field | Type | Description | Constraints |
|-------|------|-------------|-------------|
| `id` | UUID | Primary key | Auto-generated UUID |
| `full_name` | VARCHAR(255) | Full name | Required |
| `place_of_birth` | VARCHAR(255) | Place of birth | Optional |
| `date_of_birth` | DATE | Date of birth | Optional |
| `gender` | VARCHAR(30) | Gender | MALE, FEMALE, UNDEFINED |
| `religion` | VARCHAR(30) | Religion | HINDU, BUDDHA, MUSLIM, CHRISTIAN, CATHOLIC, CONFUCIUS, UNDEFINED |
| `citizenship_identity` | VARCHAR(255) | Citizenship identity number | Required, Unique |
| `citizenship` | VARCHAR(30) | Citizenship type | Various Indonesian citizenship types |
| `nationality` | VARCHAR(255) | Nationality | Default: UNDEFINED |
| `ethnicity` | VARCHAR(255) | Ethnicity | Optional |
| `marital_status` | VARCHAR(30) | Marital status | Various marital statuses |
| `disability_status` | INTEGER | Disability status | > 0 |
| `blood_type` | VARCHAR(255) | Blood type | Optional |
| `job` | VARCHAR(255) | Job/profession | Optional |
| `created_by` | UUID | User who created the record | Foreign key to users.id |
| `updated_by` | UUID | User who last updated the record | Foreign key to users.id |
| `deleted_by` | UUID | User who deleted the record | Foreign key to users.id |
| `created_at` | TIMESTAMP | Creation timestamp | Auto-generated |
| `updated_at` | TIMESTAMP | Last update timestamp | Auto-updated |
| `deleted_at` | TIMESTAMP | Deletion timestamp | Soft delete |

## API Endpoints

### 1. Create Person

**POST** `/people/`

Create a new person record.

**Request Body:**
```json
{
  "full_name": "John Doe",
  "place_of_birth": "Jakarta",
  "date_of_birth": "1990-05-15",
  "gender": "MALE",
  "religion": "MUSLIM",
  "citizenship_identity": "1234567890123456",
  "citizenship": "INDONESIAN_CITIZEN",
  "nationality": "Indonesian",
  "ethnicity": "Javanese",
  "marital_status": "SINGLE",
  "disability_status": 0,
  "blood_type": "O+",
  "job": "Software Engineer"
}
```

**Query Parameters:**
- `user_id` (optional): UUID of the user creating the record

**Response:**
```json
{
  "status": "success",
  "message": "Person created successfully",
  "data": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "full_name": "John Doe",
    "place_of_birth": "Jakarta",
    "date_of_birth": "1990-05-15",
    "gender": "MALE",
    "religion": "MUSLIM",
    "citizenship_identity": "1234567890123456",
    "citizenship": "INDONESIAN_CITIZEN",
    "nationality": "Indonesian",
    "ethnicity": "Javanese",
    "marital_status": "SINGLE",
    "disability_status": 0,
    "blood_type": "O+",
    "job": "Software Engineer",
    "created_by": "user-uuid-here",
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z"
  }
}
```

### 2. Get Person by ID

**GET** `/people/{person_id}`

Retrieve a person by their UUID.

**Path Parameters:**
- `person_id`: UUID of the person

**Response:**
```json
{
  "status": "success",
  "data": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "full_name": "John Doe",
    // ... all person fields
  }
}
```

### 3. Get All People (with filtering)

**GET** `/people/`

Get people with optional filtering and pagination.

**Query Parameters:**
- `skip` (optional): Number of records to skip (default: 0)
- `limit` (optional): Maximum number of records (default: 100)
- `name` (optional): Filter by name (partial match)
- `gender` (optional): Filter by gender
- `religion` (optional): Filter by religion
- `citizenship` (optional): Filter by citizenship type
- `marital_status` (optional): Filter by marital status
- `nationality` (optional): Filter by nationality
- `ethnicity` (optional): Filter by ethnicity
- `job` (optional): Filter by job/profession
- `blood_type` (optional): Filter by blood type
- `place_of_birth` (optional): Filter by place of birth

**Response:**
```json
{
  "status": "success",
  "count": 2,
  "data": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "full_name": "John Doe",
      // ... person fields
    },
    {
      "id": "660e8400-e29b-41d4-a716-446655440000",
      "full_name": "Jane Smith",
      // ... person fields
    }
  ]
}
```

### 4. Update Person

**PUT** `/people/{person_id}`

Update an existing person record.

**Path Parameters:**
- `person_id`: UUID of the person to update

**Request Body:**
```json
{
  "job": "Senior Software Engineer",
  "marital_status": "MARRIED",
  "blood_type": "O+"
}
```

**Query Parameters:**
- `user_id` (optional): UUID of the user updating the record

**Response:**
```json
{
  "status": "success",
  "message": "Person updated successfully",
  "data": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "full_name": "John Doe",
    "job": "Senior Software Engineer",
    "marital_status": "MARRIED",
    "blood_type": "O+",
    "updated_by": "user-uuid-here",
    "updated_at": "2024-01-01T12:00:00Z"
    // ... other fields
  }
}
```

### 5. Delete Person

**DELETE** `/people/{person_id}`

Soft delete a person record.

**Path Parameters:**
- `person_id`: UUID of the person to delete

**Query Parameters:**
- `user_id` (optional): UUID of the user deleting the record

**Response:**
```json
{
  "status": "success",
  "message": "Person deleted successfully"
}
```

### 6. Search People

**GET** `/people/search/{search_term}`

Search people by name or citizenship identity.

**Path Parameters:**
- `search_term`: Search term to match against names or citizenship identity

**Query Parameters:**
- `skip` (optional): Number of records to skip (default: 0)
- `limit` (optional): Maximum number of records (default: 100)

**Response:**
```json
{
  "status": "success",
  "search_term": "John",
  "count": 1,
  "data": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "full_name": "John Doe",
      "citizenship_identity": "1234567890123456"
      // ... other fields
    }
  ]
}
```

### 7. Get Person by Citizenship Identity

**GET** `/people/citizenship/{citizenship_identity}`

Get a person by their citizenship identity number.

**Path Parameters:**
- `citizenship_identity`: Citizenship identity number

**Response:**
```json
{
  "status": "success",
  "data": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "full_name": "John Doe",
    "citizenship_identity": "1234567890123456",
    "citizenship": "INDONESIAN_CITIZEN"
    // ... other fields
  }
}
```

### 8. Get People Statistics

**GET** `/people/statistics/`

Get demographic statistics and distributions.

**Response:**
```json
{
  "status": "success",
  "data": {
    "total_count": 150,
    "gender_distribution": {
      "MALE": 75,
      "FEMALE": 70,
      "UNDEFINED": 5
    },
    "religion_distribution": {
      "MUSLIM": 80,
      "CHRISTIAN": 30,
      "HINDU": 20,
      "BUDDHA": 15,
      "CATHOLIC": 5
    },
    "citizenship_distribution": {
      "INDONESIAN_CITIZEN": 145,
      "INDONESIAN_DESCENT_CITIZEN": 5
    },
    "marital_status_distribution": {
      "SINGLE": 60,
      "MARRIED": 80,
      "DIVORCED": 10
    }
  }
}
```

## Data Validation

### Gender Values
- `MALE`
- `FEMALE`
- `UNDEFINED`

### Religion Values
- `HINDU`
- `BUDDHA`
- `MUSLIM`
- `CHRISTIAN`
- `CATHOLIC`
- `CONFUCIUS`
- `UNDEFINED`

### Citizenship Values
- `INDONESIAN_CITIZEN`
- `INDONESIAN_DESCENT_CITIZEN`
- `ORIGINAL_INDONESIAN_CITIZEN`
- `DUAL_INDONESIAN_CITIZEN`
- `STATELESS_INDONESIAN_CITIZEN`
- `UNDEFINED`

### Marital Status Values
- `SINGLE`
- `MARRIED`
- `DIVORCED`
- `SEPARATED`
- `WIDOWED`
- `ANNULLED`
- `CIVIL_DOMESTIC_PARTNERSHIP`
- `COMMON_LOW_MARRIAGE`
- `ENGAGED`
- `COMPLICATED`
- `UNDEFINED`

## Error Handling

The API returns appropriate HTTP status codes:

- `200 OK`: Successful operation
- `400 Bad Request`: Invalid input data or UUID format
- `404 Not Found`: Person not found
- `500 Internal Server Error`: Server error

Error responses include a detail message:

```json
{
  "detail": "Person not found"
}
```

## Usage Examples

### Python Example

```python
import requests
import json

# Create a person
person_data = {
    "full_name": "John Doe",
    "place_of_birth": "Jakarta",
    "date_of_birth": "1990-05-15",
    "gender": "MALE",
    "religion": "MUSLIM",
    "citizenship_identity": "1234567890123456",
    "citizenship": "INDONESIAN_CITIZEN",
    "nationality": "Indonesian",
    "ethnicity": "Javanese",
    "marital_status": "SINGLE",
    "disability_status": 0,
    "blood_type": "O+",
    "job": "Software Engineer"
}

response = requests.post(
    "http://localhost:8000/people/",
    json=person_data,
    params={"user_id": "user-uuid-here"}
)

if response.status_code == 200:
    person = response.json()["data"]
    print(f"Created person: {person['full_name']}")
```

### cURL Example

```bash
# Create a person
curl -X POST "http://localhost:8000/people/" \
  -H "Content-Type: application/json" \
  -d '{
    "full_name": "John Doe",
    "citizenship_identity": "1234567890123456",
    "gender": "MALE",
    "religion": "MUSLIM"
  }'

# Get person by ID
curl "http://localhost:8000/people/550e8400-e29b-41d4-a716-446655440000"

# Search people
curl "http://localhost:8000/people/?gender=MALE&religion=MUSLIM"

# Get statistics
curl "http://localhost:8000/people/statistics/"
```

## Testing

Run the test script to verify the People CRUD functionality:

```bash
python test_people_crud.py
```

This will test all CRUD operations with sample data.

## Database Migration

To create the People table, run the migration:

```bash
poetry run alembic upgrade head
```

This will create the `people` table with all necessary constraints and indexes.

## Security Considerations

- All IDs use UUID format for better security
- Audit trail tracks who created, updated, or deleted records
- Soft delete prevents data loss
- Input validation prevents invalid data
- Foreign key constraints maintain data integrity 