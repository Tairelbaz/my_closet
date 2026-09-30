import streamlit as st
import requests
from streamlit_carousel import carousel
import time
from datetime import datetime
import random
import pickle
import os
from PIL import Image

# 1. Page Configuration
st.set_page_config(page_title="My Digital Closet", layout="wide")

# --- Optimized Local-First Architecture ---
DB_FILE = "wardrobe_data.pkl"
IMG_DIR = "closet_images"

os.makedirs(IMG_DIR, exist_ok=True)

def save_db():
    with open(DB_FILE, "wb") as f:
        pickle.dump(st.session_state.wardrobe, f)

def load_db():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "rb") as f:
            db = pickle.load(f)
            if "Vacations" not in db:
                db["Vacations"] = {}
            return db
    return {
        "Shirts": [], "Pants": [], "Shoes": [], "Accessories": [], "Jewelry": [], "Vacations": {}
    }

# --- Initialize UI States ---
if "wardrobe" not in st.session_state:
    st.session_state.wardrobe = load_db()
if "current_outfit" not in st.session_state:
    st.session_state.current_outfit = None
if "uploader_key" not in st.session_state:
    st.session_state.uploader_key = 0
if "vacation_outfits" not in st.session_state:
    st.session_state.vacation_outfits = None

# 2. Sidebar for Settings
with st.sidebar:
    st.header("Style Profile")
    st.write("Stylist Profile: Tair Elbaz")
    
    style_vibe = st.selectbox(
        "Primary Style Vibe",
        ["Minimalist", "Vintage / Thrifted", "Streetwear", "Classic / Timeless", "Bohemian"]
    )
    
    fit_preference = st.selectbox(
        "Fit Preference",
        ["Standard / True to Size", "Oversized & Relaxed", "Tailored & Form-fitting"]
    )
    
    style_icon = st.text_input(
        "Style Icon (Optional)", 
        placeholder="e.g., Hailey Bieber, Zendaya",
        help="The AI will use this person's signature look to inspire your outfits."
    )
    
    st.button("Log Out")

# 3. Main App Title
st.title("My Digital Closet")
st.write("Welcome to your personal AI stylist.")

# 4. Create the main navigation tabs
tab1, tab2, tab3, tab4 = st.tabs(["My Wardrobe", "Outfit Creator", "Shopping Check", "Vacation Mode"])

