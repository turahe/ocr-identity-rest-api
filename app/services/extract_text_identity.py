"""
OCR Identity Document Text Extraction using spaCy NER
This module provides spaCy-based Named Entity Recognition for extracting
structured information from Indonesian identity documents.
"""

import re
import logging
from typing import Dict, Any, Optional
from dataclasses import dataclass

# Import the spaCy extraction service
try:
    from app.services.spacy_extraction_service import (
        SpacyExtractionService, 
        IdentityDocumentData,
        get_spacy_extraction_service
    )
except ImportError:
    # Fallback for when the app module is not available
    SpacyExtractionService = None
    IdentityDocumentData = None
    get_spacy_extraction_service = None

logger = logging.getLogger(__name__)


@dataclass
class ExtractionResult:
    """Result of identity document extraction."""
    nik: Optional[str] = None
    nama: Optional[str] = None
    tempat_lahir: Optional[str] = None
    tanggal_lahir: Optional[str] = None
    jenis_kelamin: Optional[str] = None
    golongan_darah: Optional[str] = None
    alamat: Optional[str] = None
    rt: Optional[str] = None
    rw: Optional[str] = None
    kecamatan: Optional[str] = None
    kelurahan_atau_desa: Optional[str] = None
    kewarganegaraan: Optional[str] = None
    pekerjaan: Optional[str] = None
    agama: Optional[str] = None
    status_perkawinan: Optional[str] = None
    confidence: float = 0.0
    extraction_method: str = "spacy_ner"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary, excluding None values."""
        return {k: v for k, v in self.__dict__.items() if v is not None}


class IdentityDocumentExtractor:
    """
    Identity document text extractor using spaCy NER.
    
    This class provides methods to extract structured information from
    Indonesian identity documents using Named Entity Recognition.
    """
    
    def __init__(self, model_name: str = "id_core_news_sm"):
        """
        Initialize the extractor.
        
        Args:
            model_name: Name of the spaCy model to use
        """
        self.model_name = model_name
        self.spacy_service: Optional[SpacyExtractionService] = None
        self._initialize_spacy_service()
    
    def _initialize_spacy_service(self) -> None:
        """Initialize the spaCy extraction service."""
        try:
            if get_spacy_extraction_service is not None:
                self.spacy_service = get_spacy_extraction_service(self.model_name)
                logger.info(f"Initialized spaCy extraction service with model: {self.model_name}")
            else:
                logger.warning("spaCy extraction service not available, using fallback")
                self.spacy_service = None
        except Exception as e:
            logger.error(f"Failed to initialize spaCy service: {e}")
            self.spacy_service = None
    
    def extract(self, extracted_result: str) -> ExtractionResult:
        """
        Extract structured information from OCR text using spaCy NER.
        
        Args:
            extracted_result: OCR-processed text from identity document
            
        Returns:
            ExtractionResult with extracted information
        """
        if self.spacy_service is not None:
            return self._extract_with_spacy(extracted_result)
        else:
            return self._extract_with_fallback(extracted_result)
    
    def _extract_with_spacy(self, text: str) -> ExtractionResult:
        """
        Extract information using spaCy NER.
        
        Args:
            text: OCR-processed text
            
        Returns:
            ExtractionResult with extracted information
        """
        try:
            # Use spaCy service to extract entities
            if self.spacy_service is not None:
                spacy_result = self.spacy_service.extract_entities(text)
            
            # Convert to our result format
            result = ExtractionResult(
                nik=spacy_result.nik,
                nama=spacy_result.nama,
                tempat_lahir=spacy_result.tempat_lahir,
                tanggal_lahir=spacy_result.tanggal_lahir,
                jenis_kelamin=spacy_result.jenis_kelamin,
                golongan_darah=spacy_result.golongan_darah,
                alamat=spacy_result.alamat,
                rt=spacy_result.rt,
                rw=spacy_result.rw,
                kecamatan=spacy_result.kecamatan,
                kelurahan_atau_desa=spacy_result.kelurahan_atau_desa,
                kewarganegaraan=spacy_result.kewarganegaraan,
                pekerjaan=spacy_result.pekerjaan,
                agama=spacy_result.agama,
                status_perkawinan=spacy_result.status_perkawinan,
                confidence=0.85,  # spaCy NER typically has high confidence
                extraction_method="spacy_ner"
            )
            
            logger.info(f"Successfully extracted data using spaCy NER: {result}")
            return result
            
        except Exception as e:
            logger.error(f"spaCy extraction failed: {e}")
            # Fallback to manual extraction
            return self._extract_with_fallback(text)
    
    def _extract_with_fallback(self, text: str) -> ExtractionResult:
        """
        Fallback extraction using manual pattern matching.
        This is the original extraction logic as a fallback.
        
        Args:
            text: OCR-processed text
            
        Returns:
            ExtractionResult with extracted information
        """
        result = ExtractionResult(extraction_method="manual_pattern")
        
        # Clean and normalize text
        text = self._normalize_text(text)
        
        # Extract information using manual patterns
        for word in text.split("\n"):
            word = word.strip()
            if not word:
                continue
                
            # Extract NIK
            if "NIK" in word:
                word_parts = word.split(':')
                if len(word_parts) > 1:
                    result.nik = self._extract_nik(word_parts[-1].replace(" ", ""))
                continue

            # Extract name
            if "Nama" in word:
                word_parts = word.split(':')
                if len(word_parts) > 1:
                    result.nama = word_parts[-1].replace('Nama ', '').replace('1', '').strip()
                continue

            # Extract birth place and date
            if "Tempat" in word:
                word_parts = word.split(':')
                if len(word_parts) > 1:
                    birth_text = word_parts[-1]
                    date_match = re.search(r"([0-9]{2}\-[0-9]{2}\-[0-9]{4})", birth_text)
                    if date_match:
                        result.tanggal_lahir = date_match.group(1)
                        if result.tanggal_lahir:
                            result.tempat_lahir = birth_text.replace(result.tanggal_lahir, '').strip(', ')
                continue

            # Extract gender and blood type
            if 'Darah' in word:
                gender_match = re.search("(LAKI-LAKI|LAKI|LELAKI|PEREMPUAN)", word)
                if gender_match:
                    result.jenis_kelamin = gender_match.group(1)
                
                word_parts = word.split(':')
                if len(word_parts) > 1:
                    blood_match = re.search("(O|A|B|AB)", word_parts[-1])
                    if blood_match:
                        result.golongan_darah = blood_match.group(1)
                    else:
                        result.golongan_darah = '-'
                continue
                
            # Extract address
            if 'Alamat' in word:
                result.alamat = self._word_to_number_converter(word).replace("Alamat ", "").strip()
                continue
                
            # Extract RT/RW
            if "RTRW" in word:
                cleaned_string = word.replace("RTRW", '').strip()
                parts = re.split(r'[/\s]+', cleaned_string)
                if len(parts) == 2:
                    result.rt = parts[0].strip()
                    result.rw = parts[1].strip()
                else:
                    result.rt = "000"
                    result.rw = "000"
                continue
                
            # Extract kecamatan
            if "Kecamatan" in word:
                separator = '—' if '—' in word else ':'
                word_parts = word.split(separator)
                if len(word_parts) > 1:
                    result.kecamatan = word_parts[1].strip()
                continue
                
            # Extract desa/kelurahan
            if "Desa" in word:
                words = word.split()
                desa_parts = []
                for w in words:
                    if not 'desa' in w.lower():
                        desa_parts.append(w)
                result.kelurahan_atau_desa = ''.join(desa_parts)
                continue
                
            # Extract citizenship
            if 'Kewarganegaraan' in word:
                word_parts = word.split(':')
                if len(word_parts) > 1:
                    result.kewarganegaraan = word_parts[1].strip()
                continue
                
            # Extract occupation
            if 'Pekerjaan' in word:
                words = word.split()
                pekerjaan_parts = []
                for w in words:
                    if not '-' in w:
                        pekerjaan_parts.append(w)
                result.pekerjaan = ' '.join(pekerjaan_parts).replace('Pekerjaan', '').strip()
                continue
                
            # Extract religion
            if 'Agama' in word:
                result.agama = word.replace('Agama', "").strip()
                continue
                
            # Extract marital status
            if 'Perkawinan' in word:
                word_parts = word.split(':')
                if len(word_parts) > 1:
                    result.status_perkawinan = word_parts[1].strip()
                continue
        
        logger.info(f"Extracted data using manual patterns: {result}")
        return result
    
    def _normalize_text(self, text: str) -> str:
        """
        Normalize text for better extraction.
        
        Args:
            text: Raw OCR text
            
        Returns:
            Normalized text
        """
        # Normalize whitespace
        text = re.sub(r'\s+', ' ', text.strip())
        
        # Normalize common OCR errors
        text = text.replace('|', 'I')
        text = text.replace('0', 'O')  # In certain contexts
        
        # Normalize line breaks
        text = text.replace('\r\n', '\n').replace('\r', '\n')
        
        return text
    
    def _extract_nik(self, text: str) -> Optional[str]:
        """
        Extract NIK (National Identity Number) from text.
        
        Args:
            text: Text containing NIK
            
        Returns:
            Extracted NIK or None
        """
        # Remove non-digit characters
        nik = re.sub(r'[^\d]', '', text)
        
        # Check if it's a valid 16-digit NIK
        if len(nik) == 16:
            return nik
        
        return None
    
    def _word_to_number_converter(self, text: str) -> str:
        """
        Convert word representations of numbers to digits.
        
        Args:
            text: Text with word numbers
            
        Returns:
            Text with converted numbers
        """
        # Simple word to number mapping for Indonesian
        word_to_number = {
            'satu': '1', 'dua': '2', 'tiga': '3', 'empat': '4', 'lima': '5',
            'enam': '6', 'tujuh': '7', 'delapan': '8', 'sembilan': '9', 'sepuluh': '10'
        }
        
        for word, number in word_to_number.items():
            text = text.replace(word, number)
        
        return text
    
    def get_extraction_stats(self, text: str) -> Dict[str, Any]:
        """
        Get statistics about the extraction process.
        
        Args:
            text: Original text that was processed
            
        Returns:
            Dictionary with extraction statistics
        """
        stats = {
            "text_length": len(text),
            "extraction_method": "unknown",
            "confidence": 0.0
        }
        
        if self.spacy_service is not None:
            try:
                spacy_stats = self.spacy_service.get_extraction_stats(text)
                stats.update(spacy_stats)
                stats["extraction_method"] = "spacy_ner"
                stats["confidence"] = 0.85
            except Exception as e:
                logger.error(f"Failed to get spaCy stats: {e}")
                stats["extraction_method"] = "manual_pattern"
                stats["confidence"] = 0.6
        else:
            stats["extraction_method"] = "manual_pattern"
            stats["confidence"] = 0.6
        
        return stats


# Global instance for reuse
_extractor: Optional[IdentityDocumentExtractor] = None


def get_extractor(model_name: str = "id_core_news_sm") -> IdentityDocumentExtractor:
    """
    Get or create a global extractor instance.
    
    Args:
        model_name: Name of the spaCy model to use
        
    Returns:
        IdentityDocumentExtractor instance
    """
    global _extractor
    
    if _extractor is None:
        _extractor = IdentityDocumentExtractor(model_name)
    
    return _extractor


# Backward compatibility
class Result:
    """Backward compatibility class for the original extraction result."""
    
    def __init__(self):
        self.nik: Optional[str] = None
        self.nama: Optional[str] = None
        self.tanggal_lahir: Optional[str] = None
        self.tempat_lahir: Optional[str] = None
        self.jenis_kelamin: Optional[str] = None
        self.golongan_darah: Optional[str] = None
        self.alamat: Optional[str] = None
        self.rt: Optional[str] = None
        self.rw: Optional[str] = None
        self.kecamatan: Optional[str] = None
        self.kelurahan_atau_desa: Optional[str] = None
        self.kewarganegaraan: Optional[str] = None
        self.pekerjaan: Optional[str] = None
        self.agama: Optional[str] = None
        self.status_perkawinan: Optional[str] = None


def extract_identity_info(text: str) -> Result:
    """
    Extract identity information from text (backward compatibility function).
    
    Args:
        text: OCR-processed text from identity document
        
    Returns:
        Result object with extracted information
    """
    extractor = get_extractor()
    extraction_result = extractor.extract(text)
    
    # Convert to backward compatibility format
    result = Result()
    result.nik = extraction_result.nik
    result.nama = extraction_result.nama
    result.tanggal_lahir = extraction_result.tanggal_lahir
    result.tempat_lahir = extraction_result.tempat_lahir
    result.jenis_kelamin = extraction_result.jenis_kelamin
    result.golongan_darah = extraction_result.golongan_darah
    result.alamat = extraction_result.alamat
    result.rt = extraction_result.rt
    result.rw = extraction_result.rw
    result.kecamatan = extraction_result.kecamatan
    result.kelurahan_atau_desa = extraction_result.kelurahan_atau_desa
    result.kewarganegaraan = extraction_result.kewarganegaraan
    result.pekerjaan = extraction_result.pekerjaan
    result.agama = extraction_result.agama
    result.status_perkawinan = extraction_result.status_perkawinan
    
    return result


