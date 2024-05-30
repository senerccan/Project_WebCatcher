import streamlit as st
import pandas as pd
import plotly.express as px
from st_aggrid import AgGrid
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Watchdog event handler class
class WatchdogHandler(FileSystemEventHandler):
    def on_modified(self, event):
        if event.src_path.endswith('.csv'):
            st.experimental_rerun()

# Start the watchdog observer if it's not already running
if 'observer' not in st.session_state:
    event_handler = WatchdogHandler()
    observer = Observer()
    observer.schedule(event_handler, path='.', recursive=False)
    observer.start()
    st.session_state['observer'] = observer

# Define time sensitivity labels
def get_time_sensitivity_label(time_period):
    if time_period == "Less than 6 months":
        return "Short-term"
    elif time_period == "6 months to 1 year":
        return "Medium-term"
    else:
        return "Long-term"

# Function to apply alignment adjustments
def apply_alignment_adjustments(row):
    return row['Alignment'] + (row['Product Strength'] + row['Marketing Support'] + row['Monetary Support']) * 0.1

# Function to apply impact adjustments
def apply_impact_adjustments(row):
    adjusted_impact = row['Impact YoY Change'] + (row['Historical Sales Data'] * 0.01 + row['Customer Sentiment'] * 5)
    time_weight = {'Short-term': 1.2, 'Medium-term': 1.0, 'Long-term': 0.8}
    adjusted_impact *= time_weight[row['Time Sensitivity Label']]
    return adjusted_impact

# Function to create a Plotly scatter plot with quadrants
def create_plotly_scatter(df):
    fig = px.scatter(
        df, 
        x='Adjusted Alignment', 
        y='Adjusted Impact Score', 
        color='Time Sensitivity Label', 
        hover_data=['Model'],
        labels={'Adjusted Alignment': 'Adjusted Alignment', 'Adjusted Impact Score': 'Adjusted Impact Score'},
        title='Impact-Alignment Matrix'
    )
    
    # Add horizontal and vertical lines for the quadrants
    mean_alignment = df['Adjusted Alignment'].mean()
    mean_impact = df['Adjusted Impact Score'].mean()
    fig.add_shape(
        type="line",
        x0=mean_alignment, x1=mean_alignment, y0=df['Adjusted Impact Score'].min(), y1=df['Adjusted Impact Score'].max(),
        line=dict(color="Red", width=2)
    )
    fig.add_shape(
        type="line",
        x0=df['Adjusted Alignment'].min(), x1=df['Adjusted Alignment'].max(), y0=mean_impact, y1=mean_impact,
        line=dict(color="Red", width=2)
    )
    
    # Add annotations for the quadrants
    fig.add_annotation(x=mean_alignment - 1.5, y=df['Adjusted Impact Score'].max() - 200,
                       text="High Impact, Low Alignment",
                       showarrow=False,
                       font=dict(size=12, color="black"),
                       bgcolor="white")
    
    fig.add_annotation(x=mean_alignment + 1.5, y=df['Adjusted Impact Score'].max() - 200,
                       text="High Impact, High Alignment",
                       showarrow=False,
                       font=dict(size=12, color="black"),
                       bgcolor="white")
    
    fig.add_annotation(x=mean_alignment - 1.5, y=df['Adjusted Impact Score'].min() + 200,
                       text="Low Impact, Low Alignment",
                       showarrow=False,
                       font=dict(size=12, color="black"),
                       bgcolor="white")
    
    fig.add_annotation(x=mean_alignment + 1.5, y=df['Adjusted Impact Score'].min() + 200,
                       text="Low Impact, High Alignment",
                       showarrow=False,
                       font=dict(size=12, color="black"),
                       bgcolor="white")
    
    return fig

# Set custom CSS for a night mode look
st.markdown("""
    <style>
    body {
        background-color: #121212;
        color: #e0e0e0;
    }
    .stButton>button {
        background-color: #333;
        color: #fff;
        border: none;
    }
    .stButton>button:hover {
        background-color: #555;
        color: #fff;
        border: none;
    }
    .star-rating {
        display: flex;
        direction: row;
    }
    .star {
        font-size: 24px;
        cursor: pointer;
        color: #666;
    }
    .star.selected {
        color: gold;
    }
    .css-1cpxqw2 edgvbvh3 {
        color: #e0e0e0;
    }
    .css-1cpxqw2 p {
        color: #e0e0e0;
    }
    </style>
    """, unsafe_allow_html=True)

# Define core Vans SKUs
vans_skus = ["Vans Old Skool", "Vans Authentic", "Vans Slip-On"]