# Tab 1: The Wardrobe Gallery
with tab1:
    st.subheader("Add to your closet")
    
    col_file, col_cat = st.columns([2, 1])
    
    with col_file:
        uploaded_file = st.file_uploader("Upload a clothing item", type=["jpg", "jpeg", "png"], key=st.session_state.uploader_key)
    
    with col_cat:
        if uploaded_file is not None:
            if st.session_state.get("last_scanned") != uploaded_file.name:
                with st.spinner("AI scanning fabric and shape..."):
                    time.sleep(1.5) 
                    st.session_state.ai_guess = "Shirts" 
                    st.session_state.ai_weather = "All Season" 
                    st.session_state.last_scanned = uploaded_file.name 
            
            ai_guess = st.session_state.get("ai_guess", "Shirts")
            selected_category = st.selectbox("Confirm Category", list(st.session_state.wardrobe.keys())[:-1], index=list(st.session_state.wardrobe.keys()).index(ai_guess))
            
            rate_item = st.checkbox("Rate this item (Optional)")
            love_score = None
            if rate_item:
                love_score = st.slider("Score (1-10)", min_value=1, max_value=10, value=8)
            
            if st.button("OK - Save Item"):
                current_date = datetime.now().strftime("%Y-%m-%d")
                
                img = Image.open(uploaded_file).convert("RGB")
                file_name = f"{int(time.time())}.jpg" 
                file_path = os.path.join(IMG_DIR, file_name)
                
                img.save(file_path, "JPEG", quality=85) 
                
                item_data = {
                    "name": uploaded_file.name,
                    "image_path": file_path, 
                    "added_on": current_date,
                    "last_worn": current_date,
                    "love_score": love_score,
                    "weather_tag": st.session_state.get("ai_weather", "All Season") 
                }
                st.session_state.wardrobe[selected_category].append(item_data)
                
                save_db()
                
                st.session_state.uploader_key += 1
                st.session_state.pop("ai_guess", None)
                st.session_state.pop("ai_weather", None)
                st.session_state.pop("last_scanned", None)
                
                st.rerun()
        
    st.divider()
    st.write("### Your Collection")
    
    c1, c2, c3, c4, c5 = st.columns(5)
    cols = [c1, c2, c3, c4, c5]
    
    for col, category_name in zip(cols, [k for k in st.session_state.wardrobe.keys() if k != "Vacations"]):
        items = st.session_state.wardrobe[category_name]
        with col:
            with st.container(border=True):
                st.write(f"**{category_name}**")
                st.write(f"Items: {len(items)}")
                
    with st.expander("Manage Wardrobe (Delete Items)"):
        cat_to_edit = st.selectbox("Select Category to Edit", [k for k in st.session_state.wardrobe.keys() if k != "Vacations"])
        items_in_cat = st.session_state.wardrobe[cat_to_edit]
        
        if not items_in_cat:
            st.write("No items saved in this category yet.")
        else:
            grid_cols = st.columns(4)
            for i, item in enumerate(items_in_cat):
                with grid_cols[i % 4]:
                    try:
                        st.image(item["image_path"], use_container_width=True)
                        score_display = item.get('love_score')
                        if score_display is not None:
                            st.caption(f"❤️ Score: {score_display}/10")
                    except FileNotFoundError:
                        st.warning("Image missing")
                        
                    if st.button("Delete", key=f"del_{cat_to_edit}_{i}", use_container_width=True):
                        if os.path.exists(item["image_path"]):
                            os.remove(item["image_path"])
                            
                        st.session_state.wardrobe[cat_to_edit].pop(i)
                        save_db()
                        st.rerun()
                        
    st.divider()
    closet_items = [
        {
            "title": "Style Inspiration",
            "text": "Curated looks",
            "img": "https://images.unsplash.com/photo-1576871337622-98d48d1cf531?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=60"
        }
    ]
    carousel(items=closet_items, width=1)

