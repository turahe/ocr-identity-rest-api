#!/usr/bin/env python3
"""
Test script for spaCy-based identity document extraction.
This script demonstrates the new spaCy NER extraction functionality.
"""

import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_spacy_extraction():
    """Test the spaCy-based extraction functionality."""
    
    # Sample OCR text from Indonesian identity document
    sample_text = """
    PROVINSI DKI JAKARTA
    KOTA JAKARTA PUSAT
    
    NIK: 3173011234567890
    Nama: JOHN DOE
    Tempat/Tgl Lahir: JAKARTA, 01-01-1990
    Jenis Kelamin: LAKI-LAKI
    Alamat: JL. SUDIRMAN NO. 123
    RT/RW: 001/002
    Kelurahan/Desa: SENAYAN
    Kecamatan: KEBAYORAN BARU
    Agama: ISLAM
    Status Perkawinan: BELUM KAWIN
    Pekerjaan: PEGAWAI NEGERI SIPIL
    Kewarganegaraan: WNI
    Berlaku Hingga: SEUMUR HIDUP
    """
    
    print("🧪 Testing spaCy-based Identity Document Extraction")
    print("=" * 60)
    
    try:
        # Import the extraction module
        from app.services.extract_text_identity import get_extractor, IdentityDocumentExtractor
        
        # Initialize extractor
        print("📦 Initializing spaCy extractor...")
        extractor = get_extractor("id_core_news_sm")
        
        # Test extraction
        print("🔍 Extracting information from sample text...")
        result = extractor.extract(sample_text)
        
        # Display results
        print("\n📋 Extraction Results:")
        print("-" * 40)
        
        if result.extraction_method == "spacy_ner":
            print("✅ Using spaCy NER extraction")
        else:
            print("⚠️  Using fallback manual extraction")
        
        print(f"Confidence: {result.confidence:.2f}")
        print(f"Method: {result.extraction_method}")
        
        # Display extracted data
        extracted_data = result.to_dict()
        for key, value in extracted_data.items():
            if key not in ['confidence', 'extraction_method'] and value:
                print(f"{key.replace('_', ' ').title()}: {value}")
        
        # Test statistics
        print("\n📊 Extraction Statistics:")
        print("-" * 40)
        stats = extractor.get_extraction_stats(sample_text)
        for key, value in stats.items():
            print(f"{key.replace('_', ' ').title()}: {value}")
        
        # Test with different text formats
        print("\n🔄 Testing with different text formats...")
        
        # Test with English text
        english_text = """
        PROVINCE: DKI JAKARTA
        CITY: JAKARTA CENTRAL
        
        NIK: 3173011234567890
        Name: JOHN DOE
        Birth Place/Date: JAKARTA, 01-01-1990
        Gender: MALE
        Address: JL. SUDIRMAN NO. 123
        RT/RW: 001/002
        Village: SENAYAN
        District: KEBAYORAN BARU
        Religion: ISLAM
        Marital Status: SINGLE
        Occupation: CIVIL SERVANT
        Citizenship: INDONESIAN
        Valid Until: LIFETIME
        """
        
        english_result = extractor.extract(english_text)
        print(f"English text extraction method: {english_result.extraction_method}")
        
        # Test with messy OCR text
        messy_text = """
        PROVINSI DKI JAKARTA
        KOTA JAKARTA PUSAT
        
        NIK: 3173011234567890
        Nama: JOHN DOE
        Tempat/Tgl Lahir: JAKARTA, 01-01-1990
        Jenis Kelamin: LAKI-LAKI
        Alamat: JL. SUDIRMAN NO. 123
        RT/RW: 001/002
        Kelurahan/Desa: SENAYAN
        Kecamatan: KEBAYORAN BARU
        Agama: ISLAM
        Status Perkawinan: BELUM KAWIN
        Pekerjaan: PEGAWAI NEGERI SIPIL
        Kewarganegaraan: WNI
        Berlaku Hingga: SEUMUR HIDUP
        """
        
        messy_result = extractor.extract(messy_text)
        print(f"Messy OCR text extraction method: {messy_result.extraction_method}")
        
        print("\n✅ spaCy extraction test completed successfully!")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Please install dependencies: poetry install")
        return False
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False


def test_backward_compatibility():
    """Test backward compatibility with the original extraction interface."""
    
    print("\n🔄 Testing Backward Compatibility")
    print("=" * 40)
    
    try:
        from app.services.extract_text_identity import extract_identity_info, Result
        
        sample_text = """
        NIK: 3173011234567890
        Nama: JOHN DOE
        Tempat/Tgl Lahir: JAKARTA, 01-01-1990
        Jenis Kelamin: LAKI-LAKI
        Alamat: JL. SUDIRMAN NO. 123
        """
        
        # Test the backward compatibility function
        result = extract_identity_info(sample_text)
        
        print("✅ Backward compatibility test passed")
        print(f"NIK: {result.nik}")
        print(f"Nama: {result.nama}")
        print(f"Tempat Lahir: {result.tempat_lahir}")
        print(f"Tanggal Lahir: {result.tanggal_lahir}")
        
        return True
        
    except Exception as e:
        print(f"❌ Backward compatibility test failed: {e}")
        return False


def test_spacy_service():
    """Test the spaCy extraction service directly."""
    
    print("\n🔧 Testing spaCy Service Directly")
    print("=" * 40)
    
    try:
        from app.services.spacy_extraction_service import get_spacy_extraction_service, IdentityDocumentData
        
        sample_text = """
        NIK: 3173011234567890
        Nama: JOHN DOE
        Tempat/Tgl Lahir: JAKARTA, 01-01-1990
        Jenis Kelamin: LAKI-LAKI
        """
        
        # Get spaCy service
        spacy_service = get_spacy_extraction_service()
        
        # Extract entities
        result = spacy_service.extract_entities(sample_text)
        
        print("✅ spaCy service test passed")
        print(f"Extracted NIK: {result.nik}")
        print(f"Extracted Nama: {result.nama}")
        print(f"Extracted Tempat Lahir: {result.tempat_lahir}")
        print(f"Extracted Tanggal Lahir: {result.tanggal_lahir}")
        
        return True
        
    except Exception as e:
        print(f"❌ spaCy service test failed: {e}")
        return False


def main():
    """Main test function."""
    print("🚀 spaCy Identity Document Extraction Test")
    print("=" * 60)
    
    # Run tests
    tests = [
        ("spaCy Extraction", test_spacy_extraction),
        ("Backward Compatibility", test_backward_compatibility),
        ("spaCy Service", test_spacy_service),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n🧪 Running {test_name} test...")
        try:
            success = test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"❌ {test_name} test failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n📊 Test Summary")
    print("=" * 40)
    
    passed = 0
    total = len(results)
    
    for test_name, success in results:
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"{test_name}: {status}")
        if success:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! spaCy extraction is working correctly.")
    else:
        print("⚠️  Some tests failed. Please check the installation and configuration.")
    
    return passed == total


if __name__ == "__main__":
    main() 