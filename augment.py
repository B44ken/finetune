#!/usr/bin/env python3
"""
Sentence dropout augmentation for dataset.json.
Generates augmented variations of dataset entries using random sentence dropout.
"""

import json
import os
import sys
import random
import re
from typing import List, Dict, Any


def split_into_sentences(text: str) -> List[str]:
    """Split text into sentences."""
    sentences = re.split(r'(?<=[.!?])\s+', text.strip())
    return [s.strip() for s in sentences if s.strip()]


def random_dropout_augmentation(sentences: List[str], dropout_rate: float = 0.3) -> str:
    """Apply random sentence dropout."""
    if len(sentences) <= 1:
        return ' '.join(sentences)
    kept = [s for s in sentences if random.random() > dropout_rate]
    return ' '.join(kept if kept else [random.choice(sentences)])


def progressive_augmentation(sentences: List[str], max_sentences: int = 2) -> str:
    """Create progressive building (first N sentences)."""
    return ' '.join(sentences[:max_sentences])


def augment_text_content(text: str, dropout_rate: float = 0.3, num_augmentations: int = 3) -> List[str]:
    """Generate augmented variations of text content."""
    sentences = split_into_sentences(text)
    if len(sentences) < 2:
        return []
    
    augmented = []
    for i in range(num_augmentations - 1):
        aug_text = random_dropout_augmentation(sentences, dropout_rate)
        if aug_text and aug_text != text:
            augmented.append(aug_text)
    
    if len(sentences) >= 2:
        prog_text = progressive_augmentation(sentences, min(len(sentences) - 1, 2))
        if prog_text and prog_text != text:
            augmented.append(prog_text)
    
    return augmented


def augment_chatml_entry(entry: Dict[str, Any], dropout_rate: float = 0.3, num_augmentations: int = 3) -> List[Dict[str, Any]]:
    """Augment a ChatML formatted entry."""
    text = entry.get('text', '')
    match = re.search(r'b4444:\s*(.*?)<\|im_end\|>', text, re.DOTALL)
    if not match:
        return []
    
    original_content = match.group(1).strip()
    augmented_texts = augment_text_content(original_content, dropout_rate, num_augmentations)
    
    augmented_entries = []
    for idx, aug_content in enumerate(augmented_texts, start=1):
        aug_entry = entry.copy()
        if not entry.get('source'):
            continue
        aug_entry['source'] = f'{entry["source"]}-aug-{idx}'
        aug_entry['text'] = text.replace(original_content, aug_content)
        augmented_entries.append(aug_entry)
    
    return augmented_entries


def augment_dataset(dataset: List[Dict[str, Any]], dropout_rate: float = 0.3, num_augmentations: int = 3) -> List[Dict[str, Any]]:
    """Augment entire dataset with sentence dropout variations."""
    augmented_dataset = []
    stats = {'augmented': 0, 'skipped': 0}
    
    for entry in dataset:
        augmented_dataset.append(entry)  # Always keep original
        augmented_entries = augment_chatml_entry(entry, dropout_rate, num_augmentations)
        augmented_dataset.extend(augmented_entries)
        if augmented_entries:
            stats['augmented'] += 1
        else:
            stats['skipped'] += 1
    
    print(f"Augmentation statistics:", file=sys.stderr)
    print(f"  Total original entries: {len(dataset)}", file=sys.stderr)
    print(f"  Successfully augmented: {stats['augmented']}", file=sys.stderr)
    print(f"  Skipped: {stats['skipped']}", file=sys.stderr)
    print(f"  Total output entries: {len(augmented_dataset)}", file=sys.stderr)
    
    return augmented_dataset


def load_dataset(filename: str = 'dataset.json') -> List[Dict[str, Any]]:
    """Load dataset from JSON file."""
    return json.load(open(filename))


def save_dataset(dataset: List[Dict[str, Any]], filename: str = 'dataset.json'):
    """Save dataset to JSON file."""
    json.dump(dataset, open(filename, 'w'), indent=2, ensure_ascii=False)
    print(f"Saved {len(dataset)} entries to {filename}", file=sys.stderr)


def main():
    """Main function to augment dataset."""
    if len(sys.argv) > 1 and sys.argv[1] in ['-h', '--help']:
        print("Usage: python3 augment.py [input_file] [output_file] [dropout_rate] [num_augmentations]")
        return 0
    
    input_file = sys.argv[1] if len(sys.argv) > 1 else 'dataset.json'
    output_file = sys.argv[2] if len(sys.argv) > 2 else input_file
    dropout_rate = float(sys.argv[3]) if len(sys.argv) > 3 else 0.3
    num_augmentations = int(sys.argv[4]) if len(sys.argv) > 4 else 3
    
    print(f"Augmentation configuration:", file=sys.stderr)
    print(f"  Input: {input_file}", file=sys.stderr)
    print(f"  Output: {output_file}", file=sys.stderr)
    print(f"  Dropout rate: {dropout_rate}", file=sys.stderr)
    print(f"  Augmentations per entry: {num_augmentations}", file=sys.stderr)
    
    dataset = load_dataset(input_file)
    augmented = augment_dataset(dataset, dropout_rate, num_augmentations)
    save_dataset(augmented, output_file)
    return 0


if __name__ == '__main__':
    sys.exit(main())
