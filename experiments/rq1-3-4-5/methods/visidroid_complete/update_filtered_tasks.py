import pandas as pd
import os

def update_filtered_tasks():
    # Read the original all_tasks.xlsx
    df = pd.read_excel('all_tasks_to_be_update.xlsx')
    print(f"Original all_tasks.xlsx has {len(df)} rows")
    
    # Read the filtered tasks
    filtered_df = pd.read_excel('all_tasks_filtered.xlsx')
    print(f"Filtered tasks has {len(filtered_df)} rows")
    
    # Get the task descriptions from filtered tasks (case-insensitive)
    filtered_task_descs = filtered_df['task_desc'].str.lower().unique()
    print(f"Found {len(filtered_task_descs)} unique filtered task descriptions")
    
    # Remove rows where success == FAILURE for the filtered tasks
    # First, create a mask for rows that match filtered tasks (case-insensitive)
    df_lower = df.copy()
    df_lower['task_desc_lower'] = df['task_desc'].str.lower()
    
    # Create mask for rows to remove (filtered tasks with FAILURE)
    mask_to_remove = (
        df_lower['task_desc_lower'].isin(filtered_task_descs) & 
        (df['success'] == 'FAILURE')
    )
    
    rows_to_remove = df[mask_to_remove]
    print(f"Found {len(rows_to_remove)} rows with FAILURE status to remove")
    
    # Remove the FAILURE rows
    df_cleaned = df[~mask_to_remove]
    print(f"After removing FAILURE rows: {len(df_cleaned)} rows")
    
    # Add the new filtered tasks
    df_updated = pd.concat([df_cleaned, filtered_df], ignore_index=True)
    print(f"After adding filtered tasks: {len(df_updated)} rows")
    
    # Save the updated file
    output_file = 'all_tasks_updated.xlsx'
    df_updated.to_excel(output_file, index=False)
    print(f"Updated data saved to: {output_file}")
    
    # Show summary of changes
    print("\n=== SUMMARY ===")
    print(f"Original rows: {len(df)}")
    print(f"FAILURE rows removed: {len(rows_to_remove)}")
    print(f"New filtered tasks added: {len(filtered_df)}")
    print(f"Final rows: {len(df_updated)}")
    
    # Show which tasks were updated
    if len(rows_to_remove) > 0:
        print(f"\nFAILURE tasks removed:")
        for i, (_, row) in enumerate(rows_to_remove.iterrows(), 1):
            print(f"{i:2d}. {row['app_name']} - {row['task_desc']}")
    
    print(f"\nNew tasks added:")
    for i, (_, row) in enumerate(filtered_df.iterrows(), 1):
        print(f"{i:2d}. {row['app_name']} - {row['task_desc']}")
    
    return df_updated

if __name__ == "__main__":
    updated_df = update_filtered_tasks()
