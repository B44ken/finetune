# Data Augmentation

## Scripts

**reddit_scraper.py** - scrapes u/B44ken posts/comments, outputs to dataset.json
```bash
python3 reddit_scraper.py [username] [limit]
```

**merge.py** - processes Discord JSON files
```bash
python3 merge.py -t dataset  # adds to dataset.json
python3 merge.py -t llm      # outputs JSON to stdout
python3 merge.py -t stats    # shows count
```

**augment.py** - sentence dropout augmentation
```bash
python3 augment.py [input] [output] [dropout_rate] [n_augmentations]
# defaults: dataset.json dataset.json 0.3 2
```

## Dataset Format

All output to `dataset.json`:
```json
[
  {"source": "reddit-abc123", "text": "<|im_start|>..."},
  {"source": "reddit-abc123-aug-1", "text": "..."},
  {"source": "discord-f3a2b1c4", "text": "..."}
]
```

Source field = deduplication. `-aug-N` suffix = augmented.

## Workflow

```bash
python3 reddit_scraper.py B44ken 100
python3 merge.py -t dataset
python3 augment.py
```

Done. dataset.json ready for training.