# Define alignment categories
alignment_categories = ["Price", "Function", "Fit", "Material", "Color", "Pattern"]

# Function to calculate average alignment score
def calculate_alignment_score(scores):
    return sum(scores) / len(scores)

# Function to determine impact level
def get_impact_level(impact):
    if impact > 30:
        return "High"
    elif 10 <= impact <= 30:
        return "Medium"
    else:
        return "Low"

# Function to render star ratings
def render_star_ratings(key):
    if f"rating_{key}" not in st.session_state:
        st.session_state[f"rating_{key}"] = 3  # default rating
    
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        if st.button("★", key=f"{key}_1"):
            st.session_state[f"rating_{key}"] = 1
    with col2:
        if st.button("★", key=f"{key}_2"):
            st.session_state[f"rating_{key}"] = 2
    with col3:
        if st.button("★", key=f"{key}_3"):
            st.session_state[f"rating_{key}"] = 3
    with col4:
        if st.button("★", key=f"{key}_4"):
            st.session_state[f"rating_{key}"] = 4
    with col5:
        if st.button("★", key=f"{key}_5"):
            st.session_state[f"rating_{key}"] = 5
    
    # Display selected stars
    stars = ["★"] * st.session_state[f"rating_{key}"] + ["☆"] * (5 - st.session_state[f"rating_{key}"])
    st.write(" ".join(stars))
    return st.session_state[f"rating_{key}"]

# Input section for new shoe trends
st.title("Vans Trend Reaction Tool")
st.subheader("Add New Shoe Trends")

st.write("""
Use this tool to input new shoe trends and evaluate their alignment with Vans' core SKUs. 
Adjust the sliders for various categories to determine the alignment score.
""")

shoe_models = []
shoe_impact_yoy = []
shoe_time_period = []
historical_sales_data = []
customer_sentiment = []
product_strength = []
marketing_support = []
monetary_support = []

# Enter data for multiple shoes
num_shoes = st.number_input("Number of Shoes to Enter", min_value=1, max_value=10, value=1)
for i in range(num_shoes):
    st.write(f"### Shoe Model Name {i+1}")
    shoe_model = st.text_input(f"Shoe Model Name", key=f"model_{i}")
    shoe_yoy = st.number_input(f"Impact YoY Change for {shoe_model} (%)", value=0.0, key=f"yoy_{i}", format='%f')
    shoe_time = st.selectbox(f"Time Sensitivity for {shoe_model}", ["Less than 6 months", "6 months to 1 year", "More than 1 year"], key=f"time_{i}")
    sales_data_unit = st.selectbox("Unit for Sales Data", ["Units", "Thousands", "Millions"], key=f"unit_{i}")
    sales_data = st.number_input(f"Historical Sales Data for {shoe_model} ({sales_data_unit})", value=0.0, key=f"sales_{i}")
    sentiment = st.slider(f"Customer Sentiment for {shoe_model}", 1, 5, 3, key=f"sentiment_{i}")
    p_strength = st.slider(f"Product Strength for {shoe_model}", 1, 5, 3, key=f"p_strength_{i}")
    m_support = st.slider(f"Marketing Support for {shoe_model}", 1, 5, 3, key=f"m_support_{i}")
    monetary = st.slider(f"Monetary Support for {shoe_model}", 1, 5, 3, key=f"monetary_{i}")

    # Convert sales data based on the unit selected
    if sales_data_unit == "Thousands":
        sales_data *= 1000
    elif sales_data_unit == "Millions":
        sales_data *= 1000000

    shoe_models.append(shoe_model)
    shoe_impact_yoy.append(shoe_yoy)
    shoe_time_period.append(shoe_time)
    historical_sales_data.append(sales_data)
    customer_sentiment.append(sentiment)
    product_strength.append(p_strength)
    marketing_support.append(m_support)
    monetary_support.append(monetary)

# Example data for existing shoes
example_data = {
    "Model": ["Adidas Samba", "Nike Air Force 1", "Adidas Stan Smith", "New Balance 993", "Nike Dunk"],
    "Impact YoY Change": [35, -40, -15, -35, -45],
    "Time Sensitivity": ["Medium-term", "Medium-term", "Short-term", "Short-term", "Short-term"],
    "Historical Sales Data": [200000, 300000, 100000, 50000, 150000],
    "Customer Sentiment": [4, 3, 2, 2, 3],
    "Product Strength": [3, 3, 3, 3, 3],
    "Marketing Support": [3, 3, 3, 3, 3],
    "Monetary Support": [3, 3, 3, 3, 3]
}

