import streamlit as st
import pandas as pd
import plotly.express as px
from st_aggrid import AgGrid
import seaborn as sns
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Watchdog event handler class
class WatchdogHandler(FileSystemEventHandler):
    def on_modified(self, event):
        if event.src_path.endswith('.csv'):
            st.experimental_rerun()

# Start the watchdog observer
if 'observer' not in st.session_state:
    event_handler = WatchdogHandler()
    observer = Observer()
    observer.schedule(event_handler, path='.', recursive=False)
    observer.start()
    st.session_state['observer'] = observer

# Function to create a Plotly scatter plot with quadrants
def create_plotly_scatter(df):
    fig = px.scatter(
        df, 
        x='Alignment', 
        y='Impact YoY Change', 
        color='Time Sensitivity Label', 
        hover_data=['Model'],
        labels={'Alignment': 'Alignment (1-5)', 'Impact YoY Change': 'Impact YoY Change (%)'},
        title='Impact-Alignment Matrix'
    )
    
    # Add horizontal and vertical lines for the quadrants
    fig.add_shape(
        type="line",
        x0=3, x1=3, y0=-50, y1=50,
        line=dict(color="Red", width=2)
    )
    fig.add_shape(
        type="line",
        x0=1, x1=5, y0=0, y1=0,
        line=dict(color="Red", width=2)
    )
    
    # Add annotations for the quadrants
    fig.add_annotation(x=1.5, y=35,
                       text="High Impact, Low Alignment",
                       showarrow=False,
                       font=dict(size=12, color="black"),
                       bgcolor="white")
    
    fig.add_annotation(x=4.5, y=35,
                       text="High Impact, High Alignment",
                       showarrow=False,
                       font=dict(size=12, color="black"),
                       bgcolor="white")
    
    fig.add_annotation(x=1.5, y=-35,
                       text="Low Impact, Low Alignment",
                       showarrow=False,
                       font=dict(size=12, color="black"),
                       bgcolor="white")
    
    fig.add_annotation(x=4.5, y=-35,
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

# Function to determine time sensitivity
def get_time_sensitivity(time_period):
    if time_period == "Less than 6 months":
        return "Short-term"
    elif time_period == "6 months to 1 year":
        return "Medium-term"
    else:
        return "Long-term"

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

# Enter data for multiple shoes
num_shoes = st.number_input("Number of Shoes to Enter", min_value=1, max_value=10, value=1)
for i in range(num_shoes):
    st.write(f"### Shoe {i+1}")
    st.write("**Shoe Model**")
    shoe_model = st.text_input(f"Shoe Model {i+1}", key=f"model_{i}")
    st.write("**Impact YoY Change**")
    shoe_yoy = st.number_input(f"Impact YoY Change for {shoe_model}", value=0, key=f"yoy_{i}")
    st.write("**Time Sensitivity**")
    shoe_time = st.selectbox(f"Time Sensitivity for {shoe_model}", ["Less than 6 months", "6 months to 1 year", "More than 1 year"], key=f"time_{i}")
    st.write("**Historical Sales Data**")
    sales_data = st.number_input(f"Historical Sales Data for {shoe_model}", value=0, key=f"sales_{i}")
    st.write("**Customer Sentiment**")
    sentiment = st.slider(f"Customer Sentiment for {shoe_model}", 1, 5, 3, key=f"sentiment_{i}")
    
    shoe_models.append(shoe_model)
    shoe_impact_yoy.append(shoe_yoy)
    shoe_time_period.append(shoe_time)
    historical_sales_data.append(sales_data)
    customer_sentiment.append(sentiment)

# Example data for existing shoes
example_data = {
    "Model": ["Adidas Samba", "Nike Air Force 1", "Adidas Stan Smith", "New Balance 993", "Nike Dunk"],
    "Impact YoY Change": [35, -40, -15, -35, -45],
    "Time Sensitivity": ["Medium-term", "Medium-term", "Short-term", "Short-term", "Short-term"],
    "Historical Sales Data": [200, 300, 100, 50, 150],
    "Customer Sentiment": [4, 3, 2, 2, 3]
}

example_df = pd.DataFrame(example_data)
example_df['Alignment'] = [4, 3, 2, 1, 5]  # Example alignment scores
example_df['Time Sensitivity Label'] = example_df['Time Sensitivity'].apply(get_time_sensitivity)

# Create DataFrame for new shoe trends
new_data = {
    "Model": shoe_models,
    "Impact YoY Change": shoe_impact_yoy,
    "Time Sensitivity": shoe_time_period,
    "Historical Sales Data": historical_sales_data,
    "Customer Sentiment": customer_sentiment
}

new_df = pd.DataFrame(new_data)

# Ensure new data is processed correctly
new_df['Alignment'] = [3] * len(new_df)  # Example alignment score for new data
new_df['Time Sensitivity Label'] = new_df['Time Sensitivity'].apply(get_time_sensitivity)

# Concatenate new data with example data
df = pd.concat([example_df, new_df], ignore_index=True)

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
df["Time Sensitivity Label"] = df["Time Sensitivity"].apply(get_time_sensitivity)

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

# Run Streamlit app
# Save this script as `vans_trend_tool.py` and run `streamlit run vans_trend_tool.py` in the terminal
