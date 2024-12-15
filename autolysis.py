# /// script
# requires-python = ">=3.12"
# dependencies = [
#   "httpx",
#   "pandas",
#   "matplotlib",
#   "seaborn",
#   "scikit-learn",
#   "requests",
#   "numpy",
#   "platformdirs",
#   "python-dotenv",
#   "rich",
# ]
# ///


import os
import sys
import argparse
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import requests
import json
from sklearn.impute import SimpleImputer
from sklearn.cluster import KMeans
from scipy.stats import zscore

# Ensure consistent styling for plots
sns.set(style="whitegrid")

# AI Proxy configuration
API_URL = "https://aiproxy.sanand.workers.dev/openai/v1/chat/completions"
MODEL_NAME = "gpt-4o-mini"

def get_aiproxy_token():
    """Retrieve the AI Proxy token from environment variables."""
    token = os.environ.get("AIPROXY_TOKEN", None)
    if not token:
        raise EnvironmentError("AIPROXY_TOKEN environment variable is not set.")
    return token

def analyze_data(file_path):
    """Perform generic analysis on the dataset."""
    # Load the dataset
    #data = pd.read_csv(file_path)
    try:
        # Attempt to read the file with utf-8 encoding
        data = pd.read_csv(file_path, encoding="utf-8")
    except UnicodeDecodeError:
        # Fallback to a different encoding if utf-8 fails
        data = pd.read_csv(file_path, encoding="latin1")
    
    
    # Step 1: Summary Statistics
    summary = data.describe(include="all").transpose()  # Includes all columns: numeric and non-numeric
    
    # Step 2: Count Missing Values
    missing_values = data.isnull().sum()
    
    # Step 3: Data Types
    dtypes = data.dtypes
    
    # Step 4: Correlation (only numeric columns)
    correlation = None
    numerical_data = data.select_dtypes(include=["number"])  # Only numeric columns for correlation
    if not numerical_data.empty:
        correlation = numerical_data.corr()

    # Step 5: Outlier Detection (using Z-score for numerical columns)
    outliers = {}
    z_scores = numerical_data.apply(zscore)
    outliers = (z_scores.abs() > 3).sum(axis=0)  # Flag values with Z-score > 3

    # Step 6: Handle missing values
    numeric_cols = data.select_dtypes(include=["number"]).columns
    non_numeric_cols = data.select_dtypes(exclude=["number"]).columns

    # Impute numeric columns with mean
    imputer_numeric = SimpleImputer(strategy='mean')
    data[numeric_cols] = imputer_numeric.fit_transform(data[numeric_cols])

    # Impute non-numeric columns with the most frequent value
    imputer_non_numeric = SimpleImputer(strategy='most_frequent')
    data[non_numeric_cols] = imputer_non_numeric.fit_transform(data[non_numeric_cols])
    
    # Step 7: Cluster Analysis (using KMeans for numeric data)
    cluster_info = {}
    if not numerical_data.empty:
        imputer_kmeans = SimpleImputer(strategy='mean')
        numerical_data_imputed = imputer_kmeans.fit_transform(numerical_data)
        
        # Perform KMeans clustering after imputation
        kmeans = KMeans(n_clusters=3, random_state=42)
        data['cluster'] = kmeans.fit_predict(numerical_data_imputed)
        cluster_info = data['cluster'].value_counts()

    # Prepare data for LLM analysis
    context = {
        "columns": data.columns.tolist(),
        "dtypes": {col: str(dtype) for col, dtype in dtypes.items()},
        "missing_values": missing_values.to_dict(),
        "summary_stats": summary.to_dict(),
        "outliers": outliers.to_dict(),
        "correlation": correlation.to_dict() if correlation is not None else None,
        "cluster_info": cluster_info.to_dict(),
    }
    return data, context

