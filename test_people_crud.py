#!/usr/bin/env python3
"""
Test script for People CRUD functionality
"""
import requests
import json
from datetime import date
from uuid import uuid4

# API base URL
BASE_URL = "http://localhost:8000"

def test_people_crud():
    """Test People CRUD operations"""
    
    print("🧪 Testing People CRUD Operations")
    print("=" * 50)
    
    # Sample user ID for testing
    test_user_id = str(uuid4())
    
    # Test data for creating a person
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
    
    print("\n1. Creating a new person...")
    try:
        response = requests.post(
            f"{BASE_URL}/people/",
            json=person_data,
            params={"user_id": test_user_id}
        )
        
        if response.status_code == 200:
            result = response.json()
            person_id = result["data"]["id"]
            print(f"✅ Person created successfully with ID: {person_id}")
            print(f"   Name: {result['data']['full_name']}")
            print(f"   Citizenship ID: {result['data']['citizenship_identity']}")
        else:
            print(f"❌ Failed to create person: {response.text}")
            return
    except Exception as e:
        print(f"❌ Error creating person: {e}")
        return
    
    print("\n2. Getting person by ID...")
    try:
        response = requests.get(f"{BASE_URL}/people/{person_id}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Person retrieved successfully")
            print(f"   Name: {result['data']['full_name']}")
            print(f"   Gender: {result['data']['gender']}")
            print(f"   Religion: {result['data']['religion']}")
        else:
            print(f"❌ Failed to get person: {response.text}")
    except Exception as e:
        print(f"❌ Error getting person: {e}")
    
    print("\n3. Getting person by citizenship identity...")
    try:
        response = requests.get(f"{BASE_URL}/people/citizenship/{person_data['citizenship_identity']}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Person found by citizenship identity")
            print(f"   Name: {result['data']['full_name']}")
            print(f"   Citizenship: {result['data']['citizenship']}")
        else:
            print(f"❌ Failed to get person by citizenship identity: {response.text}")
    except Exception as e:
        print(f"❌ Error getting person by citizenship identity: {e}")
    
    print("\n4. Searching people by name...")
    try:
        response = requests.get(f"{BASE_URL}/people/search/John")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Found {result['count']} people matching 'John'")
            for person in result['data']:
                print(f"   - {person['full_name']} ({person['citizenship_identity']})")
        else:
            print(f"❌ Failed to search people: {response.text}")
    except Exception as e:
        print(f"❌ Error searching people: {e}")
    
    print("\n5. Getting people with filters...")
    try:
        response = requests.get(
            f"{BASE_URL}/people/",
            params={
                "gender": "MALE",
                "religion": "MUSLIM",
                "limit": 10
            }
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Found {result['count']} male Muslim people")
            for person in result['data']:
                print(f"   - {person['full_name']} ({person['gender']}, {person['religion']})")
        else:
            print(f"❌ Failed to get filtered people: {response.text}")
    except Exception as e:
        print(f"❌ Error getting filtered people: {e}")
    
    print("\n6. Updating person...")
    update_data = {
        "job": "Senior Software Engineer",
        "marital_status": "MARRIED",
        "blood_type": "O+"
    }
    
    try:
        response = requests.put(
            f"{BASE_URL}/people/{person_id}",
            json=update_data,
            params={"user_id": test_user_id}
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Person updated successfully")
            print(f"   New job: {result['data']['job']}")
            print(f"   New marital status: {result['data']['marital_status']}")
        else:
            print(f"❌ Failed to update person: {response.text}")
    except Exception as e:
        print(f"❌ Error updating person: {e}")
    
    print("\n7. Getting people statistics...")
    try:
        response = requests.get(f"{BASE_URL}/people/statistics/")
        
        if response.status_code == 200:
            result = response.json()
            stats = result['data']
            print(f"✅ People statistics retrieved")
            print(f"   Total count: {stats['total_count']}")
            print(f"   Gender distribution: {stats['gender_distribution']}")
            print(f"   Religion distribution: {stats['religion_distribution']}")
        else:
            print(f"❌ Failed to get statistics: {response.text}")
    except Exception as e:
        print(f"❌ Error getting statistics: {e}")
    
    print("\n8. Deleting person...")
    try:
        response = requests.delete(
            f"{BASE_URL}/people/{person_id}",
            params={"user_id": test_user_id}
        )
        
        if response.status_code == 200:
            print(f"✅ Person deleted successfully")
        else:
            print(f"❌ Failed to delete person: {response.text}")
    except Exception as e:
        print(f"❌ Error deleting person: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 People CRUD test completed!")


def test_bulk_operations():
    """Test bulk operations with multiple people"""
    
    print("\n🧪 Testing Bulk Operations")
    print("=" * 50)
    
    # Sample people data
    people_data = [
        {
            "full_name": "Alice Johnson",
            "place_of_birth": "Bandung",
            "date_of_birth": "1985-03-20",
            "gender": "FEMALE",
            "religion": "CHRISTIAN",
            "citizenship_identity": "1111111111111111",
            "citizenship": "INDONESIAN_CITIZEN",
            "nationality": "Indonesian",
            "ethnicity": "Sundanese",
            "marital_status": "MARRIED",
            "disability_status": 0,
            "blood_type": "A+",
            "job": "Teacher"
        },
        {
            "full_name": "Bob Smith",
            "place_of_birth": "Surabaya",
            "date_of_birth": "1992-08-10",
            "gender": "MALE",
            "religion": "HINDU",
            "citizenship_identity": "2222222222222222",
            "citizenship": "INDONESIAN_CITIZEN",
            "nationality": "Indonesian",
            "ethnicity": "Balinese",
            "marital_status": "SINGLE",
            "disability_status": 0,
            "blood_type": "B+",
            "job": "Doctor"
        },
        {
            "full_name": "Charlie Brown",
            "place_of_birth": "Medan",
            "date_of_birth": "1988-12-05",
            "gender": "MALE",
            "religion": "BUDDHA",
            "citizenship_identity": "3333333333333333",
            "citizenship": "INDONESIAN_CITIZEN",
            "nationality": "Indonesian",
            "ethnicity": "Chinese",
            "marital_status": "DIVORCED",
            "disability_status": 0,
            "blood_type": "AB+",
            "job": "Engineer"
        }
    ]
    
    created_people = []
    
    print("\n1. Creating multiple people...")
    for i, person_data in enumerate(people_data, 1):
        try:
            response = requests.post(f"{BASE_URL}/people/", json=person_data)
            
            if response.status_code == 200:
                result = response.json()
                person_id = result["data"]["id"]
                created_people.append(person_id)
                print(f"✅ Created person {i}: {person_data['full_name']} ({person_id})")
            else:
                print(f"❌ Failed to create person {i}: {response.text}")
        except Exception as e:
            print(f"❌ Error creating person {i}: {e}")
    
    print(f"\n2. Created {len(created_people)} people successfully")
    
    print("\n3. Testing advanced search...")
    try:
        response = requests.get(
            f"{BASE_URL}/people/",
            params={
                "gender": "MALE",
                "religion": "HINDU",
                "limit": 5
            }
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Found {result['count']} male Hindu people")
            for person in result['data']:
                print(f"   - {person['full_name']} ({person['gender']}, {person['religion']})")
        else:
            print(f"❌ Failed to search: {response.text}")
    except Exception as e:
        print(f"❌ Error in advanced search: {e}")
    
    print("\n4. Cleaning up created people...")
    for person_id in created_people:
        try:
            response = requests.delete(f"{BASE_URL}/people/{person_id}")
            if response.status_code == 200:
                print(f"✅ Deleted person: {person_id}")
            else:
                print(f"❌ Failed to delete person {person_id}: {response.text}")
        except Exception as e:
            print(f"❌ Error deleting person {person_id}: {e}")


if __name__ == "__main__":
    print("🚀 Starting People CRUD API Tests")
    print("Make sure the API server is running on http://localhost:8000")
    print()
    
    try:
        # Test basic CRUD operations
        test_people_crud()
        
        # Test bulk operations
        test_bulk_operations()
        
        print("\n🎉 All tests completed successfully!")
        
    except KeyboardInterrupt:
        print("\n⏹️  Tests interrupted by user")
    except Exception as e:
        print(f"\n💥 Test failed with error: {e}") 