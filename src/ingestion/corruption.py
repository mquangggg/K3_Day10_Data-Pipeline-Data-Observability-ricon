from __future__ import annotations

import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta


def corrupt_clean_dataframe(df: pd.DataFrame, output_log_path) -> pd.DataFrame:
    """Simulate many types of data corruption.
    
    Pseudo-code:
    1. Drop some latest records.
    2. Blank summary on some rows.
    3. Inject noise into text.
    4. Make title be truncated.
    5. Make published date be wrong.
    6. Add duplicate rows.
    7. Rebuild `text_for_embedding`.
    8. Write corruption log to output_log_path.
    """
    # Make a copy to avoid modifying the original
    corrupted_df = df.copy()
    
    # 1. Drop some latest records
    num_drop = min(len(corrupted_df) // 10, 3)  # Drop 10% or max 3 records
    if num_drop > 0:
        drop_indices = random.sample(range(len(corrupted_df)), num_drop)
        corrupted_df = corrupted_df.drop(drop_indices).reset_index(drop=True)
    
    # 2. Blank summary on some rows
    num_blank = min(len(corrupted_df) // 5, 2)  # Blank 20% or max 2 summaries
    if num_blank > 0:
        blank_indices = random.sample(range(len(corrupted_df)), num_blank)
        corrupted_df.loc[blank_indices, 'summary'] = ''
    
    # 3. Inject noise into text (authors, title, categories)
    num_noise = min(len(corrupted_df) // 4, 2)  # Apply noise to 25% or max 2 rows
    if num_noise > 0:
        noise_indices = random.sample(range(len(corrupted_df)), num_noise)
        for idx in noise_indices:
            # Add random characters to title
            title = corrupted_df.loc[idx, 'title']
            if len(title) > 10:
                pos = random.randint(0, len(title) - 1)
                corrupted_df.loc[idx, 'title'] = title[:pos] + random.choice('abcdefghijklmnopqrstuvwxyz') + title[pos:]
            
            # Add random characters to authors
            authors = corrupted_df.loc[idx, 'authors_joined']
            if len(authors) > 10:
                pos = random.randint(0, len(authors) - 1)
                corrupted_df.loc[idx, 'authors_joined'] = authors[:pos] + random.choice('abcdefghijklmnopqrstuvwxyz') + authors[pos:]
            
            # Add random characters to categories
            categories = corrupted_df.loc[idx, 'categories_joined']
            if len(categories) > 10:
                pos = random.randint(0, len(categories) - 1)
                corrupted_df.loc[idx, 'categories_joined'] = categories[:pos] + random.choice('abcdefghijklmnopqrstuvwxyz') + categories[pos:]
    
    # 4. Make title be truncated
    num_truncate = min(len(corrupted_df) // 6, 2)  # Truncate 16.6% or max 2 titles
    if num_truncate > 0:
        truncate_indices = random.sample(range(len(corrupted_df)), num_truncate)
        for idx in truncate_indices:
            title = corrupted_df.loc[idx, 'title']
            if len(title) > 10:
                # Truncate to random length
                new_length = random.randint(5, min(len(title) - 1, 15))
                corrupted_df.loc[idx, 'title'] = title[:new_length]
    
    # 5. Make published date be wrong
    num_wrong_date = min(len(corrupted_df) // 8, 2)  # Wrong date for 12.5% or max 2 rows
    if num_wrong_date > 0:
        wrong_date_indices = random.sample(range(len(corrupted_df)), num_wrong_date)
        for idx in wrong_date_indices:
            # Generate a random date in the past
            days_back = random.randint(1, 3650)  # Up to 10 years back
            random_date = datetime.now() - timedelta(days=days_back)
            corrupted_df.loc[idx, 'published'] = random_date.strftime('%Y-%m-%d')
    
    # 6. Add duplicate rows
    num_duplicates = min(len(corrupted_df) // 10, 2)  # Add 10% or max 2 duplicates
    if num_duplicates > 0:
        duplicate_indices = random.sample(range(len(corrupted_df)), num_duplicates)
        for idx in duplicate_indices:
            # Get the row to duplicate
            row_to_dup = corrupted_df.iloc[idx].copy()
            # Add a small modification to make it slightly different
            row_to_dup['paper_id'] = f"{row_to_dup['paper_id']}_dup"
            # Append the duplicated row
            corrupted_df = pd.concat([corrupted_df, row_to_dup.to_frame().T], ignore_index=True)
    
    # 7. Rebuild `text_for_embedding`
    def rebuild_text_for_embedding(row):
        # Combine title, summary, authors, categories
        text_parts = [
            row.get('title', ''),
            row.get('summary', ''),
            row.get('authors_joined', ''),
            row.get('categories_joined', '')
        ]
        return ' '.join(part.strip() for part in text_parts if part)
    
    corrupted_df['text_for_embedding'] = corrupted_df.apply(rebuild_text_for_embedding, axis=1)
    
    # 8. Write corruption log to output_log_path
    corruption_log = {
        "timestamp": datetime.now().isoformat(),
        "original_row_count": len(df),
        "corrupted_row_count": len(corrupted_df),
        "corruptions_applied": {
            "dropped_records": num_drop,
            "blank_summaries": num_blank,
            "noise_injected": num_noise,
            "titles_truncated": num_truncate,
            "wrong_dates": num_wrong_date,
            "duplicate_rows_added": num_duplicates
        }
    }
    
    # Save log to file
    import json
    with open(output_log_path, 'w') as f:
        json.dump(corruption_log, f, indent=2)
    
    return corrupted_df