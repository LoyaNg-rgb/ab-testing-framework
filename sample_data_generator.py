import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

def generate_sample_ab_test_data(n_users=100000, seed=42):
    """
    Generate realistic A/B test sample data
    
    Parameters:
    -----------
    n_users : int
        Number of users to generate
    seed : int
        Random seed for reproducibility
        
    Returns:
    --------
    tuple: (ab_test_df, countries_df)
    """
    
    np.random.seed(seed)
    random.seed(seed)
    
    # Define parameters for realistic data
    countries = ['US', 'UK', 'CA']
    country_weights = [0.6, 0.25, 0.15]  # US-heavy distribution
    
    # Base conversion rates by country (control group)
    base_conversion_rates = {
        'US': 0.125,
        'UK': 0.110, 
        'CA': 0.115
    }
    
    # Treatment effects by country (some positive, some negative for realism)
    treatment_effects = {
        'US': -0.008,   # Slightly negative effect
        'UK': +0.015,   # Positive effect  
        'CA': -0.005    # Slightly negative effect
    }
    
    # Generate user IDs
    user_ids = list(range(1, n_users + 1))
    
    # Assign countries
    countries_assigned = np.random.choice(
        countries, 
        size=n_users, 
        p=country_weights
    )
    
    # Random assignment to treatment groups (50/50 split)
    treatment_assignment = np.random.choice(
        ['control', 'treatment'], 
        size=n_users,
        p=[0.5, 0.5]
    )
    
    # Generate page assignment (should match treatment, with small error rate)
    page_assignment = []
    for treatment in treatment_assignment:
        if treatment == 'control':
            # 99% get old_page, 1% misassigned
            page = np.random.choice(['old_page', 'new_page'], p=[0.99, 0.01])
        else:
            # 99% get new_page, 1% misassigned  
            page = np.random.choice(['new_page', 'old_page'], p=[0.99, 0.01])
        page_assignment.append(page)
    
    # Generate conversions based on country and treatment
    conversions = []
    for i in range(n_users):
        country = countries_assigned[i]
        treatment = treatment_assignment[i]
        
        # Base rate for this country
        base_rate = base_conversion_rates[country]
        
        # Apply treatment effect
        if treatment == 'treatment':
            conversion_rate = base_rate + treatment_effects[country]
        else:
            conversion_rate = base_rate
            
        # Ensure rate is between 0 and 1
        conversion_rate = max(0, min(1, conversion_rate))
        
        # Generate conversion (0 or 1)
        converted = np.random.binomial(1, conversion_rate)
        conversions.append(converted)
    
    # Generate timestamps (spread over 30 days)
    start_date = datetime(2024, 1, 1)
    timestamps = []
    for _ in range(n_users):
        random_days = random.randint(0, 29)
        random_hours = random.randint(0, 23) 
        random_minutes = random.randint(0, 59)
        random_seconds = random.randint(0, 59)
        
        timestamp = start_date + timedelta(
            days=random_days,
            hours=random_hours, 
            minutes=random_minutes,
            seconds=random_seconds
        )
        timestamps.append(timestamp)
    
    # Create A/B test DataFrame
    ab_test_df = pd.DataFrame({
        'id': user_ids,
        'timestamp': timestamps,
        'con_treat': treatment_assignment,  # Using your column name
        'page': page_assignment,
        'converted': conversions
    })
    
    # Create countries DataFrame  
    countries_df = pd.DataFrame({
        'id': user_ids,
        'country': countries_assigned
    })
    
    # Add some missing values for realism (very few)
    missing_indices = np.random.choice(n_users, size=int(0.001 * n_users), replace=False)
    for idx in missing_indices:
        if random.random() < 0.5:
            countries_df.loc[idx, 'country'] = np.nan
    
    return ab_test_df, countries_df

def save_sample_data(ab_test_df, countries_df, ab_test_filename='sample_ab_test.csv', 
                     countries_filename='sample_countries.csv'):
    """
    Save the generated sample data to CSV files
    
    Parameters:
    -----------
    ab_test_df : pandas.DataFrame
        A/B test data
    countries_df : pandas.DataFrame  
        Countries data
    ab_test_filename : str
        Filename for A/B test data
    countries_filename : str
        Filename for countries data
    """
    
    ab_test_df.to_csv(ab_test_filename, index=False)
    countries_df.to_csv(countries_filename, index=False)
    
    print(f"Sample data saved:")
    print(f"  - A/B test data: {ab_test_filename} ({len(ab_test_df):,} records)")
    print(f"  - Countries data: {countries_filename} ({len(countries_df):,} records)")
    
    # Print summary statistics
    print(f"\nData Summary:")
    print(f"  - Date range: {ab_test_df['timestamp'].min()} to {ab_test_df['timestamp'].max()}")
    print(f"  - Countries: {', '.join(countries_df['country'].value_counts().index)}")
    print(f"  - Treatment split: {ab_test_df['con_treat'].value_counts().to_dict()}")
    print(f"  - Overall conversion rate: {ab_test_df['converted'].mean():.3f}")
    
    # Conversion rates by treatment
    conv_by_treatment = ab_test_df.groupby('con_treat')['converted'].mean()
    print(f"  - Control conversion rate: {conv_by_treatment['control']:.3f}")
    print(f"  - Treatment conversion rate: {conv_by_treatment['treatment']:.3f}")
    print(f"  - Relative difference: {((conv_by_treatment['treatment'] / conv_by_treatment['control']) - 1) * 100:+.1f}%")

if __name__ == "__main__":
    # Generate sample data
    print("Generating sample A/B test data...")
    ab_test_df, countries_df = generate_sample_ab_test_data(n_users=100000)
    
    # Save to CSV files
    save_sample_data(ab_test_df, countries_df)
    
    print("\nSample data generation complete!")
    print("You can now run: python ab_test_analyzer.py")
