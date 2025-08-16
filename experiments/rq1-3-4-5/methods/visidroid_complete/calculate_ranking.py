import pandas as pd
import re

def word_match_score(candidate: str, gt: str) -> int:
    """Calculate word match score between candidate and ground truth"""
    # Clean the strings: keep only letters, digits, and spaces
    clean = lambda s: re.sub(r'[^a-zA-Z0-9\s]', '', s).lower().split()

    candidate_words = set(clean(candidate))
    gt_words = set(clean(gt))

    return len(candidate_words & gt_words)

def calculate_ranking_scores():
    """Calculate related_score for tasks that don't have it"""
    
    # Read the updated CSV file
    input_file = 'hai-visidroid-results-with-score-updated.csv'
    print(f"Reading {input_file}...")
    df = pd.read_csv(input_file)
    print(f"File has {len(df)} rows")
    
    # Count tasks that need ranking calculation
    tasks_needing_score = df[df['related_score'].isna()]
    print(f"Tasks needing score calculation: {len(tasks_needing_score)}")
    
    # Count tasks that already have scores
    tasks_with_score = df[df['related_score'].notna()]
    print(f"Tasks with existing scores: {len(tasks_with_score)}")
    
    # Calculate scores for tasks that don't have them
    updated_count = 0
    for idx, row in df.iterrows():
        if pd.isna(row['related_score']):
            # Get the soa and task_desc
            soa = row['soa']
            task_desc = row['task_desc']
            
            # Calculate word match score
            score = word_match_score(soa, task_desc)
            
            # Update the related_score
            df.at[idx, 'related_score'] = score
            updated_count += 1
            
            print(f"Updated task {idx}: {task_desc} -> score {score}")
    
    # Save the updated file
    output_file = 'hai-visidroid-results-with-score-ranked.csv'
    df.to_csv(output_file, index=False)
    
    print(f"\nRanking Summary:")
    print(f"Total tasks processed: {len(df)}")
    print(f"Tasks with existing scores: {len(tasks_with_score)}")
    print(f"Tasks with new scores: {updated_count}")
    print(f"Updated file saved as: {output_file}")
    
    # Show score distribution
    score_counts = df['related_score'].value_counts().sort_index()
    print(f"\nScore distribution:")
    for score, count in score_counts.items():
        print(f"  Score {score}: {count} tasks")
    
    return df

if __name__ == "__main__":
    df = calculate_ranking_scores()