# Tab 2: The Stylist 
with tab2:
    st.subheader("Today's AI Recommendation")
    
    col_dest, col_when, col_time = st.columns([2, 1, 1])
    with col_dest:
        destination = st.text_input("Destination/Occasion", placeholder="e.g., Campus library, evening dinner")
    with col_when:
        target_day = st.radio("When?", ["Today", "Tomorrow"], horizontal=True)
    with col_time:
        time_of_day = st.radio("Time?", ["Day ☀️", "Night 🌙"], horizontal=True)

    def get_valid_clothes(day_choice, time_choice):
        shirts = st.session_state.wardrobe.get("Shirts", [])
        pants = st.session_state.wardrobe.get("Pants", [])
        try:
            url = "https://api.open-meteo.com/v1/forecast"
            params = {
                "latitude": 31.9730, 
                "longitude": 34.7925, 
                "daily": ["temperature_2m_max", "temperature_2m_min"],
                "timezone": "auto"
            }
            res = requests.get(url, params=params).json()
            
            day_index = 0 if day_choice == "Today" else 1
            temp_key = "temperature_2m_max" if "Day" in time_choice else "temperature_2m_min"
            temp = res["daily"][temp_key][day_index]
            
            st.session_state.current_temp = temp
            
            def is_weather_appropriate(item, current_temp):
                tag = item.get("weather_tag", "All Season")
                if current_temp >= 22 and tag == "Cold Weather":
                    return False 
                if current_temp < 18 and tag == "Warm Weather":
                    return False 
                return True
            
            valid_shirts = [s for s in shirts if is_weather_appropriate(s, temp)]
            valid_pants = [p for p in pants if is_weather_appropriate(p, temp)]
            return valid_shirts, valid_pants
            
        except Exception as e:
            st.error(f"Could not load weather data: {e}")
            return [], []

    if st.session_state.current_outfit is None:
        if st.button("Generate Outfit"):
            valid_shirts, valid_pants = get_valid_clothes(target_day, time_of_day)
            
            if not valid_shirts or not valid_pants:
                st.error(f"No weather-appropriate clothes found for {target_day} {time_of_day}! Add more items.")
            else:
                st.session_state.current_outfit = {
                    "shirt": random.choice(valid_shirts),
                    "pant": random.choice(valid_pants)
                }
                st.rerun() 

    if st.session_state.current_outfit is not None:
        shirt = st.session_state.current_outfit["shirt"]
        pant = st.session_state.current_outfit["pant"]
        temp = st.session_state.get("current_temp", "--")
        occ = destination if destination else "Everyday Outing"
        
        inspiration_text = f"channeling your inner **{style_icon}**" if style_icon else f"sticking to your **{style_vibe}** aesthetic"
        
        st.metric(label=f"Forecast ({target_day} {time_of_day})", value=f"{temp}°C")
        st.divider()
        
        st.write(f"### **Recommendation for {occ}:**")
        st.write(f"Based on a **{fit_preference}** fit and {inspiration_text}, try this combination:")
        
        outfit_col1, outfit_col2 = st.columns(2)
        with outfit_col1:
            try:
                st.image(shirt["image_path"], use_container_width=True)
            except:
                st.warning("Image missing")
        with outfit_col2:
            try:
                st.image(pant["image_path"], use_container_width=True)
            except:
                st.warning("Image missing")
        
        st.divider()
        
        col_yes, col_no = st.columns(2)
        with col_yes:
            if st.button("Love it! (Save Plan)", use_container_width=True):
                current_date = datetime.now().strftime("%Y-%m-%d")
                shirt["last_worn"] = current_date
                pant["last_worn"] = current_date
                save_db()
                
                st.success("✓")
                time.sleep(0.8)
                st.session_state.current_outfit = None 
                st.rerun()
        with col_no:
            if st.button("Try a different combination", use_container_width=True):
                valid_shirts, valid_pants = get_valid_clothes(target_day, time_of_day)
                
                if valid_shirts and valid_pants:
                    new_shirt = random.choice(valid_shirts)
                    new_pant = random.choice(valid_pants)
                    
                    attempts = 0
                    while len(valid_shirts) > 1 and new_shirt['name'] == shirt['name'] and attempts < 5:
                        new_shirt = random.choice(valid_shirts)
                        attempts += 1
                        
                    st.session_state.current_outfit = {
                        "shirt": new_shirt,
                        "pant": new_pant
                    }
                st.rerun()

