import pandas as pd
import hashlib

def get_task_hash(app_name, task_desc):
    """Generate hash for task matching with ground truth"""
    task_string = f"{app_name}: {task_desc}"
    return hashlib.sha256(task_string.encode()).hexdigest()

def clean_action_sequence(history_action):
    """Clean the action sequence by removing 'Jade Green' prefix and fixing formatting"""
    if not history_action:
        return ""
    
    # Remove 'Jade Green' prefix from each action
    lines = history_action.strip().split('\n')
    cleaned_lines = []
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        # Remove 'Jade Green' prefix
        if line.startswith('- ACTION'):
            # Find the position after "ACTION X: "
            action_parts = line.split(': ', 1)
            if len(action_parts) == 2:
                action_header = action_parts[0] + ': '
                action_content = action_parts[1]
                
                # Remove 'Jade Green ' prefix from action content
                if action_content.startswith('Jade Green '):
                    action_content = action_content[11:]  # Remove 'Jade Green '
                
                cleaned_line = action_header + action_content
                cleaned_lines.append(cleaned_line)
            else:
                cleaned_lines.append(line)
        else:
            cleaned_lines.append(line)
    
    return '\n'.join(cleaned_lines)

def extract_app_name_from_task(task_desc):
    """Extract app name from task description"""
    # Common app names in the dataset
    app_names = [
        'applauncher', 'calendar', 'camera', 'clock', 'contacts', 
        'dialer', 'filemanager', 'firefox', 'gallery', 'messenger', 
        'musicplayer', 'notes', 'voicerecorder'
    ]
    
    task_lower = task_desc.lower()
    for app in app_names:
        if app in task_lower:
            return app
    
    # If no app name found, try to extract from common patterns
    if 'calendar' in task_lower or 'event' in task_lower:
        return 'calendar'
    elif 'photo' in task_lower or 'image' in task_lower or 'gallery' in task_lower:
        return 'gallery'
    elif 'contact' in task_lower:
        return 'contacts'
    elif 'call' in task_lower or 'dial' in task_lower:
        return 'dialer'
    elif 'note' in task_lower:
        return 'notes'
    elif 'music' in task_lower or 'song' in task_lower:
        return 'musicplayer'
    elif 'voice' in task_lower or 'record' in task_lower:
        return 'voicerecorder'
    elif 'file' in task_lower:
        return 'filemanager'
    elif 'browser' in task_lower or 'web' in task_lower:
        return 'firefox'
    elif 'alarm' in task_lower or 'timer' in task_lower:
        return 'clock'
    elif 'camera' in task_lower or 'photo' in task_lower:
        return 'camera'
    else:
        return 'unknown'

