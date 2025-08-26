import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from statsmodels.stats.proportion import proportions_ztest, proportion_confint
from statsmodels.stats.power import ttest_power
import warnings
warnings.filterwarnings('ignore')

# Set style for better visualizations
plt.style.use('seaborn-v0_8')
sns.set_palette("husl")

class ABTestAnalyzer:
    """Comprehensive A/B Test Analysis Class"""
    
    def __init__(self, ab_test_file, countries_file):
        self.load_and_prepare_data(ab_test_file, countries_file)
        self.alpha = 0.05
        
    def load_and_prepare_data(self, ab_test_file, countries_file):
        """Load and clean the data"""
        print("=== DATA LOADING & PREPARATION ===")
        
        # Load data
        ab_test = pd.read_csv(ab_test_file)
        countries = pd.read_csv(countries_file)
        
        print(f"Initial AB test data shape: {ab_test.shape}")
        print(f"Initial countries data shape: {countries.shape}")
        
        # Merge datasets
        self.data = pd.merge(ab_test, countries, on='id', how='inner')
        print(f"Merged data shape: {self.data.shape}")
        
        # Check for duplicates
        duplicates = self.data.duplicated('id').sum()
        print(f"Duplicate IDs found: {duplicates}")
        
        if duplicates > 0:
            print("Removing duplicates...")
            self.data = self.data.drop_duplicates(subset='id')
            print(f"Data shape after removing duplicates: {self.data.shape}")
        
        # Data quality checks
        self._data_quality_checks()
        
    def _data_quality_checks(self):
        """Comprehensive data quality validation"""
        print("\n=== DATA QUALITY CHECKS ===")
        
        # Missing values
        missing = self.data.isnull().sum()
        print("Missing values by column:")
        print(missing)
        
        # Check treatment assignment integrity
        print("\n--- Treatment Assignment Validation ---")
        assignment_check = pd.crosstab(self.data['con_treat'], self.data['page'])
        print("Treatment vs Page Assignment:")
        print(assignment_check)
        
        # Calculate misassignment rate
        control_with_new = assignment_check.loc['control', 'new_page'] if 'new_page' in assignment_check.columns else 0
        treatment_with_old = assignment_check.loc['treatment', 'old_page'] if 'old_page' in assignment_check.columns else 0
        
        total_control = assignment_check.loc['control'].sum()
        total_treatment = assignment_check.loc['treatment'].sum()
        
        control_error_rate = control_with_new / total_control if total_control > 0 else 0
        treatment_error_rate = treatment_with_old / total_treatment if total_treatment > 0 else 0
        
        print(f"Control group misassignment rate: {control_error_rate:.2%}")
        print(f"Treatment group misassignment rate: {treatment_error_rate:.2%}")
        
        if control_error_rate > 0.01 or treatment_error_rate > 0.01:
            print("⚠️  WARNING: High misassignment rate detected! This could invalidate results.")
        else:
            print("✅ Treatment assignment appears correct.")
            
        # Sample size balance
        print(f"\n--- Sample Size Balance ---")
        group_sizes = self.data['con_treat'].value_counts()
        print(group_sizes)
        
        size_ratio = group_sizes.min() / group_sizes.max()
        print(f"Sample size ratio: {size_ratio:.3f}")
        
        if size_ratio < 0.8:
            print("⚠️  WARNING: Unbalanced sample sizes detected!")
        else:
            print("✅ Sample sizes are reasonably balanced.")
            
    def exploratory_analysis(self):
        """Comprehensive exploratory data analysis"""
        print("\n=== EXPLORATORY DATA ANALYSIS ===")
        
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        
        # 1. Sample distribution by country
        country_counts = self.data['country'].value_counts()
        axes[0,0].bar(country_counts.index, country_counts.values)
        axes[0,0].set_title('Sample Distribution by Country')
        axes[0,0].set_xlabel('Country')
        axes[0,0].set_ylabel('Count')
        
        # Add count labels
        for i, (country, count) in enumerate(country_counts.items()):
            axes[0,0].text(i, count + 1000, f'{count:,}', ha='center', va='bottom')
        
        # 2. Overall conversion rates
        overall_rates = self.data.groupby('con_treat')['converted'].agg(['mean', 'count']).reset_index()
        
        axes[0,1].bar(overall_rates['con_treat'], overall_rates['mean'], 
                     color=['#1f77b4', '#ff7f0e'])
        axes[0,1].set_title('Overall Conversion Rates')
        axes[0,1].set_ylabel('Conversion Rate')
        axes[0,1].set_ylim(0, max(overall_rates['mean']) * 1.2)
        
        # Add rate labels
        for i, row in overall_rates.iterrows():
            axes[0,1].text(i, row['mean'] + 0.002, f'{row["mean"]:.3f}', 
                          ha='center', va='bottom', fontweight='bold')
        
        # 3. Conversion rates by country
        country_rates = self.data.groupby(['country', 'con_treat'])['converted'].mean().unstack()
        country_rates.plot(kind='bar', ax=axes[1,0], width=0.8)
        axes[1,0].set_title('Conversion Rates by Country and Treatment')
        axes[1,0].set_ylabel('Conversion Rate')
        axes[1,0].legend(title='Group')
        axes[1,0].tick_params(axis='x', rotation=0)
        
        # 4. Sample sizes by country and treatment
        country_sizes = self.data.groupby(['country', 'con_treat']).size().unstack()
        country_sizes.plot(kind='bar', ax=axes[1,1], width=0.8)
        axes[1,1].set_title('Sample Sizes by Country and Treatment')
        axes[1,1].set_ylabel('Sample Size')
        axes[1,1].legend(title='Group')
        axes[1,1].tick_params(axis='x', rotation=0)
        
        plt.tight_layout()
        plt.show()
        
    def power_analysis(self):
        """Calculate power analysis for the experiment"""
        print("\n=== POWER ANALYSIS ===")
        
        # Overall rates
        control_rate = self.data[self.data['con_treat'] == 'control']['converted'].mean()
        treatment_rate = self.data[self.data['con_treat'] == 'treatment']['converted'].mean()
        
        # Effect size (Cohen's h for proportions)
        effect_size = 2 * (np.arcsin(np.sqrt(treatment_rate)) - np.arcsin(np.sqrt(control_rate)))
        
        # Sample sizes
        n_control = len(self.data[self.data['con_treat'] == 'control'])
        n_treatment = len(self.data[self.data['con_treat'] == 'treatment'])
        n_avg = (n_control + n_treatment) / 2
        
        # Calculate achieved power
        power = ttest_power(effect_size, n_avg, self.alpha, alternative='two-sided')
        
        print(f"Control conversion rate: {control_rate:.4f}")
        print(f"Treatment conversion rate: {treatment_rate:.4f}")
        print(f"Effect size (Cohen's h): {effect_size:.4f}")
        print(f"Average sample size per group: {n_avg:,.0f}")
        print(f"Achieved statistical power: {power:.3f}")
        
        if power < 0.8:
            print("⚠️  WARNING: Statistical power is below the recommended 0.8 threshold!")
        else:
            print("✅ Adequate statistical power achieved.")
            
        return power
    
    def statistical_tests(self):
        """Comprehensive statistical analysis"""
        print("\n=== STATISTICAL ANALYSIS ===")
        
        results = {}
        
        # Overall test
        print("--- Overall Test ---")
        control_data = self.data[self.data['con_treat'] == 'control']
        treatment_data = self.data[self.data['con_treat'] == 'treatment']
        
        control_conversions = control_data['converted'].sum()
        treatment_conversions = treatment_data['converted'].sum()
        control_size = len(control_data)
        treatment_size = len(treatment_data)
        
        # Z-test for proportions
        z_stat, p_value = proportions_ztest([treatment_conversions, control_conversions], 
                                           [treatment_size, control_size])
        
        # Effect size
        control_rate = control_conversions / control_size
        treatment_rate = treatment_conversions / treatment_size
        effect_size = treatment_rate - control_rate
        relative_effect = (effect_size / control_rate) * 100
        
        # Confidence interval
        ci_low, ci_high = proportion_confint([treatment_conversions, control_conversions], 
                                           [treatment_size, control_size], alpha=self.alpha)
        ci_diff_low = ci_low[0] - ci_high[1]
        ci_diff_high = ci_high[0] - ci_low[1]
        
        results['overall'] = {
            'control_rate': control_rate,
            'treatment_rate': treatment_rate,
            'effect_size': effect_size,
            'relative_effect': relative_effect,
            'z_stat': z_stat,
            'p_value': p_value,
            'ci_low': ci_diff_low,
            'ci_high': ci_diff_high,
            'significant': p_value < self.alpha
        }
        
        print(f"Control rate: {control_rate:.4f} ({control_conversions}/{control_size})")
        print(f"Treatment rate: {treatment_rate:.4f} ({treatment_conversions}/{treatment_size})")
        print(f"Absolute effect: {effect_size:.4f} ({effect_size*100:+.2f} percentage points)")
        print(f"Relative effect: {relative_effect:+.2f}%")
        print(f"95% CI for difference: [{ci_diff_low:.4f}, {ci_diff_high:.4f}]")
        print(f"Z-statistic: {z_stat:.4f}")
        print(f"P-value: {p_value:.4f}")
        print(f"Result: {'Significant' if p_value < self.alpha else 'Not significant'}")
        
        # Country-level analysis with Bonferroni correction
        print("\n--- Country-Level Analysis ---")
        countries = self.data['country'].unique()
        n_tests = len(countries)
        bonferroni_alpha = self.alpha / n_tests
        
        print(f"Applying Bonferroni correction for {n_tests} tests")
        print(f"Adjusted significance level: {bonferroni_alpha:.4f}")
        
        for country in countries:
            print(f"\n{country}:")
            country_data = self.data[self.data['country'] == country]
            
            country_control = country_data[country_data['con_treat'] == 'control']
            country_treatment = country_data[country_data['con_treat'] == 'treatment']
            
            c_conv = country_control['converted'].sum()
            t_conv = country_treatment['converted'].sum()
            c_size = len(country_control)
            t_size = len(country_treatment)
            
            if c_size > 0 and t_size > 0:
                z_stat, p_val = proportions_ztest([t_conv, c_conv], [t_size, c_size])
                
                c_rate = c_conv / c_size
                t_rate = t_conv / t_size
                effect = t_rate - c_rate
                rel_effect = (effect / c_rate) * 100 if c_rate > 0 else 0
                
                # Confidence interval
                ci_low, ci_high = proportion_confint([t_conv, c_conv], [t_size, c_size], 
                                                   alpha=bonferroni_alpha)
                ci_diff_low = ci_low[0] - ci_high[1]
                ci_diff_high = ci_high[0] - ci_low[1]
                
                results[country] = {
                    'control_rate': c_rate,
                    'treatment_rate': t_rate,
                    'effect_size': effect,
                    'relative_effect': rel_effect,
                    'z_stat': z_stat,
                    'p_value': p_val,
                    'p_value_adjusted': p_val < bonferroni_alpha,
                    'ci_low': ci_diff_low,
                    'ci_high': ci_diff_high
                }
                
                print(f"  Control: {c_rate:.4f} ({c_conv}/{c_size})")
                print(f"  Treatment: {t_rate:.4f} ({t_conv}/{t_size})")
                print(f"  Effect: {effect:+.4f} ({rel_effect:+.2f}%)")
                print(f"  95% CI: [{ci_diff_low:.4f}, {ci_diff_high:.4f}]")
                print(f"  Z: {z_stat:.4f}, p: {p_val:.4f}")
                print(f"  Significant (Bonferroni): {'Yes' if p_val < bonferroni_alpha else 'No'}")
        
        return results
    
    def create_results_visualization(self, results):
        """Create comprehensive results visualization"""
        print("\n=== RESULTS VISUALIZATION ===")
        
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        
        # 1. Effect sizes by country
        countries = [k for k in results.keys() if k != 'overall']
        effects = [results[country]['relative_effect'] for country in countries]
        colors = ['red' if effect < 0 else 'green' for effect in effects]
        
        bars = axes[0,0].bar(countries, effects, color=colors, alpha=0.7)
        axes[0,0].axhline(y=0, color='black', linestyle='-', alpha=0.3)
        axes[0,0].set_title('Relative Effect Size by Country (%)')
        axes[0,0].set_ylabel('Relative Effect (%)')
        
        # Add value labels
        for bar, effect in zip(bars, effects):
            height = bar.get_height()
            axes[0,0].text(bar.get_x() + bar.get_width()/2., 
                          height + (0.1 if height >= 0 else -0.3),
                          f'{effect:+.1f}%', ha='center', va='bottom' if height >= 0 else 'top',
                          fontweight='bold')
        
        # 2. Confidence intervals
        countries_with_overall = ['Overall'] + countries
        effects_with_overall = [results['overall']['relative_effect']] + effects
        
        ci_lows = [results['overall']['ci_low']*100] + [results[country]['ci_low']*100 for country in countries]
        ci_highs = [results['overall']['ci_high']*100] + [results[country]['ci_high']*100 for country in countries]

        x_pos = range(len(countries_with_overall))
        lower_errors = np.abs(np.array(effects_with_overall) - np.array(ci_lows))
        upper_errors = np.abs(np.array(ci_highs) - np.array(effects_with_overall))

        axes[0,1].errorbar(x_pos, effects_with_overall, 
                          yerr=[lower_errors, upper_errors],
                          fmt='o', capsize=5, capthick=2)
        axes[0,1].axhline(y=0, color='red', linestyle='--', alpha=0.5)
        axes[0,1].set_xticks(x_pos)
        axes[0,1].set_xticklabels(countries_with_overall, rotation=45)
        axes[0,1].set_title('Effect Sizes with 95% Confidence Intervals')
        axes[0,1].set_ylabel('Relative Effect (%)')
        axes[0,1].grid(True, alpha=0.3)
        
        # 3. Sample sizes
        control_sizes = [len(self.data[(self.data['country'] == country) & 
                                     (self.data['con_treat'] == 'control')]) for country in countries]
        treatment_sizes = [len(self.data[(self.data['country'] == country) & 
                                       (self.data['con_treat'] == 'treatment')]) for country in countries]
        
        x = np.arange(len(countries))
        width = 0.35
        
        axes[1,0].bar(x - width/2, control_sizes, width, label='Control', alpha=0.8)
        axes[1,0].bar(x + width/2, treatment_sizes, width, label='Treatment', alpha=0.8)
        axes[1,0].set_title('Sample Sizes by Country')
        axes[1,0].set_ylabel('Sample Size')
        axes[1,0].set_xticks(x)
        axes[1,0].set_xticklabels(countries)
        axes[1,0].legend()
        
        # 4. P-values
        p_values = [results[country]['p_value'] for country in countries]
        colors_p = ['red' if p < 0.05/len(countries) else 'orange' if p < 0.05 else 'gray' 
                   for p in p_values]
        
        bars_p = axes[1,1].bar(countries, p_values, color=colors_p, alpha=0.7)
        axes[1,1].axhline(y=0.05, color='orange', linestyle='--', alpha=0.7, label='α = 0.05')
        axes[1,1].axhline(y=0.05/len(countries), color='red', linestyle='--', alpha=0.7, 
                         label=f'Bonferroni α = {0.05/len(countries):.3f}')
        axes[1,1].set_title('P-values by Country')
        axes[1,1].set_ylabel('P-value')
        axes[1,1].set_yscale('log')
        axes[1,1].legend()
        
        plt.tight_layout()
        plt.show()
    
    def business_recommendations(self, results):
        """Generate business recommendations"""
        print("\n" + "="*50)
        print("BUSINESS RECOMMENDATIONS & CONCLUSIONS")
        print("="*50)
        
        overall_effect = results['overall']['relative_effect']
        overall_significant = results['overall']['significant']
        
        print(f"\n🎯 OVERALL RESULT:")
        print(f"   New page shows a {overall_effect:+.2f}% relative change in conversion rate")
        print(f"   Statistical significance: {'YES' if overall_significant else 'NO'}")
        
        if overall_effect < -2:  # More than 2% relative decrease
            print(f"\n❌ CRITICAL FINDING: Treatment is HARMING conversions!")
            print(f"   This represents a potentially significant business risk.")
        elif overall_effect < 0:
            print(f"\n⚠️  WARNING: Treatment shows negative effect on conversions")
        elif overall_effect > 2:
            print(f"✅ POSITIVE: Treatment shows promising improvement")
        else:
            print(f"➡️  NEUTRAL: Treatment shows minimal effect")
        
        print(f"\n📊 COUNTRY-LEVEL INSIGHTS:")
        
        countries = [k for k in results.keys() if k != 'overall']
        negative_countries = []
        positive_countries = []
        
        for country in countries:
            effect = results[country]['relative_effect']
            if effect < 0:
                negative_countries.append((country, effect))
            else:
                positive_countries.append((country, effect))
            
            print(f"   {country}: {effect:+.2f}% relative change")
        
        print(f"\n🚨 BUSINESS RECOMMENDATIONS:")
        
        if len(negative_countries) >= 2:
            print(f"   1. IMMEDIATE ACTION REQUIRED: Do NOT launch the new page")
            print(f"      - Negative effects observed in {len(negative_countries)} countries")
            print(f"      - Investigate what's causing the decrease in conversions")
        
        print(f"   2. INVESTIGATE ROOT CAUSES:")
        print(f"      - Technical issues with new page?")
        print(f"      - User experience problems?")
        print(f"      - Cultural/regional preferences?")
        
        print(f"   3. NEXT STEPS:")
        if overall_effect < -1:
            print(f"      - Stop the experiment immediately")
            print(f"      - Conduct user research to understand the negative impact")
        else:
            print(f"      - Consider extending test duration for more data")
            print(f"      - Segment analysis by device, traffic source, etc.")
            
        # Calculate potential business impact
        total_users = len(self.data)
        current_conversions = self.data['converted'].sum()
        
        if overall_effect != 0:
            projected_impact = (overall_effect / 100) * current_conversions
            print(f"\n💰 PROJECTED BUSINESS IMPACT:")
            print(f"   With current traffic volume:")
            print(f"   - Current conversions: {current_conversions:,}")
            print(f"   - Projected change: {projected_impact:+,.0f} conversions")
            print(f"   - That's a {projected_impact/current_conversions*100:+.1f}% change in total conversions")

# Usage
if __name__ == "__main__":
    # Initialize analyzer
    analyzer = ABTestAnalyzer("ab_test.csv", "countries_ab.csv")
    
    # Run complete analysis
    analyzer.exploratory_analysis()
    analyzer.power_analysis()
    results = analyzer.statistical_tests()
    analyzer.create_results_visualization(results)
    analyzer.business_recommendations(results)
    
    print(f"\n{'='*50}")
    print("ANALYSIS COMPLETE")
    print(f"{'='*50}")
