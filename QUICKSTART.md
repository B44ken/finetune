# Quick Start Guide

## Install
```bash
pip install requests
```

## Usage

### 1. Scrape Reddit
```bash
python3 reddit_scraper.py B44ken 100
```

### 2. Add Discord data (if you have `*-*.json` files)
```bash
python3 merge.py -t dataset
```

### 3. Augment
```bash
python3 augment.py dataset.json dataset.json 0.3 2
```

## Output

`dataset.json` with:
- Source tracking (`reddit-{id}`, `discord-{hash}`, `{source}-aug-{N}`)
- ChatML format
- Duplicate detection
- Augmented variations

## Files

- `reddit_scraper.py` - Scrapes u/B44ken posts/comments
- `merge.py` - Processes Discord JSON files (`-t dataset` mode)
- `augment.py` - Sentence dropout augmentation
- `dataset.json` - Output dataset

## Notes

This is an ML experiment script - minimal error handling by design.
If files are malformed or missing, it will error and you can fix them.
