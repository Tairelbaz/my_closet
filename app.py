import streamlit as st
import requests

# 1. Page Configuration
st.set_page_config(page_title="My Digital Closet", layout="wide")

# 2. Sidebar for Settings
with st.sidebar:
    st.header("⚙️ Style Profile")
    st.write("Stylist Profile: Tair")
    
    # Replaced body type with empowering style and fit preferences
    style_vibe = st.selectbox(
        "Primary Style Vibe",
        ["Minimalist", "Vintage / Thrifted", "Streetwear", "Classic / Timeless", "Bohemian"]
    )
    
    fit_preference = st.selectbox(
        "Fit Preference",
        ["Standard / True to Size", "Oversized & Relaxed", "Tailored & Form-fitting"]
    )
    st.caption("Recommendations will adapt to your aesthetic and fit choices.")
    st.button("Log Out")

# 3. Main App Title
st.title("My Digital Closet 👗")
st.write("Welcome to your personal AI stylist!")

# 4. Create the main navigation tabs
tab1, tab2, tab3 = st.tabs([" My Wardrobe 🚪", " Outfit Creator ✨", " Shopping Check 🛍️"])

# Tab 1: The Wardrobe Gallery
with tab1:
    st.subheader("Add to your closet")
    uploaded_file = st.file_uploader("Upload a clothing item", type=["jpg", "jpeg", "png"])
    
    if uploaded_file is not None:
        st.success("Item saved!")
        st.image(uploaded_file, width=200)
        
    st.divider()
    st.write("### Your Collection")
    
    # Gallery categorized across five columns
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        with st.container(border=True):
            st.write("Shirts 👕")
    with col2:
        with st.container(border=True):
            st.write("Pants 👖")
    with col3:
        with st.container(border=True):
            st.write("Shoes 👟")
    with col4:
        with st.container(border=True):
            st.write("Accessories 👜")
    with col5:
        with st.container(border=True):
            st.write("Jewelrys 💍")

# Tab 2: The Stylist
with tab2:
    st.subheader("Today's AI Recommendation")
    
    col_dest, col_plan = st.columns(2)
    with col_dest:
        destination = st.text_input("Where are you going?", placeholder="e.g., Campus library, evening dinner")
    with col_plan:
        activity = st.text_input("What are you doing?", placeholder="e.g., Sitting indoors, long walk")

    if st.button("Generate New Outfit"):
        try:
            # Fetch live weather data
            url = "https://api.open-meteo.com/v1/forecast"
            params = {
                "latitude": 31.9730,
                "longitude": 34.7925,
                "current_weather": True
            }
            res = requests.get(url, params=params).json()
            temp = res["current_weather"]["temperature"]
            
            st.metric(label="Outdoor Temperature", value=f"{temp}°C")
            
            # Recommendation output incorporating context and new style preferences
            st.divider()
            occ = destination if destination else "Everyday Outing"
            st.info(f"💡 **Recommendation for {occ} ({temp}°C):**\n\n"
                    f"Since your vibe is **{style_vibe}** and you prefer a **{fit_preference}** fit, pair a breathable top with structured trousers.")
            
            # 1.0 - 10.0 Rating System
            st.write("#### How did the stylist do?")
            score = st.slider("Rate this outfit suggestion:", min_value=1.0, max_value=10.0, value=8.0, step=0.1)
            if st.button("Submit Rating"):
                st.success(f"Recorded rating: {score}/10.0! Future recommendations will adapt to your taste.")
                
        except Exception as e:
            st.error(f"Could not load weather data: {e}")

# Tab 3: Shopping Check
with tab3:
    st.subheader("Will this look good on me?")
    st.write("Found something online? Paste the store link below to see if it matches your wardrobe.")
    st.text_input("Paste URL from the shop's website:")
    st.button("Analyze Compatibility")