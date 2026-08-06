from __future__ import annotations

import json
import uuid
from typing import Any

import pandas as pd


def build_test_set(df: pd.DataFrame, output_path) -> list[dict[str, Any]]:
    """Tao bo evaluation set tu cleaned dataframe."""
    if len(df) == 0:
        return []
    
    # 1. Kiem tra so luong document & 2. Chon 5 paper dai dien
    sample_df = df.sample(min(5, len(df)), random_state=42)
    test_set = []
    
    for _, row in sample_df.iterrows():
        # paper_id is the stable ID from Crossref
        doc_id = str(row.get('paper_id', ''))
        title = row.get('title', 'Unknown Title')
        if not doc_id:
            continue
            
        # 3. Tao nhieu loai cau hoi & 4. Moi row can co cac field yeu cau
        # Cau hoi ve tac gia
        authors_val = row.get('authors')
        if authors_val is not None and len(authors_val) > 0:
            test_set.append({
                "id": str(uuid.uuid4()),
                "question_type": "authors",
                "question": f"Ai là tác giả của bài báo '{title}'?",
                "ground_truth": str(authors_val),
                "ground_truth_doc_ids": [doc_id]
            })
            
        # Cau hoi ve summary
        summary_val = row.get('summary')
        if summary_val is not None and str(summary_val).strip() != "":
            test_set.append({
                "id": str(uuid.uuid4()),
                "question_type": "summary",
                "question": f"Tóm tắt nội dung chính của bài báo '{title}' là gì?",
                "ground_truth": str(summary_val),
                "ground_truth_doc_ids": [doc_id]
            })
            
        # Cau hoi ve ngay xuat ban
        published_val = row.get('published')
        if published_val is not None and str(published_val).strip() != "":
            test_set.append({
                "id": str(uuid.uuid4()),
                "question_type": "date",
                "question": f"Bài báo '{title}' được xuất bản khi nào?",
                "ground_truth": str(published_val),
                "ground_truth_doc_ids": [doc_id]
            })
            
        # Cau hoi ve categories
        categories_val = row.get('categories')
        if categories_val is not None and len(categories_val) > 0:
            test_set.append({
                "id": str(uuid.uuid4()),
                "question_type": "categories",
                "question": f"Chủ đề của bài báo '{title}' là gì?",
                "ground_truth": str(categories_val),
                "ground_truth_doc_ids": [doc_id]
            })

            
    # 5. Ghi file JSON vao output_path
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(test_set, f, ensure_ascii=False, indent=4)
        
    return test_set
