"""
Unit tests for Rider Registration
Uses Django's test framework with in-memory database
"""

from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from accounts.models import AssistantVerification
from django.core.files.uploadedfile import SimpleUploadedFile
from io import BytesIO
from PIL import Image

User = get_user_model()

def create_test_image(name="test.jpg"):
    """Create a test image in memory"""
    image = Image.new('RGB', (100, 100), color='red')
    image_io = BytesIO()
    image.save(image_io, format='JPEG')
    image_io.seek(0)
    return SimpleUploadedFile(name, image_io.read(), content_type='image/jpeg')

class RiderRegistrationTests(TestCase):
    """Test cases for rider registration endpoint"""
    
    def setUp(self):
        """Set up test client"""
        self.client = Client()
        self.url = '/api/accounts/rider/register/'
    
    def get_valid_data(self, username='test_rider_001'):
        """Get valid registration data"""
        return {
            'username': username,
            'email': f'{username}@test.com',
            'password': 'TestPass123!',
            'password2': 'TestPass123!',
            'first_name': 'John',
            'last_name': 'Doe',
            'phone_number': f'+25471234{username[-4:]}',
            'full_name': 'John Doe Mwangi',
            'id_number': '12345678',
            'address': '123 Test Street, Nairobi',
            'area_of_operation': 'Westlands, Nairobi',
            'driving_license_number': 'DL123456',
            'profile_picture': create_test_image('selfie.jpg'),
            'id_front_image': create_test_image('id_front.jpg'),
            'id_back_image': create_test_image('id_back.jpg'),
            'driving_license_image': create_test_image('license.jpg'),
        }
    
    def test_successful_registration(self):
        """Test successful rider registration"""
        print("\n✓ Test 1: Successful Registration")
        
        data = self.get_valid_data()
        response = self.client.post(self.url, data, format='multipart')
        
        self.assertEqual(response.status_code, 201, f"Expected 201, got {response.status_code}")
        self.assertIn('user_id', response.json())
        self.assertIn('phone_number', response.json())
        
        # Verify user created
        user = User.objects.get(username='test_rider_001')
        self.assertEqual(user.user_type, 'assistant')
        self.assertFalse(user.is_active)  # Should be inactive until phone verified
        
        # Verify verification record
        verification = AssistantVerification.objects.get(user=user)
        self.assertEqual(verification.status, 'pending')
        self.assertEqual(verification.user_role, 'rider')
        self.assertIsNotNone(verification.selfie_url)
        
        print("  ✓ User created with correct type")
        print("  ✓ Verification record created")
        print("  ✓ Images uploaded")
    
    def test_missing_required_field(self):
        """Test missing required field"""
        print("\n✓ Test 2: Missing Required Field")
        
        data = self.get_valid_data()
        del data['username']  # Remove required field
        
        response = self.client.post(self.url, data, format='multipart')
        
        self.assertEqual(response.status_code, 400)
        print("  ✓ Correctly rejected missing field")
    
    def test_duplicate_username(self):
        """Test duplicate username rejection"""
        print("\n✓ Test 3: Duplicate Username")
        
        # Create first user
        data1 = self.get_valid_data('test_dup_001')
        response1 = self.client.post(self.url, data1, format='multipart')
        self.assertEqual(response1.status_code, 201)
        
        # Try to create duplicate
        data2 = self.get_valid_data('test_dup_001')
        data2['email'] = 'different@test.com'
        data2['phone_number'] = '+254712340002'
        data2['profile_picture'] = create_test_image('selfie2.jpg')
        data2['id_front_image'] = create_test_image('id_front2.jpg')
        data2['id_back_image'] = create_test_image('id_back2.jpg')
        data2['driving_license_image'] = create_test_image('license2.jpg')
        
        response2 = self.client.post(self.url, data2, format='multipart')
        
        self.assertEqual(response2.status_code, 400)
        print("  ✓ Correctly rejected duplicate username")
    
    def test_duplicate_phone(self):
        """Test duplicate phone number rejection"""
        print("\n✓ Test 4: Duplicate Phone Number")
        
        # Create first user
        data1 = self.get_valid_data('test_phone_001')
        response1 = self.client.post(self.url, data1, format='multipart')
        self.assertEqual(response1.status_code, 201)
        
        # Try with same phone
        data2 = self.get_valid_data('test_phone_002')
        data2['phone_number'] = data1['phone_number']  # Same phone
        data2['profile_picture'] = create_test_image('selfie2.jpg')
        data2['id_front_image'] = create_test_image('id_front2.jpg')
        data2['id_back_image'] = create_test_image('id_back2.jpg')
        data2['driving_license_image'] = create_test_image('license2.jpg')
        
        response2 = self.client.post(self.url, data2, format='multipart')
        
        self.assertEqual(response2.status_code, 400)
        print("  ✓ Correctly rejected duplicate phone")
    
    def test_password_mismatch(self):
        """Test password mismatch"""
        print("\n✓ Test 5: Password Mismatch")
        
        data = self.get_valid_data()
        data['password2'] = 'DifferentPass123!'
        
        response = self.client.post(self.url, data, format='multipart')
        
        self.assertEqual(response.status_code, 400)
        print("  ✓ Correctly rejected password mismatch")
    
    def test_missing_image(self):
        """Test missing required image"""
        print("\n✓ Test 6: Missing Required Image")
        
        data = self.get_valid_data()
        del data['profile_picture']  # Remove required image
        
        response = self.client.post(self.url, data, format='multipart')
        
        self.assertEqual(response.status_code, 400)
        print("  ✓ Correctly rejected missing image")
    
    def test_user_type_is_assistant(self):
        """Test that user_type is automatically set to assistant"""
        print("\n✓ Test 7: User Type Auto-Set")
        
        data = self.get_valid_data('test_type_001')
        response = self.client.post(self.url, data, format='multipart')
        
        self.assertEqual(response.status_code, 201)
        
        user = User.objects.get(username='test_type_001')
        self.assertEqual(user.user_type, 'assistant')
        print("  ✓ User type correctly set to 'assistant'")
    
    def test_verification_fields(self):
        """Test that all verification fields are saved"""
        print("\n✓ Test 8: Verification Fields")
        
        data = self.get_valid_data('test_verify_001')
        response = self.client.post(self.url, data, format='multipart')
        
        self.assertEqual(response.status_code, 201)
        
        user = User.objects.get(username='test_verify_001')
        verification = AssistantVerification.objects.get(user=user)
        
        self.assertEqual(verification.full_name, 'John Doe Mwangi')
        self.assertEqual(verification.id_number, '12345678')
        self.assertEqual(verification.driving_license_number, 'DL123456')
        self.assertEqual(verification.address, '123 Test Street, Nairobi')
        self.assertEqual(verification.area_of_operation, 'Westlands, Nairobi')
        
        print("  ✓ All verification fields saved correctly")