example_df = pd.DataFrame(example_data)
example_df['Alignment'] = [4, 3, 2, 1, 5]  # Example alignment scores
example_df['Time Sensitivity Label'] = example_df['Time Sensitivity'].apply(get_time_sensitivity_label)

# Create DataFrame for new shoe trends
new_data = {
    "Model": shoe_models,
    "Impact YoY Change": shoe_impact_yoy,
    "Time Sensitivity": shoe_time_period,
    "Historical Sales Data": historical_sales_data,
    "Customer Sentiment": customer_sentiment,
    "Product Strength": product_strength,
    "Marketing Support": marketing_support,
    "Monetary Support": monetary_support
}

new_df = pd.DataFrame(new_data)

# Ensure new data is processed correctly
new_df['Alignment'] = [3] * len(new_df)  # Example alignment score for new data
new_df['Time Sensitivity Label'] = new_df['Time Sensitivity'].apply(get_time_sensitivity_label)

# Concatenate new data with example data
df = pd.concat([example_df, new_df], ignore_index=True)

# Apply adjustments
df['Adjusted Alignment'] = df.apply(apply_alignment_adjustments, axis=1)
df['Adjusted Impact Score'] = df.apply(apply_impact_adjustments, axis=1)

# Interactive star ratings for alignment scores
st.subheader("Evaluate Alignment Scores for Vans SKUs")

alignment_scores = {}
for sku in vans_skus:
    st.write(f"### {sku}")
    scores = []
    for category in alignment_categories:
        st.write(f"**{category}**")
        score = render_star_ratings(f"{sku}_{category}")
        scores.append(score)
    alignment_scores[sku] = calculate_alignment_score(scores)
    st.write(f"**Average Alignment Score for {sku}: {alignment_scores[sku]:.2f}**")

# Add alignment scores to DataFrame
for sku in vans_skus:
    df[f"{sku} Alignment"] = [alignment_scores[sku]] * len(df)

# Calculate and display impact level and time sensitivity
df["Impact Level"] = df["Impact YoY Change"].apply(get_impact_level)
df["Time Sensitivity Label"] = df["Time Sensitivity"].apply(get_time_sensitivity_label)

st.subheader("Calculated Impact Levels and Time Sensitivity")
AgGrid(df)

# Visualization using Plotly
st.subheader("Impact-Alignment Matrix")

fig = create_plotly_scatter(df)
st.plotly_chart(fig)

# Assumption Setting
st.subheader("Assumption Setting")
product_strength = st.slider("Product Strength", 1, 5, 3)
marketing_support = st.slider("Marketing Support", 1, 5, 3)
monetary_support = st.slider("Monetary Support", 1, 5, 3)

# Output section
st.subheader("Output and Recommendations")

# Determine output based on impact and alignment
output_messages = {
    "High Impact, High Alignment": "Major investment in production and marketing, wide availability.",
    "High Impact, Medium Alignment": "Moderate marketing push, monitor performance.",
    "Medium Impact, High Alignment": "Maintain current levels, focus on niche marketing.",
    "Low Impact, High Alignment": "Maintain presence, limited investment.",
    "Low Impact, Low Alignment": "Minimal investment, focus on niche markets."
}

for idx, row in df.iterrows():
    alignment = max(row[f"{sku} Alignment"] for sku in vans_skus)
    impact_level = row["Impact Level"]
    if alignment >= 4 and impact_level == "High":
        recommendation = output_messages["High Impact, High Alignment"]
    elif alignment >= 4 and impact_level == "Medium":
        recommendation = output_messages["High Impact, Medium Alignment"]
    elif alignment >= 3 and impact_level == "Medium":
        recommendation = output_messages["Medium Impact, High Alignment"]
    elif alignment >= 3 and impact_level == "Low":
        recommendation = output_messages["Low Impact, High Alignment"]
    else:
        recommendation = output_messages["Low Impact, Low Alignment"]
    
    st.write(f"**{row['Model']}**: {recommendation} with product strength {product_strength}, marketing support {marketing_support}, and monetary support {monetary_support}")

st.write("""
### Recommendations
- **High Impact, High Alignment**: Major investment in production and marketing, wide availability.
- **High Impact, Medium Alignment**: Moderate marketing push, monitor performance.
- **Medium Impact, High Alignment**: Maintain current levels, focus on niche marketing.
- **Low Impact, High Alignment**: Maintain presence, limited investment.
- **Low Impact, Low Alignment**: Minimal investment, focus on niche markets.
""")