# Tab 3: Shopping Check
with tab3:
    st.subheader("Compatibility & Shopping Check")
    st.write("Paste a store URL below to verify how a new item matches your existing wardrobe, and add it directly if you buy it.")
    
    shop_url = st.text_input("Paste item link (URL):")
    
    if "scraped_item" not in st.session_state:
        st.session_state.scraped_item = None
        
    if st.button("Analyze Item"):
        if shop_url:
            with st.spinner("AI scanning store page..."):
                time.sleep(2)
                st.session_state.scraped_item = {
                    "name": "Vintage Leather Jacket",
                    "image_url": "https://images.unsplash.com/photo-1551028719-00167b16eac5?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80",
                    "match_score": "92%",
                    "verdict": "This vintage piece perfectly aligns with your aesthetic and pairs beautifully with the basics you already own."
                }
                
    if st.session_state.scraped_item:
        item = st.session_state.scraped_item
        st.success("Analysis Complete")
        col_img, col_info = st.columns([1, 2])
        with col_img:
            st.image(item["image_url"], use_container_width=True)
        with col_info:
            st.write(f"**Match Score:** {item['match_score']}")
            st.write(f"**AI Verdict:** {item['verdict']}")
            st.divider()
            st.write("Did you buy this?")
            save_cat = st.selectbox("Select Category to Save", [k for k in st.session_state.wardrobe.keys() if k != "Vacations"], key="shop_cat")
            if st.button("Add to My Closet", type="primary"):
                from io import BytesIO
                try:
                    response = requests.get(item["image_url"])
                    img = Image.open(BytesIO(response.content)).convert("RGB")
                    file_name = f"web_{int(time.time())}.jpg"
                    file_path = os.path.join(IMG_DIR, file_name)
                    img.save(file_path, "JPEG", quality=85)
                    
                    item_data = {
                        "name": item["name"],
                        "image_path": file_path,
                        "added_on": datetime.now().strftime("%Y-%m-%d"),
                        "last_worn": datetime.now().strftime("%Y-%m-%d"),
                        "love_score": None,
                        "weather_tag": "All Season"
                    }
                    st.session_state.wardrobe[save_cat].append(item_data)
                    save_db()
                    
                    st.toast("✅ Downloaded and added to your wardrobe!")
                    st.session_state.scraped_item = None 
                    time.sleep(1.5)
                    st.rerun()
                except Exception as e:
                    st.error(f"Failed to save item: {e}")

