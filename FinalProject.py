"""
Name: Harsh Johari
CS230: Section 4 Professor Xu
Data:Starbucks Locations
URL:

Description:
The "Starbucks Locator" application allows users to explore Starbucks
locations globally through interactive filters and visualizations.
Users can search based on geographical preferences and view detailed maps
and charts that highlight Starbucks distribution in key cities, offering a
user-friendly interface for comprehensive Starbucks store analysis.
"""


import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from geopy.distance import geodesic
import matplotlib.pyplot as plt

# [PY1] Function with a default parameter
def load_data(filepath='starbucks_10000_sample.csv'):  # Default parameter
    """Load and clean data."""
    df = pd.read_csv(filepath)
    for col in df.select_dtypes(include=['object']).columns:
        df[col] = df[col].apply(lambda x: x.strip() if isinstance(x, str) else x)  # [DA1] Cleaning data with a lambda function
    return df

# [PY3] Function returns a value and is called at least twice in your program (once in main and could be called elsewhere for different datasets)
def filter_data(df, country, state, city, radius, ownership_type):
    """Filter data based on user input."""
    df = df.sort_values(by=['CountryCode', 'City'], ascending=[True, False])  # [DA2] Sorting data by Country and City
    filtered_df = df[(df['CountryCode'] == country) &  # [DA5] Filtering by multiple conditions with AND
                     (df['CountrySubdivisionCode'] == state) &
                     (df['OwnershipType'].isin(ownership_type))].copy()
    if city:
        center = filtered_df.loc[filtered_df['City'] == city, ['Latitude', 'Longitude']].iloc[0]
        center = (center['Latitude'], center['Longitude'])
        filtered_df['Distance'] = filtered_df.apply(lambda row: geodesic(center, (row['Latitude'], row['Longitude'])).miles, axis=1)  # [DA9] Adding a new column with calculation
        filtered_df = filtered_df[filtered_df['Distance'] <= radius]  # [DA4] Filtering by one condition
    return filtered_df

def create_pivot_table(df):
    pivot = pd.pivot_table(df, values='Distance', index=['CountryCode', 'City'], aggfunc='mean')  # [DA6] Creating a pivot table
    return pivot

# [ST4] Displaying data table in the UI
def show_data_table(df):
    """Display the filtered data in a table format."""
    if not df.empty:
        st.write("Filtered Data Table:")
        st.dataframe(df)  # Display data table
    else:
        st.write("No data available to display based on the current filters.")

def create_detailed_map(df):
    """Create a folium map to display locations."""
    if df.empty:
        return None
    m = folium.Map(location=[df['Latitude'].mean(), df['Longitude'].mean()], zoom_start=11)
    for _, row in df.iterrows(): # [DA8] Explicit iteration with iterrows()
        folium.Marker(
            location=[row['Latitude'], row['Longitude']],
            popup=f"{row['Name']}, {row['City']}, {row['OwnershipType']}",
            tooltip=row['Name'],
            icon=folium.Icon(icon="coffee", prefix='fa', color='green')
        ).add_to(m)
    return m

def display_map_and_data(filtered_data):
    """Display the map and data tables."""
    map_obj = create_detailed_map(filtered_data)  # [VIZ1] Detailed map with interactive features
    if map_obj:
        st_folium(map_obj, width=700, height=500)  # [ST4] Using Streamlit folium integration for map
    else:
        st.write("No data available to show on the map.")

# [VIZ2] Plot pie chart for ownership distribution
def plot_pie_chart(df):
    ownership_counts = df['OwnershipType'].value_counts()  # [DA3] Getting top values of a column
    plt.figure(figsize=(8, 8))
    plt.pie(ownership_counts, labels=ownership_counts.index, autopct='%1.1f%%', startangle=140, colors=plt.cm.Paired(range(len(ownership_counts))))
    plt.title('Distribution of Ownership Types')
    st.pyplot(plt)  # Display pie chart

# [VIZ3] Plot bar chart for the top 5 cities within the selected state of the country.
def plot_bar_chart(df, state):
    df_state = df[df['CountrySubdivisionCode'] == state]
    city_counts = df_state['City'].value_counts().head(5)  # [DA3] Getting top largest values of a column
    plt.figure(figsize=(10, 6))
    city_counts.plot(kind='bar', color='green')
    plt.title(f'Top 5 Cities by Number of Starbucks Stores in {state}')
    plt.xlabel('City')
    plt.ylabel('Number of Stores')
    plt.xticks(rotation=45)
    plt.tight_layout()
    st.pyplot(plt)  # Display bar chart

def plot_stores_by_top_cities_usa(df):
    """Plot bar chart for the top 20 cities in the USA."""
    df_usa = df[df['CountryCode'] == 'US']
    city_counts = df_usa['City'].value_counts().head(20)  # [DA3] Getting top values of a column
    plt.figure(figsize=(12, 8))
    city_counts.plot(kind='bar', color='blue')
    plt.title('Number of Starbucks Stores in Top 20 Cities in the USA')
    plt.xlabel('City')
    plt.ylabel('Number of Stores')
    plt.xticks(rotation=45)
    plt.tight_layout()
    st.pyplot(plt)  # Display bar chart

def main():
    st.set_page_config(page_title="Starbucks Locator", page_icon=":coffee:", layout="wide")

    # [ST4] Placing the Starbucks logo in the sidebar
    st.sidebar.image('starbucks.jpg', width=300)  # Adjust the width to fit the sidebar nicely

    # Application Title and Markdown
    st.title('Starbucks Locator')
    st.markdown("Explore Starbucks locations around the world.", unsafe_allow_html=True)

    # [ST1], [ST2], [ST3] Different Streamlit widgets used here for user input
    data = load_data()
    country = st.sidebar.selectbox('Country', data['CountryCode'].unique())
    state = st.sidebar.selectbox('State', data[data['CountryCode'] == country]['CountrySubdivisionCode'].unique())
    city = st.sidebar.selectbox('City',
                                data[(data['CountryCode'] == country) & (data['CountrySubdivisionCode'] == state)][
                                    'City'].unique())
    radius = st.sidebar.slider('Radius (miles)', 0, 50, 10)
    ownership_types = st.sidebar.multiselect('Ownership Type', data['OwnershipType'].unique(),
                                             default=data['OwnershipType'].unique())

    filtered_data = filter_data(data, country, state, city, radius, ownership_types)
    display_map_and_data(filtered_data)

    if st.button('Show Data Table'):
        show_data_table(filtered_data)
    if st.button('Show Pie Chart'):
        plot_pie_chart(filtered_data)
    if st.button('Show Top 5 Cities in Selected State'):
        plot_bar_chart(filtered_data, state)
    if st.button('Show Top 20 US Cities Bar Chart'):
        plot_stores_by_top_cities_usa(data)

if __name__ == "__main__":
    main()
