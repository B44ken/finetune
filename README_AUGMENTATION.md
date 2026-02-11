# Data Augmentation System

This repository includes a comprehensive data augmentation system for building training datasets from Discord and Reddit sources.

## Components

### 1. Reddit Scraper (`reddit_scraper.py`)

Fetches posts and comments from a Reddit user and converts them to ChatML format.

**Usage:**
```bash
python3 reddit_scraper.py [username] [limit]
```

**Arguments:**
- `username`: Reddit username to scrape (default: `B44ken`)
- `limit`: Maximum number of posts/comments to fetch (default: `100`)

**Output:**
- Adds entries to `dataset.json` with source format: `reddit-{post_id}`
- Automatically merges with existing dataset entries
- Skips duplicates based on source field

**Example:**
```bash
python3 reddit_scraper.py B44ken 50
```

**Features:**
- Fetches both submissions (posts) and comments
- Converts to ChatML format compatible with training pipeline
- Filters out code blocks and URLs
- Length filtering (80-2000 characters)
- Duplicate detection via source field

### 2. Discord Scraper Integration (`merge.py`)

Updated to include source tracking and dataset.json integration.

**Usage:**
```bash
python3 merge.py -t dataset
```

**Output Modes:**
- `-t stats`: Show statistics only (default)
- `-t plain`: Plain text output
- `-t llm`: JSON format (legacy)
- `-t dataset`: Add to `dataset.json` with source tracking

**Source Format:**
- Discord entries: `discord-{hash}` (SHA256 hash of conversation content, 16 chars)

**Example:**
```bash
# Process Discord JSON files in current directory
python3 merge.py -t dataset
```

### 3. Sentence Dropout Augmentation (`augment.py`)

Generates augmented variations using sentence dropout and progressive building strategies.

**Usage:**
```bash
python3 augment.py [input_file] [output_file] [dropout_rate] [num_augmentations]
```

**Arguments:**
- `input_file`: Input dataset JSON file (default: `dataset.json`)
- `output_file`: Output dataset JSON file (default: same as input)
- `dropout_rate`: Probability of dropping each sentence, 0.0-1.0 (default: `0.3`)
- `num_augmentations`: Number of augmented versions per entry (default: `3`)

**Output:**
- Preserves original entries
- Adds augmented entries with source format: `{original_source}-aug-{N}`
- Example: `reddit-abc123-aug-1`, `discord-xyz789-aug-2`

**Example:**
```bash
# Augment with default settings (30% dropout, 3 variations)
python3 augment.py dataset.json dataset.json

# Custom settings: 40% dropout, 2 variations
python3 augment.py dataset.json augmented.json 0.4 2
```

**Augmentation Strategies:**
1. **Random Sentence Dropout**: Randomly removes 20-40% of sentences
2. **Progressive Building**: Includes first N sentences (2-3 max)
3. **Original**: Always preserved in output

**Features:**
- Maintains semantic coherence
- Skips entries with fewer than 2 sentences
- Tracks augmentation lineage via source suffix
- Configurable dropout rate and augmentation count

## Dataset Format

All tools work with a unified `dataset.json` format:

```json
[
  {
    "source": "reddit-abc123",
    "text": "<|im_start|>system\n...<|im_end|>\n<|im_start|>assistant\n...<|im_end|>",
    "subreddit": "example",
    "created_utc": 1700000000,
    "score": 10
  },
  {
    "source": "reddit-abc123-aug-1",
    "text": "<|im_start|>system\n...<|im_end|>\n<|im_start|>assistant\n...<|im_end|>",
    "subreddit": "example",
    "created_utc": 1700000000,
    "score": 10
  },
  {
    "source": "discord-xyz789",
    "text": "<|im_start|>system\n...<|im_end|>\n..."
  }
]
```

### Source Field

The `source` field enables:
- **Duplicate detection**: Same source = duplicate entry
- **Augmentation tracking**: Suffix `-aug-N` links to original
- **Data lineage**: Track whether data is from Reddit, Discord, or augmented

## Complete Workflow

1. **Scrape Reddit data:**
   ```bash
   python3 reddit_scraper.py B44ken 100
   ```

2. **Add Discord data** (if you have Discord JSON files):
   ```bash
   python3 merge.py -t dataset
   ```

3. **Generate augmentations:**
   ```bash
   python3 augment.py dataset.json dataset.json 0.3 2
   ```

4. **Use in training:**
   - The `dataset.json` file is ready for training
   - Each entry has a `text` field in ChatML format
   - Compatible with the existing Kaggle notebook training pipeline

## Configuration

### Reddit Scraper
- Minimum content length: 80 characters
- Maximum content length: 2000 characters
- Filters: code blocks (```), URLs (https://)

### Discord Scraper
- Time gap threshold: 1 hour (3600 seconds)
- Minimum messages: 2
- Maximum messages: 4
- Same length and filter rules as Reddit

### Augmentation
- Default dropout rate: 0.3 (30%)
- Configurable range: 0.2-0.4 (20%-40%)
- Default augmentations per entry: 2-3
- Minimum sentences for augmentation: 2

## Requirements

```bash
pip install requests
```

Note: The scripts use Python's built-in `re` module for sentence splitting. For more advanced sentence tokenization, you could optionally use `nltk` or `spacy`, but they are not required.

## Notes

- All tools automatically handle merging with existing `dataset.json`
- Duplicate detection prevents re-adding the same content
- Original entries are always preserved during augmentation
- The system is designed to work with the existing Qwen model training pipeline
