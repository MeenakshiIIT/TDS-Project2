# Automated Data Analysis Report

### Story of Data Analysis: Understanding Well-Being Across Countries

In the quest to understand global well-being, a comprehensive analysis was conducted using a dataset summarizing various indicators from 165 countries spanning the years 2005 to 2023. The dataset revealed intricate relationships between economic, social, and psychological factors shaping people's lives. Here's a deep dive into the data, findings, insights, and implications of this analysis.

#### The Data Landscape
The dataset consisted of 2,363 entries, each reflecting key indicators necessary for evaluating well-being:
- **Life Ladder**: A measure of life satisfaction.
- **Log GDP per capita**: Economic prosperity.
- **Social Support**: The perceived support available from friends and family.
- **Healthy Life Expectancy**: The duration individuals can expect to live in good health.
- **Freedom to make life choices**: Autonomy in personal decisions.
- **Generosity and perceptions of corruption**: Societal attitudes influencing community spirit.
- **Positive and Negative Affect**: Emotional experiences captured through psychological surveys.

However, the dataset did present some challenges, particularly with missing values in key areas like GDP per capita (28 missing), social support (13 missing), and perceptions of corruption (125 missing). These gaps highlighted the complexities involved in capturing a comprehensive view of well-being across different countries.

#### Statistical Overview
The analysis commenced with a summary of statistics:
- The average **Life Ladder** rating was 5.48, indicating moderate life satisfaction worldwide.
- The average **Log GDP per capita** stood at 9.40, reflecting varying levels of economic stability.
- **Social support**, a critical component of community life, averaged at 0.81 on a scale where 1 is the maximum support.
- As for **freedom to make life choices**, the indicator stood at 0.75, suggesting that many people feel relatively free in their decision-making.
  
Moreover, the dataset showed an interesting standard deviation among scores, suggesting significant diversity in well-being across various nations, as evidenced by the high range between the minimum and maximum scores.

#### Uncovering Insights
Correlational analysis revealed intriguing patterns:
1. **Strong Correlations**: There were substantial connections between Life Ladder and Log GDP per capita (0.78) and between Life Ladder and social support (0.72). This indicates a synergistic relationship where wealth and social connections enhance life satisfaction.
2. **Negative Correlations**: Conversely, perceptions of corruption had a strong negative correlation with life satisfaction (-0.43), suggesting that higher corruption perceptions correlate to lower well-being. This underscores the importance of good governance and ethical standards.
3. **Healthy Life Expectancy**: This factor demonstrated a moderate correlation with life satisfaction (0.71), showing that health plays a crucial role in overall happiness.

#### Clustering Analysis
Countries were grouped into three clusters based on common patterns in well-being indicators:
- **Cluster 0 (908 countries)**: Characterized by high life satisfaction and social support but varying economic prosperity.
- **Cluster 1 (602 countries)**: Featured lower life satisfaction scores, often correlating with higher perceptions of corruption.
- **Cluster 2 (853 countries)**: Showed a unique pattern where GDP was high, but the life ladder scores were not as elevated, indicating economic wealth doesn't always translate to happiness.

#### Implications of Findings
The analysis paints a nuanced picture of global well-being and suggests several implications:
- **Policy Recommendations**: Countries should focus on enhancing social support systems and reducing corruption to improve their citizens' life satisfaction significantly. Targeting improvements in economic health should be paired with fostering community ties and ensuring sound governance.
- **Focus on Mental Health**: Countries in cluster 1, where life satisfaction diverges from economic measures, should prioritize mental health services to address underlying issues affecting their citizens’ happiness.
- **Global Standards**: Findings can inform international organizations and aid bodies on effective resource allocation for development projects that align with boosting both economic and psychological well-being.

### Conclusion
Through this extensive analysis of data concerning global well-being, we gain valuable insights into the intertwined nature of economic factors, social support, and emotional health. This narrative not only underscores importance for policymakers and researchers but also holds relevance for individuals seeking to understand the global landscape of happiness. The journey of analyzing these interactions illuminates potential pathways towards a more satisfied and fulfilled global citizenry.

## Visualizations
![correlation_matrix.png](correlation_matrix.png)
![top_10_features_histogram.png](top_10_features_histogram.png)