def update_results_with_rerun():
    """Replace tasks in hai-visidroid-results-with-score.csv with rerun failed tasks"""
    
    # Read the main results file
    main_file = 'hai-visidroid-results-with-score.csv'
    rerun_file = 'rerun_failed_task.csv'
    
    print(f"Reading {main_file}...")
    main_df = pd.read_csv(main_file)
    print(f"Main file has {len(main_df)} rows")
    
    # Count unique tasks in main file
    unique_main_tasks = main_df[['app_name', 'task_desc']].drop_duplicates()
    print(f"Main file has {len(unique_main_tasks)} unique tasks")
    
    print(f"Reading {rerun_file}...")
    rerun_df = pd.read_csv(rerun_file)
    print(f"Rerun file has {len(rerun_df)} rows")
    
    # Count unique tasks in rerun file
    unique_rerun_tasks = rerun_df['Task'].drop_duplicates()
    print(f"Rerun file has {len(unique_rerun_tasks)} unique tasks")
    
    # Create a new dataframe for the updated results
    updated_rows = []
    
    # Track which tasks have been replaced (by task description only)
    replaced_tasks = set()
    
    # Process each rerun task
    for idx, rerun_row in rerun_df.iterrows():
        task_desc = rerun_row['Task']
        task_result = rerun_row['Task Result']
        steps_count = rerun_row['Steps Count']
        history_action = rerun_row['History Action']
        
        # Extract app name from task description
        app_name = extract_app_name_from_task(task_desc)
        
        # Clean the action sequence
        cleaned_soa = clean_action_sequence(history_action)
        
        # Find matching task in main dataframe by task description only
        # Try exact match first
        matches = main_df[main_df['task_desc'] == task_desc]
        
        if len(matches) == 0:
            # Try case-insensitive match
            matches = main_df[main_df['task_desc'].str.lower() == task_desc.lower()]
        
        if len(matches) == 0:
            # Try partial match
            matches = main_df[main_df['task_desc'].str.contains(task_desc, case=False, na=False)]
        
        if len(matches) > 0:
            # Get the first match to preserve original task_desc and app_name
            original_row = matches.iloc[0]
            
            # Create new row with rerun data but without related_score and selected
            new_row = {
                'app_name': original_row['app_name'],
                'task_desc': original_row['task_desc'],
                'gpt_gen_result': rerun_row['Summary'],
                'success': task_result,
                'n_actions': steps_count,
                'soa': cleaned_soa,
                'related_score': None,  # Remove ranking
                'selected': False  # Remove selection
            }
            
            updated_rows.append(new_row)
            replaced_tasks.add(task_desc)  # Track by task description only
            print(f"Replaced: {app_name} - {task_desc}")
        else:
            print(f"Not found: {app_name} - {task_desc}")
            
            # Adhoc fix: Add specific tasks that don't exist in main file
            if task_desc == "Search call history with Bob":
                # Add this task to the results
                new_row = {
                    'app_name': 'dialer',
                    'task_desc': task_desc,
                    'gpt_gen_result': rerun_row['Summary'],
                    'success': task_result,
                    'n_actions': steps_count,
                    'soa': cleaned_soa,
                    'related_score': None,  # No ranking for new tasks
                    'selected': False  # No selection for new tasks
                }
                updated_rows.append(new_row)
                replaced_tasks.add(task_desc)
                print(f"  Added new task: {app_name} - {task_desc}")
    
    # Add all non-matching tasks from main file
    for idx, main_row in main_df.iterrows():
        task_desc = main_row['task_desc']
        app_name = main_row['app_name']
        
        # Check if this task was replaced by rerun
        if task_desc not in replaced_tasks:
            # Keep the original row
            updated_rows.append(main_row.to_dict())
        # If task was replaced, skip adding the original rows (they're already replaced above)
    
    # Create new dataframe
    updated_df = pd.DataFrame(updated_rows)
    
    # Count unique tasks in updated file
    unique_updated_tasks = updated_df[['app_name', 'task_desc']].drop_duplicates()
    print(f"\nAfter merge - Updated file has {len(unique_updated_tasks)} unique tasks")
    
    # Analyze task distribution
    task_counts = updated_df.groupby(['app_name', 'task_desc']).size().reset_index(name='count')
    print(f"\nTask distribution analysis:")
    print(f"Tasks with exactly 3 runs: {len(task_counts[task_counts['count'] == 3])}")
    print(f"Tasks with more than 3 runs: {len(task_counts[task_counts['count'] > 3])}")
    print(f"Tasks with less than 3 runs: {len(task_counts[task_counts['count'] < 3])}")
    
    # Show tasks with unusual counts
    if len(task_counts[task_counts['count'] > 3]) > 0:
        print(f"\nTasks with more than 3 runs:")
        for _, row in task_counts[task_counts['count'] > 3].iterrows():
            print(f"  {row['app_name']} - {row['task_desc']} ({row['count']} runs)")
    
    if len(task_counts[task_counts['count'] < 3]) > 0:
        print(f"\nTasks with less than 3 runs:")
        for _, row in task_counts[task_counts['count'] < 3].iterrows():
            print(f"  {row['app_name']} - {row['task_desc']} ({row['count']} runs)")
    
    # Expected vs actual
    expected_rows = len(unique_updated_tasks) * 3
    actual_rows = len(updated_df)
    print(f"\nExpected rows (if all tasks had 3 runs): {expected_rows}")
    print(f"Actual rows: {actual_rows}")
    print(f"Difference: {actual_rows - expected_rows}")
    
    # Save the updated file
    output_file = 'hai-visidroid-results-with-score-updated.csv'
    updated_df.to_csv(output_file, index=False)
    
    print(f"\nUpdate Summary:")
    print(f"Total rerun tasks: {len(rerun_df)}")
    print(f"Unique rerun tasks: {len(unique_rerun_tasks)}")
    print(f"Tasks replaced: {len([r for r in updated_rows if r['related_score'] is None])}")
    print(f"Original tasks kept: {len([r for r in updated_rows if r['related_score'] is not None])}")
    print(f"Total rows in updated file: {len(updated_rows)}")
    print(f"Updated file saved as: {output_file}")
    
    return updated_df

if __name__ == "__main__":
    updated_df = update_results_with_rerun()