def interact_with_aiproxy(context, task_description):
    """Interact with the AI Proxy to get insights from the LLM."""
    
    # ** Step 1: Reduce context size to optimize LLM usage **
    reduced_context = {
        "columns": context.get("columns", [])[:10],  # Send only the first 10 columns
        
        # Reduce dtypes to only essential ones (first 10 columns)
        "dtypes": {col: dtype for col, dtype in list(context.get("dtypes", {}).items())[:10]},
        
        # Limit summary stats to the first 5 columns
        "summary_stats": {k: v for k, v in list(context.get("summary_stats", {}).items())[:5]},
        
        # Reduce missing values to the 5 most missing columns
        "missing_values": dict(sorted(context.get("missing_values", {}).items(), key=lambda x: x[1], reverse=True)[:5]),
        
        # Only send details about the 5 features with the highest number of outliers
        "outliers": dict(sorted(context.get("outliers", {}).items(), key=lambda x: x[1], reverse=True)[:5]),
        
        # Only keep top correlations (above a threshold) and limit to 10 pairs
        "correlation": None  
    }
    
    # If correlation exists, reduce it by filtering high correlations (> 0.7) and limiting to 10 pairs
    if context.get("correlation") is not None:
        correlation = context["correlation"]
        high_corr_pairs = {}
        for col, corr_values in correlation.items():
            for other_col, corr_value in corr_values.items():
                if col != other_col and abs(corr_value) > 0.7:  # Only high correlations
                    if len(high_corr_pairs) < 10:  # Limit to 10 correlations
                        high_corr_pairs[f"{col} & {other_col}"] = round(corr_value, 2)  # Round for clarity
        reduced_context["correlation"] = high_corr_pairs
    
    # ** Step 2: Prepare the API request payload **
    payload = {
        "model": MODEL_NAME,
        "messages": [
            {"role": "system", "content": "You are an expert data analyst."},
            {"role": "user", "content": f"{task_description}\nContext: {json.dumps(reduced_context)}"}
        ]
    }
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {get_aiproxy_token()}"
    }

    # ** Step 3: Send request to LLM and handle the response **
    try:
        response = requests.post(API_URL, json=payload, headers=headers)
        response.raise_for_status()
        result = response.json()
        return result["choices"][0]["message"]["content"]
    except requests.exceptions.RequestException as e:
        print(f"Error interacting with AI Proxy: {e}")
        return None


def interact_with_aiproxy_with_images(context, task_description, image_paths):
    """Interact with the AI Proxy to get insights from the LLM with visual capabilities."""
    
    # Convert images to base64 strings
    def encode_image_as_base64(image_path):
        """Encodes an image file as a base64 string."""
        try:
            with open(image_path, "rb") as img_file:
                return base64.b64encode(img_file.read()).decode("utf-8")
        except FileNotFoundError:
            print(f"Error: Image file not found at {image_path}")
            return None
        except Exception as e:
            print(f"Error encoding image {image_path}: {e}")
            return None

    encoded_images = [encode_image_as_base64(img_path) for img_path in image_paths]
    encoded_images = [img for img in encoded_images if img is not None]  # Remove None values

    # Reduce the context to avoid large payloads
    reduced_context = {
        "columns": context.get("columns", [])[:10],
        "summary_stats": {k: v for k, v in list(context.get("summary_stats", {}).items())[:5]},
    }

    payload = {
        "model": MODEL_NAME,
        "messages": [
            {"role": "system", "content": "You are an expert data and image analyst."},
            {"role": "user", "content": f"{task_description}\nContext: {json.dumps(reduced_context)}"},
        ],
        "images": encoded_images  # Include the encoded images
    }

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {get_aiproxy_token()}"
    }

    try:
        response = requests.post(API_URL, json=payload, headers=headers)
        response.raise_for_status()
        result = response.json()
        return result["choices"][0]["message"]["content"]
    except requests.exceptions.RequestException as e:
        print(f"Error interacting with AI Proxy for image analysis: {e}")
        print(f"Payload: {json.dumps(payload, indent=4)}")
        return None
    except KeyError as e:
        print(f"Unexpected response structure: {response.text}")
        return None


def identify_important_features(data):
    """Identify important numeric features based on correlation, variance, and missing values."""
    
    # Step 1: Remove columns with too many missing values (e.g., more than 30% missing)
    missing_percentage = data.isnull().mean()
    data_clean = data.drop(columns=missing_percentage[missing_percentage > 0.3].index)

    # Step 2: Remove non-numeric columns for boxplot and histogram visualization
    numerical_data = data_clean.select_dtypes(include=["number"])

    # Step 3: Remove columns with low variance (below a threshold, e.g., 0.1)
    variance = numerical_data.var()
    important_numerical_data = numerical_data[variance[variance > 0.1].index]

    # Step 4: Identify the top 10 important features (could be based on correlation or other metrics)
    correlation_matrix = important_numerical_data.corr().abs()
    upper = correlation_matrix.where(np.triu(np.ones(correlation_matrix.shape), k=1).astype(bool))  # Upper triangle
    correlated_features = [column for column in upper.columns if any(upper[column] > 0.2)]
    
    # Selecting top 10 based on their correlation with the rest of the features
    top_10_features = important_numerical_data[correlated_features].columns[:10]
    
    return important_numerical_data, top_10_features



