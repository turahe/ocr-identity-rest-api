"""
spaCy-based Named Entity Recognition (NER) service for identity document processing.
This service uses spaCy models to extract structured information from OCR text.
"""

import re
import logging
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from datetime import datetime

try:
    import spacy
    from spacy.tokens import Doc
    from spacy.language import Language
except ImportError:
    spacy = None
    Doc = None
    Language = None

logger = logging.getLogger(__name__)


@dataclass
class IdentityDocumentData:
    """Structured data extracted from identity documents."""
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
    kk_number: Optional[str] = None
    document_type: Optional[str] = None
    issue_date: Optional[str] = None
    expiry_date: Optional[str] = None
    issuing_authority: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary, excluding None values."""
        return {k: v for k, v in self.__dict__.items() if v is not None}
    
    def __str__(self) -> str:
        """String representation of extracted data."""
        return f"IdentityDocumentData({', '.join(f'{k}={v}' for k, v in self.to_dict().items())})"


class SpacyExtractionService:
    """
    spaCy-based extraction service for identity documents.
    
    This service uses Named Entity Recognition (NER) to extract structured
    information from OCR-processed identity document text.
    """
    
    def __init__(self, model_name: str = "id_core_news_sm"):
        """
        Initialize the spaCy extraction service.
        
        Args:
            model_name: Name of the spaCy model to use for processing
        """
        if spacy is None:
            raise ImportError("spaCy is not installed. Please install it with: poetry install")
        
        self.model_name = model_name
        self.nlp: Optional[Language] = None
        self._load_model()
        self._setup_custom_patterns()
    
    def _load_model(self) -> None:
        """Load the spaCy model."""
        try:
            self.nlp = spacy.load(self.model_name)
            logger.info(f"Loaded spaCy model: {self.model_name}")
        except OSError as e:
            logger.error(f"Failed to load spaCy model {self.model_name}: {e}")
            logger.info("Please download the model using: poetry run python scripts/download_spacy_models.py")
            raise
    
    def _setup_custom_patterns(self) -> None:
        """Setup custom patterns and rules for identity document processing."""
        if self.nlp is None:
            return
        
        # Add custom entity patterns for Indonesian identity documents
        ruler = self.nlp.get_pipe("entity_ruler") if "entity_ruler" in self.nlp.pipe_names else self.nlp.add_pipe("entity_ruler")
        
        patterns = [
            # NIK patterns
            {"label": "NIK", "pattern": [{"LOWER": "nik"}, {"OP": ":"}, {"SHAPE": "dddddddddddddddd"}]},
            {"label": "NIK", "pattern": [{"LOWER": "nik"}, {"OP": ":"}, {"TEXT": {"REGEX": r"\d{16}"}}]},
            
            # Name patterns
            {"label": "NAME", "pattern": [{"LOWER": "nama"}, {"OP": ":"}, {"OP": "+"}]},
            {"label": "NAME", "pattern": [{"LOWER": "name"}, {"OP": ":"}, {"OP": "+"}]},
            
            # Date patterns
            {"label": "DATE", "pattern": [{"TEXT": {"REGEX": r"\d{2}-\d{2}-\d{4}"}}]},
            {"label": "DATE", "pattern": [{"TEXT": {"REGEX": r"\d{2}/\d{2}/\d{4}"}}]},
            
            # Address patterns
            {"label": "ADDRESS", "pattern": [{"LOWER": "alamat"}, {"OP": ":"}, {"OP": "+"}]},
            {"label": "ADDRESS", "pattern": [{"LOWER": "address"}, {"OP": ":"}, {"OP": "+"}]},
            
            # Blood type patterns
            {"label": "BLOOD_TYPE", "pattern": [{"LOWER": "darah"}, {"OP": ":"}, {"TEXT": {"REGEX": r"[OAB]\+?"}}]},
            {"label": "BLOOD_TYPE", "pattern": [{"LOWER": "golongan"}, {"OP": ":"}, {"TEXT": {"REGEX": r"[OAB]\+?"}}]},
            
            # Gender patterns
            {"label": "GENDER", "pattern": [{"LOWER": {"IN": ["laki-laki", "perempuan", "male", "female"]}}]},
            
            # Religion patterns
            {"label": "RELIGION", "pattern": [{"LOWER": "agama"}, {"OP": ":"}, {"OP": "+"}]},
            
            # Occupation patterns
            {"label": "OCCUPATION", "pattern": [{"LOWER": "pekerjaan"}, {"OP": ":"}, {"OP": "+"}]},
            
            # Citizenship patterns
            {"label": "CITIZENSHIP", "pattern": [{"LOWER": "kewarganegaraan"}, {"OP": ":"}, {"OP": "+"}]},
            
            # Marital status patterns
            {"label": "MARITAL_STATUS", "pattern": [{"LOWER": "perkawinan"}, {"OP": ":"}, {"OP": "+"}]},
        ]
        
        ruler.add_patterns(patterns)
        logger.info("Added custom entity patterns for identity document processing")
    
    def extract_entities(self, text: str) -> IdentityDocumentData:
        """
        Extract structured data from identity document text using spaCy NER.
        
        Args:
            text: OCR-processed text from identity document
            
        Returns:
            IdentityDocumentData object with extracted information
        """
        if self.nlp is None:
            raise RuntimeError("spaCy model not loaded")
        
        # Clean and preprocess text
        cleaned_text = self._preprocess_text(text)
        
        # Process with spaCy
        doc = self.nlp(cleaned_text)
        
        # Extract structured data
        result = IdentityDocumentData()
        
        # Extract NIK
        result.nik = self._extract_nik(doc, cleaned_text)
        
        # Extract name
        result.nama = self._extract_name(doc, cleaned_text)
        
        # Extract birth information
        result.tempat_lahir, result.tanggal_lahir = self._extract_birth_info(doc, cleaned_text)
        
        # Extract gender and blood type
        result.jenis_kelamin, result.golongan_darah = self._extract_gender_and_blood(doc, cleaned_text)
        
        # Extract address information
        result.alamat, result.rt, result.rw = self._extract_address_info(doc, cleaned_text)
        
        # Extract administrative information
        result.kecamatan, result.kelurahan_atau_desa = self._extract_admin_info(doc, cleaned_text)
        
        # Extract other personal information
        result.kewarganegaraan = self._extract_citizenship(doc, cleaned_text)
        result.pekerjaan = self._extract_occupation(doc, cleaned_text)
        result.agama = self._extract_religion(doc, cleaned_text)
        result.status_perkawinan = self._extract_marital_status(doc, cleaned_text)
        
        # Extract document information
        result.document_type = self._extract_document_type(doc, cleaned_text)
        result.issue_date, result.expiry_date = self._extract_dates(doc, cleaned_text)
        result.issuing_authority = self._extract_issuing_authority(doc, cleaned_text)
        
        logger.info(f"Extracted data: {result}")
        return result
    
    def _preprocess_text(self, text: str) -> str:
        """Preprocess text for better NER performance."""
        # Normalize whitespace
        text = re.sub(r'\s+', ' ', text.strip())
        
        # Normalize common OCR errors
        text = text.replace('|', 'I')  # Common OCR error
        text = text.replace('0', 'O')  # Common OCR error in certain contexts
        
        # Add line breaks for better sentence segmentation
        text = re.sub(r'([A-Z][a-z]+:)', r'\n\1', text)
        
        return text
    
    def _extract_nik(self, doc: Doc, text: str) -> Optional[str]:
        """Extract NIK (National Identity Number)."""
        # Look for NIK entities
        for ent in doc.ents:
            if ent.label_ == "NIK":
                # Extract the number part
                nik_match = re.search(r'\d{16}', ent.text)
                if nik_match:
                    return nik_match.group()
        
        # Fallback: search for NIK pattern in text
        nik_patterns = [
            r'NIK[:\s]*(\d{16})',
            r'Nomor[:\s]*Induk[:\s]*Kependudukan[:\s]*(\d{16})',
        ]
        
        for pattern in nik_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1)
        
        return None
    
    def _extract_name(self, doc: Doc, text: str) -> Optional[str]:
        """Extract person name."""
        # Look for NAME entities
        for ent in doc.ents:
            if ent.label_ == "NAME":
                return ent.text.strip()
        
        # Look for PERSON entities
        for ent in doc.ents:
            if ent.label_ == "PERSON":
                return ent.text.strip()
        
        # Fallback: search for name pattern
        name_patterns = [
            r'Nama[:\s]+([A-Za-z\s]+)',
            r'Name[:\s]+([A-Za-z\s]+)',
        ]
        
        for pattern in name_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        return None
    
    def _extract_birth_info(self, doc: Doc, text: str) -> Tuple[Optional[str], Optional[str]]:
        """Extract birth place and date."""
        tempat_lahir = None
        tanggal_lahir = None
        
        # Look for DATE entities
        for ent in doc.ents:
            if ent.label_ == "DATE":
                date_text = ent.text
                # Try to extract date from birth information
                birth_match = re.search(r'(\d{2}-\d{2}-\d{4})', date_text)
                if birth_match:
                    tanggal_lahir = birth_match.group(1)
                    # Extract place from the same text
                    place_part = date_text.replace(tanggal_lahir, '').strip()
                    if place_part:
                        tempat_lahir = place_part.strip(', ')
        
        # Fallback: search for birth information pattern
        birth_patterns = [
            r'Tempat/Tgl[:\s]*Lahir[:\s]*([^,]+),\s*(\d{2}-\d{2}-\d{4})',
            r'Birth[:\s]*Place/Date[:\s]*([^,]+),\s*(\d{2}-\d{2}-\d{4})',
        ]
        
        for pattern in birth_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                tempat_lahir = match.group(1).strip()
                tanggal_lahir = match.group(2)
                break
        
        return tempat_lahir, tanggal_lahir
    
    def _extract_gender_and_blood(self, doc: Doc, text: str) -> Tuple[Optional[str], Optional[str]]:
        """Extract gender and blood type."""
        jenis_kelamin = None
        golongan_darah = None
        
        # Look for GENDER and BLOOD_TYPE entities
        for ent in doc.ents:
            if ent.label_ == "GENDER":
                jenis_kelamin = ent.text.strip()
            elif ent.label_ == "BLOOD_TYPE":
                golongan_darah = ent.text.strip()
        
        # Fallback: search for gender and blood type patterns
        gender_patterns = [
            r'(LAKI-LAKI|LAKI|LELAKI|PEREMPUAN)',
            r'(Male|Female)',
        ]
        
        for pattern in gender_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                jenis_kelamin = match.group(1)
                break
        
        blood_patterns = [
            r'Gol[.\s]*Darah[:\s]*([OAB]\+?)',
            r'Blood[:\s]*Type[:\s]*([OAB]\+?)',
        ]
        
        for pattern in blood_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                golongan_darah = match.group(1)
                break
        
        return jenis_kelamin, golongan_darah
    
    def _extract_address_info(self, doc: Doc, text: str) -> Tuple[Optional[str], Optional[str], Optional[str]]:
        """Extract address, RT, and RW information."""
        alamat = None
        rt = None
        rw = None
        
        # Look for ADDRESS entities
        for ent in doc.ents:
            if ent.label_ == "ADDRESS":
                alamat = ent.text.strip()
                break
        
        # Fallback: search for address patterns
        address_patterns = [
            r'Alamat[:\s]+([^\n]+)',
            r'Address[:\s]+([^\n]+)',
        ]
        
        for pattern in address_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                alamat = match.group(1).strip()
                break
        
        # Extract RT/RW
        rtrw_patterns = [
            r'RT[:\s]*(\d+)[/\s]*RW[:\s]*(\d+)',
            r'RTRW[:\s]*(\d+)/(\d+)',
        ]
        
        for pattern in rtrw_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                rt = match.group(1)
                rw = match.group(2)
                break
        
        return alamat, rt, rw
    
    def _extract_admin_info(self, doc: Doc, text: str) -> Tuple[Optional[str], Optional[str]]:
        """Extract kecamatan and kelurahan/desa information."""
        kecamatan = None
        kelurahan_atau_desa = None
        
        # Search for administrative patterns
        kecamatan_patterns = [
            r'Kecamatan[:\s]+([^\n]+)',
            r'District[:\s]+([^\n]+)',
        ]
        
        for pattern in kecamatan_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                kecamatan = match.group(1).strip()
                break
        
        kelurahan_patterns = [
            r'Desa[:\s]+([^\n]+)',
            r'Kelurahan[:\s]+([^\n]+)',
            r'Village[:\s]+([^\n]+)',
        ]
        
        for pattern in kelurahan_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                kelurahan_atau_desa = match.group(1).strip()
                break
        
        return kecamatan, kelurahan_atau_desa
    
    def _extract_citizenship(self, doc: Doc, text: str) -> Optional[str]:
        """Extract citizenship information."""
        # Look for CITIZENSHIP entities
        for ent in doc.ents:
            if ent.label_ == "CITIZENSHIP":
                return ent.text.strip()
        
        # Fallback: search for citizenship pattern
        citizenship_patterns = [
            r'Kewarganegaraan[:\s]+([^\n]+)',
            r'Citizenship[:\s]+([^\n]+)',
        ]
        
        for pattern in citizenship_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        return None
    
    def _extract_occupation(self, doc: Doc, text: str) -> Optional[str]:
        """Extract occupation information."""
        # Look for OCCUPATION entities
        for ent in doc.ents:
            if ent.label_ == "OCCUPATION":
                return ent.text.strip()
        
        # Fallback: search for occupation pattern
        occupation_patterns = [
            r'Pekerjaan[:\s]+([^\n]+)',
            r'Occupation[:\s]+([^\n]+)',
        ]
        
        for pattern in occupation_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        return None
    
    def _extract_religion(self, doc: Doc, text: str) -> Optional[str]:
        """Extract religion information."""
        # Look for RELIGION entities
        for ent in doc.ents:
            if ent.label_ == "RELIGION":
                return ent.text.strip()
        
        # Fallback: search for religion pattern
        religion_patterns = [
            r'Agama[:\s]+([^\n]+)',
            r'Religion[:\s]+([^\n]+)',
        ]
        
        for pattern in religion_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        return None
    
    def _extract_marital_status(self, doc: Doc, text: str) -> Optional[str]:
        """Extract marital status information."""
        # Look for MARITAL_STATUS entities
        for ent in doc.ents:
            if ent.label_ == "MARITAL_STATUS":
                return ent.text.strip()
        
        # Fallback: search for marital status pattern
        marital_patterns = [
            r'Perkawinan[:\s]+([^\n]+)',
            r'Marital[:\s]+Status[:\s]+([^\n]+)',
        ]
        
        for pattern in marital_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        return None
    
    def _extract_document_type(self, doc: Doc, text: str) -> Optional[str]:
        """Extract document type."""
        # Search for document type patterns
        doc_type_patterns = [
            r'KTP[:\s]*Elektronik',
            r'Electronic[:\s]*ID[:\s]*Card',
            r'Kartu[:\s]*Tanda[:\s]*Penduduk',
        ]
        
        for pattern in doc_type_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(0).strip()
        
        return None
    
    def _extract_dates(self, doc: Doc, text: str) -> Tuple[Optional[str], Optional[str]]:
        """Extract issue and expiry dates."""
        issue_date = None
        expiry_date = None
        
        # Look for DATE entities and determine if they're issue or expiry dates
        dates = []
        for ent in doc.ents:
            if ent.label_ == "DATE":
                dates.append(ent.text)
        
        # Simple heuristic: first date is usually issue date, second is expiry
        if len(dates) >= 1:
            issue_date = dates[0]
        if len(dates) >= 2:
            expiry_date = dates[1]
        
        return issue_date, expiry_date
    
    def _extract_issuing_authority(self, doc: Doc, text: str) -> Optional[str]:
        """Extract issuing authority information."""
        # Search for issuing authority patterns
        authority_patterns = [
            r'Dikeluarkan[:\s]+oleh[:\s]+([^\n]+)',
            r'Issued[:\s]+by[:\s]+([^\n]+)',
        ]
        
        for pattern in authority_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        return None
    
    def get_extraction_stats(self, text: str) -> Dict[str, Any]:
        """
        Get statistics about the extraction process.
        
        Args:
            text: Original text that was processed
            
        Returns:
            Dictionary with extraction statistics
        """
        if self.nlp is None:
            return {}
        
        doc = self.nlp(text)
        
        stats = {
            "text_length": len(text),
            "tokens_count": len(doc),
            "entities_count": len(doc.ents),
            "entity_types": {},
            "sentences_count": len(list(doc.sents)),
        }
        
        # Count entity types
        for ent in doc.ents:
            entity_type = ent.label_
            stats["entity_types"][entity_type] = stats["entity_types"].get(entity_type, 0) + 1
        
        return stats


# Global instance for reuse
_spacy_extraction_service: Optional[SpacyExtractionService] = None


def get_spacy_extraction_service(model_name: str = "id_core_news_sm") -> SpacyExtractionService:
    """
    Get or create a global spaCy extraction service instance.
    
    Args:
        model_name: Name of the spaCy model to use
        
    Returns:
        SpacyExtractionService instance
    """
    global _spacy_extraction_service
    
    if _spacy_extraction_service is None:
        _spacy_extraction_service = SpacyExtractionService(model_name)
    
    return _spacy_extraction_service 