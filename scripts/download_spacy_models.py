#!/usr/bin/env python3
"""
Download spaCy models for OCR identity document processing.
This script downloads and installs the necessary spaCy models for Indonesian and English text processing.
"""

import subprocess
import sys
import os
from pathlib import Path


def run_command(command: str, description: str) -> bool:
    """Run a command and return success status."""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(
            command.split(),
            capture_output=True,
            text=True,
            check=True
        )
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed:")
        print(f"Error: {e.stderr}")
        return False
    except FileNotFoundError:
        print(f"❌ Command not found: {command.split()[0]}")
        return False


def check_spacy_installation() -> bool:
    """Check if spaCy is installed."""
    try:
        import spacy
        print(f"✅ spaCy {spacy.__version__} is installed")
        return True
    except ImportError:
        print("❌ spaCy is not installed. Please install it first:")
        print("   poetry install")
        return False


def download_models() -> bool:
    """Download spaCy models for Indonesian and English."""
    models = [
        ("en_core_web_sm", "English (small)"),
        ("en_core_web_md", "English (medium)"),
        ("id_core_news_sm", "Indonesian (small)"),
        ("id_core_news_md", "Indonesian (medium)"),
    ]
    
    success_count = 0
    
    for model, description in models:
        print(f"\n📦 Downloading {description} model: {model}")
        
        # Try to download using spacy download
        if run_command(f"python -m spacy download {model}", f"Downloading {model}"):
            success_count += 1
        else:
            print(f"⚠️  Failed to download {model} using spacy download")
            
            # Try alternative method using pip
            pip_command = f"pip install {model}"
            if run_command(pip_command, f"Installing {model} via pip"):
                success_count += 1
            else:
                print(f"❌ Failed to install {model}")
    
    return success_count == len(models)


def verify_models() -> bool:
    """Verify that the models are properly installed."""
    print("\n🔍 Verifying model installation...")
    
    try:
        import spacy
        
        models_to_test = [
            "en_core_web_sm",
            "en_core_web_md", 
            "id_core_news_sm",
            "id_core_news_md"
        ]
        
        for model_name in models_to_test:
            try:
                nlp = spacy.load(model_name)
                print(f"✅ {model_name} loaded successfully")
                
                # Test basic functionality
                test_text = "This is a test document for identity processing."
                doc = nlp(test_text)
                print(f"   - Entities found: {len(doc.ents)}")
                print(f"   - Pipeline components: {nlp.pipe_names}")
                
            except OSError as e:
                print(f"❌ {model_name} failed to load: {e}")
                return False
                
        return True
        
    except Exception as e:
        print(f"❌ Error during model verification: {e}")
        return False


def create_custom_model_config() -> None:
    """Create a custom spaCy configuration for identity document processing."""
    config_content = """
# Custom spaCy configuration for identity document processing
[paths]
train = "corpus"
vectors = null
init_tok2vec = null

[system]
gpu_allocator = null

[nlp]
lang = "id"
pipeline = ["tok2vec", "tagger", "parser", "ner", "attribute_ruler", "lemmatizer"]
batch_size = 1000

[components]

[components.tok2vec]
factory = "tok2vec"

[components.tok2vec.model]
@architectures = "spacy.Tok2Vec.v2"

[components.tok2vec.model.embed]
@architectures = "spacy.MultiHashEmbed.v2"
width = 312
rows = [5000, 2000, 1000, 1000]
attrs = ["NORM", "PREFIX", "SUFFIX", "SHAPE"]
include_static_vectors = true

[components.tok2vec.model.encode]
@architectures = "spacy.MaxoutWindowEncoder.v2"
width = 312
window_size = 1
maxout_pieces = 3
depth = 4

[components.tagger]
factory = "tagger"

[components.tagger.model]
@architectures = "spacy.Tagger.v2"
tok2vec = @components.tok2vec.model

[components.parser]
factory = "parser"

[components.parser.model]
@architectures = "spacy.TransitionBasedParser.v2"
state_type = "parser"
extra_state_tokens = false
include_features = {"bias": true, "prev": {"window": 1}, "curr": {"window": 1}, "next": {"window": 1}, "prev_stack": {"window": 3}, "curr_stack": {"window": 3}}
tok2vec = @components.tok2vec.model

[components.ner]
factory = "ner"

[components.ner.model]
@architectures = "spacy.TransitionBasedParser.v2"
state_type = "ner"
extra_state_tokens = false
include_features = {"bias": true, "prev": {"window": 1}, "curr": {"window": 1}, "next": {"window": 1}, "prev_stack": {"window": 3}, "curr_stack": {"window": 3}}
tok2vec = @components.tok2vec.model

[components.attribute_ruler]
factory = "attribute_ruler"

[components.lemmatizer]
factory = "lemmatizer"

[corpora]

[corpora.dev]
@readers = "spacy.Corpus.v1"
path = ${paths.dev}
max_length = 0

[corpora.train]
@readers = "spacy.Corpus.v1"
path = ${paths.train}
max_length = 0

[training]
dev_corpus = "corpora.dev"
train_corpus = "corpora.train"

[training.optimizer]
@optimizers = "Adam.v1"

[training.batcher]
@batchers = "spacy.batch_by_words.v2"
discard_oversize = false
size = 2000
tolerance = 0.2

[training.logger]
@loggers = "spacy.ConsoleLogger.v1"
progress_bar = false

[training.optimizer.learn_rate]
@schedules = "warmup_linear.v1"
warmup_steps = 250
total_steps = 20000
initial_rate = 0.025
peak_rate = 0.1
final_rate = 0.001

[training.score_weights]
ner_f = 1.0
ner_p = 0.0
ner_r = 0.0
ner_per_type_f = 0.0
ner_per_type_p = 0.0
ner_per_type_r = 0.0
"""
    
    config_path = Path("config.cfg")
    with open(config_path, "w") as f:
        f.write(config_content.strip())
    
    print(f"✅ Created custom spaCy configuration: {config_path}")


def main():
    """Main function to download and setup spaCy models."""
    print("🚀 spaCy Model Downloader for OCR Identity Processing")
    print("=" * 60)
    
    # Check spaCy installation
    if not check_spacy_installation():
        sys.exit(1)
    
    # Download models
    if not download_models():
        print("\n⚠️  Some models failed to download. Continuing with verification...")
    
    # Verify models
    if not verify_models():
        print("\n❌ Model verification failed. Please check the installation.")
        sys.exit(1)
    
    # Create custom configuration
    create_custom_model_config()
    
    print("\n🎉 spaCy model setup completed successfully!")
    print("\n📋 Next steps:")
    print("1. Test the models with your identity document processing")
    print("2. Fine-tune models with your specific document types")
    print("3. Update the extraction logic to use spaCy NER")
    
    print("\n🔧 Usage example:")
    print("""
import spacy

# Load Indonesian model
nlp = spacy.load("id_core_news_sm")

# Process identity document text
text = "NIK: 1234567890123456\\nNama: John Doe\\nTempat/Tgl Lahir: Jakarta, 01-01-1990"
doc = nlp(text)

# Extract entities
for ent in doc.ents:
    print(f"{ent.text} - {ent.label_}")
    """)


if __name__ == "__main__":
    main() 