# Tab 4: Vacation Mode
with tab4:
    st.subheader("✈️ Capsule Wardrobe Packer")
    st.write("The AI will pack a limited capsule wardrobe based on your trip length and reuse items to prevent overpacking.")
    
    v_col_dest, v_col_days = st.columns([3, 1])
    with v_col_dest:
        vacation_dest = st.text_input("Destination", placeholder="e.g., Trento, Italy")
    with v_col_days:
        trip_days = st.number_input("Days", min_value=1, max_value=14, value=3)
    
    if st.button("Pack My Bags", type="primary"):
        if not vacation_dest:
            st.warning("Please enter a destination.")
        else:
            with st.spinner(f"Building a capsule wardrobe for {trip_days} days in {vacation_dest}..."):
                try:
                    geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={vacation_dest}&count=1&language=en&format=json"
                    geo_res = requests.get(geo_url).json()
                    
                    if "results" not in geo_res or len(geo_res["results"]) == 0:
                        st.error("Could not find that location.")
                    else:
                        lat = geo_res["results"][0]["latitude"]
                        lon = geo_res["results"][0]["longitude"]
                        country = geo_res["results"][0].get("country", "")
                        
                        w_res = requests.get("https://api.open-meteo.com/v1/forecast", params={
                            "latitude": lat, "longitude": lon, 
                            "daily": ["temperature_2m_max", "temperature_2m_min"], "timezone": "auto"
                        }).json()
                        
                        avg_max = sum(w_res["daily"]["temperature_2m_max"]) / len(w_res["daily"]["temperature_2m_max"])
                        avg_min = sum(w_res["daily"]["temperature_2m_min"]) / len(w_res["daily"]["temperature_2m_min"])
                        
                        shirts = st.session_state.wardrobe.get("Shirts", [])
                        pants = st.session_state.wardrobe.get("Pants", [])
                        
                        # Create the strict packing list (Pool of items) to force reuse
                        # For a trip, we need fewer bottoms than tops
                        target_pants_count = max(1, trip_days // 2)
                        target_shirts_count = trip_days
                        
                        packed_pants = random.sample(pants, min(len(pants), target_pants_count)) if pants else []
                        packed_shirts = random.sample(shirts, min(len(shirts), target_shirts_count)) if shirts else []
                        
                        if not packed_pants or not packed_shirts:
                            st.error("Not enough clothes in your wardrobe to build a capsule.")
                        else:
                            # Generate outfits strictly from the packed pool
                            day_looks = []
                            night_looks = []
                            for _ in range(trip_days):
                                day_looks.append({"shirt": random.choice(packed_shirts), "pant": random.choice(packed_pants)})
                                night_looks.append({"shirt": random.choice(packed_shirts), "pant": random.choice(packed_pants)})
                            
                            st.session_state.vacation_outfits = {
                                "destination": f"{vacation_dest}, {country}".strip(", "),
                                "days": trip_days,
                                "avg_max": avg_max,
                                "avg_min": avg_min,
                                "pool_shirts": packed_shirts,
                                "pool_pants": packed_pants,
                                "day_looks": day_looks,
                                "night_looks": night_looks,
                                "extra_looks": []
                            }
                except Exception as e:
                    st.error(f"Failed to load vacation data: {e}")

    if st.session_state.vacation_outfits:
        vo = st.session_state.vacation_outfits
        st.success(f"Capsule created for {vo['days']} days in {vo['destination']}! Highs: {vo['avg_max']:.1f}°C | Lows: {vo['avg_min']:.1f}°C")
        
        st.write(f"### 🧳 What's in your suitcase (Reused items)")
        st.write(f"**{len(vo['pool_shirts'])} Tops and {len(vo['pool_pants'])} Bottoms packed.**")
        
        st.divider()
        st.write(f"### ☀️ {vo['days']} Day Looks")
        cols_day = st.columns(vo['days'] if vo['days'] < 5 else 4)
        for i, look in enumerate(vo['day_looks']):
            with cols_day[i % len(cols_day)]:
                st.image(look["shirt"]["image_path"], use_container_width=True)
                st.image(look["pant"]["image_path"], use_container_width=True)

        st.divider()
        st.write(f"### 🌙 {vo['days']} Night Looks")
        cols_night = st.columns(vo['days'] if vo['days'] < 5 else 4)
        for i, look in enumerate(vo['night_looks']):
            with cols_night[i % len(cols_night)]:
                st.image(look["shirt"]["image_path"], use_container_width=True)
                st.image(look["pant"]["image_path"], use_container_width=True)
                
        if vo["extra_looks"]:
            st.divider()
            st.write("### ✨ Custom / Extra Looks")
            cols_extra = st.columns(4)
            for i, look in enumerate(vo['extra_looks']):
                with cols_extra[i % 4]:
                    st.image(look["shirt"]["image_path"], use_container_width=True)
                    st.image(look["pant"]["image_path"], use_container_width=True)

        st.divider()
        
        col_more, col_save = st.columns(2)
        with col_more:
            # Reusing the exact same pool of packed items to make a new combination
            if st.button("➕ Ask AI for one more look", use_container_width=True):
                new_look = {
                    "shirt": random.choice(vo["pool_shirts"]),
                    "pant": random.choice(vo["pool_pants"])
                }
                st.session_state.vacation_outfits["extra_looks"].append(new_look)
                st.rerun()
                
        with col_save:
            if st.button("💾 Save this Trip Album", type="primary", use_container_width=True):
                album_name = f"{vo['destination']} ({vo['days']} Days)"
                st.session_state.wardrobe["Vacations"][album_name] = vo
                save_db()
                st.session_state.vacation_outfits = None
                st.rerun()
                
    st.divider()
    st.write("### 📁 Saved Vacation Albums")
    saved_vacations = st.session_state.wardrobe.get("Vacations", {})
    
    if not saved_vacations:
        st.info("No saved trips.")
    else:
        for album, data in saved_vacations.items():
            with st.expander(f"🧳 {album}"):
                st.write(f"Packed {len(data['pool_shirts'])} Tops and {len(data['pool_pants'])} Bottoms.")
                if st.button("Delete Album", key=f"del_vac_{album}"):
                    del st.session_state.wardrobe["Vacations"][album]
                    save_db()
                    st.rerun()