import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px

file_path = r'SGJobData/SGJobData.csv'
df = pd.read_csv(file_path)

# Display the first few rows of the dataframe
print(df.head())

print("Number of rows:", df.shape[0])

# Convert date columns to datetime objects
date_columns = ['metadata_expiryDate', 'metadata_newPostingDate', 'metadata_originalPostingDate']
for col in date_columns:
    df[col] = pd.to_datetime(df[col], errors='coerce')

# Create a new column for the average salary
df['average_salary'] = (df['salary_minimum'] + df['salary_maximum']) / 2

# display 'salary_minimum', 'salary_maximum', 'average_salary', 'metadata_newPostingDate'
print(df[['salary_minimum', 'salary_maximum', 'average_salary', 'metadata_newPostingDate']].head()) 


# Display column names and data types
print("Column Information:")
df.info()

# Display basic statistics for numerical columns
print("\nBasic Statistics:")
df.describe()

# Display the number of unique values in each column
print("\nUnique Values per Column:")
for col in df.columns:
    print(f"{col}: {df[col].nunique()} unique values")

#histogram

# Check required columns
required_cols = ['positionLevels', 'title', 'metadata_totalNumberJobApplication']
missing = [col for col in required_cols if col not in df.columns]
if missing:
    print(f"Missing columns: {missing}")
else:
    # Aggregate total applications by position level
    position_demand = df.groupby('positionLevels')['metadata_totalNumberJobApplication'].sum().sort_values(ascending=False)

    # Aggregate total applications by title
    title_demand = df.groupby('title')['metadata_totalNumberJobApplication'].sum().sort_values(ascending=False)

    # Plot histogram for position levels
    plt.figure(figsize=(10, 6))
    position_demand.plot(kind='bar')
    plt.title('Histogram of Position Levels by Total Applications')
    plt.xlabel('Position Level')
    plt.ylabel('Total Applications')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

    # Plot histogram for job titles
    plt.figure(figsize=(12, 6))
    title_demand.head(20).plot(kind='bar')
    plt.title('Histogram of Top Job Titles by Total Applications')
    plt.xlabel('Job Title')
    plt.ylabel('Total Applications')
    plt.xticks(rotation=75)
    plt.tight_layout()
    plt.show()

    #Other option 
    # Sample category mapping (expand this with full data)
category_map = {
    7: "Consulting",
    14: "Events / Promotions",
    24: "Logistics / Supply Chain",
    29: "Professional Services",
    35: "Sales / Retail"
}

# Flatten 'categories' column if it's a list of dicts
def extract_category(cat_list):
    if isinstance(cat_list, str):
        try:
            import ast
            cat_list = ast.literal_eval(cat_list)
        except:
            return None
    if isinstance(cat_list, list):
        return [category_map.get(item['id'], item['category']) for item in cat_list]
    return None

df['flattened_categories'] = df['categories'].apply(extract_category)

# Explode categories into separate rows
df_exploded = df.explode('flattened_categories')

# Group by positionLevels and title to find demand
demand_summary = df_exploded.groupby(['flattened_categories', 'positionLevels', 'title'])['metadata_totalNumberJobApplication'].sum().reset_index()

# Sort by demand
top_demand = demand_summary.sort_values(by='metadata_totalNumberJobApplication', ascending=False).head(10)

# Visualization 1: Bar chart of top demand
plt.figure(figsize=(12, 6))
sns.barplot(
    data=top_demand,
    x='metadata_totalNumberJobApplication',
    y='title',
    hue='positionLevels',
    dodge=False,
    palette='viridis'
)
plt.title("Top Job Titles by Demand Across Categories")
plt.xlabel("Total Job Applications")
plt.ylabel("Job Title")
plt.legend(title="Position Level")
plt.tight_layout()
plt.show()

# Visualization 2: Heatmap of demand by category and position level
pivot_table = demand_summary.pivot_table(
    index='flattened_categories',
    columns='positionLevels',
    values='metadata_totalNumberJobApplication',
    aggfunc='sum',
    fill_value=0
)

plt.figure(figsize=(10, 8))
sns.heatmap(pivot_table, annot=True, fmt='d', cmap='YlGnBu')
plt.title("Demand Heatmap: Categories vs Position Levels")
plt.xlabel("Position Level")
plt.ylabel("Category")
plt.tight_layout()
plt.show()

#present differently with plotly

# Sample category mapping
category_map = pd.DataFrame([
    {"id":7,"category":"Consulting"},
    {"id":14,"category":"Events / Promotions"},
    {"id":24,"category":"Logistics / Supply Chain"},
    {"id":29,"category":"Professional Services"},
    {"id":35,"category":"Sales / Retail"}
])

# Load your main dataset (replace with your actual file path or DataFrame)
# Example: demand_unstacked = pd.read_csv('/content/demand_unstacked.csv')
# For demonstration, here's a mock dataset:
demand_unstacked = pd.DataFrame({
    'categories': [7, 14, 24, 29, 35],
    'title': ['Analyst', 'Promoter', 'Supply Manager', 'Consultant', 'Retail Associate'],
    'positionLevels': ['Entry', 'Mid', 'Senior', 'Mid', 'Entry'],
    'metadata_totalNumberJobApplication': [1200, 800, 950, 1100, 1500]
})

# Merge category names
demand_unstacked = demand_unstacked.merge(category_map, left_on='categories', right_on='id', how='left')
demand_unstacked.drop(columns=['id'], inplace=True)

# Rename for clarity
demand_unstacked.rename(columns={'category': 'Category',
                                 'title': 'Title',
                                 'positionLevels': 'Position Level',
                                 'metadata_totalNumberJobApplication': 'Total Applications'}, inplace=True)

# ✅ Treemap Visualization
fig = px.treemap(
    demand_unstacked,
    path=['Category', 'Position Level', 'Title'],
    values='Total Applications',
    color='Total Applications',
    color_continuous_scale='Blues',
    title='Job Market Demand by Category, Position Level, and Title'
)
fig.show()

# ✅ Alternative 1: Barplot of Top Titles by Applications
plt.figure(figsize=(10, 6))
top_titles = demand_unstacked.sort_values(by='Total Applications', ascending=False)
sns.barplot(data=top_titles, x='Total Applications', y='Title', hue='Category')
plt.title('Top Job Titles by Total Applications')
plt.tight_layout()
plt.show()

# ✅ Alternative 2: Heatmap of Position Level vs Category
pivot_table = demand_unstacked.pivot_table(
    index='Position Level', columns='Category', values='Total Applications', aggfunc='sum'
)
plt.figure(figsize=(10, 6))
sns.heatmap(pivot_table, annot=True, fmt=".0f", cmap='YlGnBu')
plt.title('Applications by Position Level and Category')
plt.tight_layout()
plt.show()