def generate_visualizations(data, output_dir):
    """Generate and save visualizations based on the important features."""
    important_data, top_10_features = identify_important_features(data)
    
    # Ensure there are enough features to generate the requested plots
    # if important_data.empty or len(top_10_features) < 10:
    #     print("Insufficient important features for visualization.")
    #     return
    
    # Create Correlation Matrix for all numeric features (excluding categorical features)
    plt.figure(figsize=(12, 10))
    numeric_data = data.select_dtypes(include=["number"])  # Only numeric columns
    correlation_matrix = numeric_data.corr()
    sns.heatmap(correlation_matrix, annot=True, cmap="coolwarm", fmt=".2f")
    plt.title("Correlation Matrix (Numeric Features)")
    plt.savefig(os.path.join(output_dir, "correlation_matrix.png"))
    plt.close()

    # Create Combined Histograms for Top 10 Features in Subplots
    fig, axes = plt.subplots(2, 5, figsize=(20, 10))  # 2 rows, 5 columns
    axes = axes.ravel()  # Flatten the 2D axes array for easier indexing

    for i, col in enumerate(top_10_features):
        axes[i].hist(important_data[col].dropna(), bins=20, alpha=0.7)
        axes[i].set_title(f"Histogram of {col}")
        axes[i].set_xlabel(col)
        axes[i].set_ylabel('Frequency')

    # Hide the last subplot if there are less than 10 features
    for j in range(i + 1, 10):
        axes[j].axis('off')

    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "top_10_features_histogram.png"))
    plt.close()

# # Compress the image
#     compress_image(temp_image_path, compressed_image_path)
#     os.remove(temp_image_path)

# def compress_image(input_path, output_path, quality=70):
#     """Compress an image to reduce file size."""
#     with Image.open(input_path) as img:
#         img = img.convert("RGB")
#         img.save(output_path, "JPEG", quality=quality)

def write_markdown_report(output_dir, analysis_summary, visualizations):
    """Write a markdown report summarizing the analysis."""
    with open(os.path.join(output_dir, "README.md"), "w") as f:
        f.write("# Automated Data Analysis Report\n\n")
        f.write(analysis_summary)
        f.write("\n\n## Visualizations\n")
        for viz in visualizations:
            f.write(f"![{viz}]({viz})\n")

def agentic_workflow(context, initial_task, output_dir):
    """Agentic workflow where the LLM decides the next step."""
    current_task = initial_task
    for step in range(3):  
       # print(f"🔍 Task {step + 1}: {current_task}")
        result = interact_with_aiproxy(context, current_task)
        
        if "generate visualization" in result.lower():
            generate_visualizations(context, output_dir)
        elif "stop" in result.lower() or "complete" in result.lower():
            break  
        else:
            current_task = result  

def main():
    parser = argparse.ArgumentParser(description="Automated data analysis with AI Proxy support.")
    parser.add_argument("csv_file", help="Path to the CSV dataset")
    args = parser.parse_args()

    output_dir = os.path.splitext(args.csv_file)[0]
    os.makedirs(output_dir, exist_ok=True)

    # Step 1: Analyze the dataset
    data, context = analyze_data(args.csv_file)

    # Step 2: Interact with AI Proxy for insights
    insights = interact_with_aiproxy(context, "Generate a story about this data analysis, including the data, analysis, insights, and implications.")

    
    # Step 3: Visualize findings
    generate_visualizations(data, output_dir)

    # image_paths = [os.path.join(output_dir, f) for f in os.listdir(output_dir) if f.endswith(".png")]
    # try:
    #     insights_with_images = interact_with_aiproxy_with_images(
    #         context, 
    #         "Analyze these images and explain any interesting insights or patterns you observe.", 
    #         image_paths
    #     )
    # except Exception as e:
    #     print(f"Error interacting with AI Proxy for image analysis: {e}")
    #     insights_with_images = "No insights available for image analysis."


    # Step 4: Write a markdown report
    visualizations = [f for f in os.listdir(output_dir) if f.endswith(".png")]
    write_markdown_report(output_dir, insights, visualizations)

    # initial_task = "Perform an initial analysis of the dataset and decide next steps."
    # agentic_workflow(context, initial_task, output_dir)

if __name__ == "__main__":
    main()
