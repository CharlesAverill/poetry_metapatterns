import pandas as pd
import os

def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    input_files = {
        'gutenberg': os.path.join(base_dir, 'gutenberg', 'gutenberg_final.csv'),
        'poetryfoundation': os.path.join(base_dir, 'poetryfoundation', 'poetryfoundation_final.csv'),
        'oupoco': os.path.join(base_dir, 'oupoco', 'oupoco_final.csv'),
        'dlk': os.path.join(base_dir, 'DLK', 'dlk_final.csv')
    }
    
    output_dir = os.path.join(base_dir, 'global')
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, 'combined_poetry_dataset.csv')
    
    all_dfs = []
    
    for source, file_path in input_files.items():
        print(f"Processing {source} dataset...")
        
        try:
            df = pd.read_csv(file_path, encoding='utf-8')
            
            df['source'] = source
            
            all_dfs.append(df)
            
            print(f"  - {len(df)} poems loaded")
            
        except Exception as e:
            print(f"Error processing {source} dataset: {e}")
    
    if all_dfs:
        combined_df = pd.concat(all_dfs, ignore_index=True)
        
        combined_df.to_csv(output_file, index=False, encoding='utf-8')
        
        print("\nCombined dataset summary:")
        print(f"  - Total poems: {len(combined_df)}")
        for source in input_files.keys():
            count = len(combined_df[combined_df['source'] == source])
            print(f"  - {source}: {count} poems")
        print(f"\nCombined dataset saved to: {output_file}")
    else:
        print("Check input")

if __name__ == "__main__":
    main()
