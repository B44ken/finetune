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
    """
    Split text into sentences using simple heuristics.
    
    Args:
        text: Input text to split
        
    Returns:
        List of sentences
    """
    # Use regex to split on common sentence boundaries
    # This handles periods, question marks, exclamation marks followed by space or end
    sentences = re.split(r'(?<=[.!?])\s+', text.strip())
    # Filter out empty sentences
    return [s.strip() for s in sentences if s.strip()]


def random_dropout_augmentation(sentences: List[str], dropout_rate: float = 0.3) -> str:
    """
    Apply random sentence dropout.
    
    Args:
        sentences: List of sentences
        dropout_rate: Probability of dropping each sentence (0.0-1.0)
        
    Returns:
        Text with random sentences dropped
    """
    if len(sentences) <= 1:
        return ' '.join(sentences)
    
    # Keep at least one sentence
    kept_sentences = [s for s in sentences if random.random() > dropout_rate]
    if not kept_sentences:
        # If all dropped, keep a random one
        kept_sentences = [random.choice(sentences)]
    
    return ' '.join(kept_sentences)


def progressive_augmentation(sentences: List[str], max_sentences: int = 2) -> str:
    """
    Create progressive building augmentation (first N sentences).
    
    Args:
        sentences: List of sentences
        max_sentences: Maximum number of sentences to include
        
    Returns:
        Text with first N sentences
    """
    return ' '.join(sentences[:max_sentences])


def augment_text_content(text: str, dropout_rate: float = 0.3, num_augmentations: int = 3) -> List[str]:
    """
    Generate augmented variations of text content.
    
    Args:
        text: Original text content
        dropout_rate: Dropout rate for random dropout (0.0-1.0)
        num_augmentations: Number of augmented versions to generate
        
    Returns:
        List of augmented text variations (does not include original)
    """
    sentences = split_into_sentences(text)
    
    # Skip augmentation if too few sentences
    if len(sentences) < 2:
        return []
    
    augmented = []
    
    # Generate random dropout variations
    for i in range(num_augmentations - 1):
        aug_text = random_dropout_augmentation(sentences, dropout_rate)
        if aug_text and aug_text != text:  # Don't add if identical to original
            augmented.append(aug_text)
    
    # Generate one progressive building variation
    if len(sentences) >= 2:
        prog_text = progressive_augmentation(sentences, min(len(sentences) - 1, 2))
        if prog_text and prog_text != text:
            augmented.append(prog_text)
    
    return augmented


def augment_chatml_entry(entry: Dict[str, Any], dropout_rate: float = 0.3, num_augmentations: int = 3) -> List[Dict[str, Any]]:
    """
    Augment a ChatML formatted entry.
    
    Args:
        entry: Original dataset entry with 'text' field in ChatML format
        dropout_rate: Dropout rate for augmentation
        num_augmentations: Number of augmented versions to generate
        
    Returns:
        List of augmented entries with updated source identifiers
    """
    augmented_entries = []
    
    # Extract the content to augment from ChatML format
    # Look for assistant content (b4444's responses)
    text = entry.get('text', '')
    
    # Find assistant content after "b4444: " prefix
    match = re.search(r'b4444:\s*(.*?)<\|im_end\|>', text, re.DOTALL)
    if not match:
        # No assistant content found, skip augmentation
        return []
    
    original_content = match.group(1).strip()
    
    # Generate augmented versions
    augmented_texts = augment_text_content(original_content, dropout_rate, num_augmentations)
    
    # Create augmented entries
    for idx, aug_content in enumerate(augmented_texts, start=1):
        # Create a copy of the entry
        aug_entry = entry.copy()
        
        # Update source with augmentation suffix
        original_source = entry.get('source', f'unknown-{random.randint(1000, 9999)}')
        aug_entry['source'] = f'{original_source}-aug-{idx}'
        
        # Replace content in ChatML format
        aug_entry['text'] = text.replace(original_content, aug_content)
        
        augmented_entries.append(aug_entry)
    
    return augmented_entries


def augment_dataset(
    dataset: List[Dict[str, Any]], 
    dropout_rate: float = 0.3, 
    num_augmentations: int = 3,
    preserve_original: bool = True
) -> List[Dict[str, Any]]:
    """
    Augment entire dataset with sentence dropout variations.
    
    Args:
        dataset: Original dataset
        dropout_rate: Dropout rate for augmentation (0.0-1.0)
        num_augmentations: Number of augmented versions per entry
        preserve_original: Whether to keep original entries in output
        
    Returns:
        Augmented dataset
    """
    augmented_dataset = []
    
    # Track statistics
    total_entries = len(dataset)
    augmented_count = 0
    skipped_count = 0
    
    for entry in dataset:
        # Always include original if requested
        if preserve_original:
            augmented_dataset.append(entry)
        
        # Generate augmented versions
        try:
            augmented_entries = augment_chatml_entry(entry, dropout_rate, num_augmentations)
            augmented_dataset.extend(augmented_entries)
            
            if augmented_entries:
                augmented_count += 1
            else:
                skipped_count += 1
                
        except Exception as e:
            print(f"Error augmenting entry {entry.get('source', 'unknown')}: {e}", file=sys.stderr)
            skipped_count += 1
    
    print(f"Augmentation statistics:", file=sys.stderr)
    print(f"  Total original entries: {total_entries}", file=sys.stderr)
    print(f"  Successfully augmented: {augmented_count}", file=sys.stderr)
    print(f"  Skipped: {skipped_count}", file=sys.stderr)
    print(f"  Total output entries: {len(augmented_dataset)}", file=sys.stderr)
    
    return augmented_dataset


def load_dataset(filename: str = 'dataset.json') -> List[Dict[str, Any]]:
    """Load dataset from JSON file."""
    if not os.path.exists(filename):
        print(f"Error: {filename} not found", file=sys.stderr)
        return []
    
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        print(f"Error loading {filename}: {e}", file=sys.stderr)
        return []


def save_dataset(dataset: List[Dict[str, Any]], filename: str = 'dataset.json'):
    """Save dataset to JSON file."""
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(dataset, f, indent=2, ensure_ascii=False)
    print(f"Saved {len(dataset)} entries to {filename}", file=sys.stderr)


def main():
    """Main function to augment dataset."""
    # Parse command line arguments
    input_file = sys.argv[1] if len(sys.argv) > 1 else 'dataset.json'
    output_file = sys.argv[2] if len(sys.argv) > 2 else input_file
    dropout_rate = float(sys.argv[3]) if len(sys.argv) > 3 else 0.3
    num_augmentations = int(sys.argv[4]) if len(sys.argv) > 4 else 3
    
    print(f"Augmentation configuration:", file=sys.stderr)
    print(f"  Input: {input_file}", file=sys.stderr)
    print(f"  Output: {output_file}", file=sys.stderr)
    print(f"  Dropout rate: {dropout_rate}", file=sys.stderr)
    print(f"  Augmentations per entry: {num_augmentations}", file=sys.stderr)
    
    # Load dataset
    dataset = load_dataset(input_file)
    if not dataset:
        return 1
    
    # Augment dataset
    augmented = augment_dataset(dataset, dropout_rate, num_augmentations, preserve_original=True)
    
    # Save augmented dataset
    save_dataset(augmented, output_file)
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
