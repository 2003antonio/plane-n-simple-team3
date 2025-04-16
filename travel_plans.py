import streamlit as st
from firebase_admin import db
import json

def delete_entire_plan(uid, plan_name):
    try:
        db.reference(f"travel_plans/{uid}/{plan_name}").delete()
        st.success(f"🗑 Deleted travel plan: {plan_name}")
    except Exception as e:
        st.error(f"❌ Failed to delete travel plan: {e}")

def save_plan(uid, plan_name, plan_data):
    try:
        db.reference(f"travel_plans/{uid}/{plan_name}").set(json.dumps(plan_data))
        st.success(f"✅ Travel plan '{plan_name}' saved under travel_plans/{uid}")
    except Exception as e:
        st.error(f"❌ Failed to save travel plan: {e}")


def get_user_plans(uid):
    try:
        plans = db.reference(f"travel_plans/{uid}").get()
        if not plans:
            st.info("ℹ️ No travel plans found.")
            return {}

        return plans
    except Exception as e:
        st.error(f"❌ Failed to read travel plans: {e}")
        return {}


def delete_item_from_plan(uid, plan_name, item_type, index):
    try:
        ref = db.reference(f"travel_plans/{uid}/{plan_name}")
        plan = json.loads(ref.get())
        if 0 <= index < len(plan.get(item_type)):
            plan.get(item_type).pop(index)
            ref.set(json.dumps(plan))
    except Exception as e:
        st.error(f"❌ Failed to delete item from plan: {e}")


def main():
    st.title("📘 Your Travel Plans")

    uid = st.session_state.get("uid")
    if not uid:
        st.error("❌ You must be logged in to access your travel plans.")
        return

    travel_plans = get_user_plans(uid)

    with st.expander(label="Create a New Travel Plan", icon="➕"):
        new_plan_name = st.text_input("Plan Name", key="new_plan_name")
        if st.button("Create Plan"):
            if new_plan_name and new_plan_name not in travel_plans:
                save_plan(uid, new_plan_name, {"flights": [], "pois": []})
                st.rerun()
            else:
                st.warning("Plan already exists or name is empty.")

    for plan_name, plan in travel_plans.items():
        plan = json.loads(plan)

        with st.expander(label=plan_name, icon="📍"):
            col1, col2 = st.columns([5, 1])
            with col2:
                if st.button("🗑 Delete Plan", key=f"delete_plan_{plan_name}"):
                    delete_entire_plan(uid, plan_name)
                    st.rerun()

            st.markdown("<span style=\"font-size: 20px;margin-left:24px\">✈️ Flights</span>", unsafe_allow_html=True)
            for i, flight in enumerate(plan.get("flights", [])):

                with st.container(border=True):

                    col1, col2 = st.columns([5, 1])

                    with col1:
                        st.markdown(f'<span style=\"font-size: 20px; margin-right: 20px\">🛫 {flight.get("from")} → 🛬 {flight.get("to")} ({flight.get("airline")} | {flight.get("aircraft", {})})</span>💲{flight.get("price")}', unsafe_allow_html=True)
                        st.markdown(f"Departure: {flight.get('departure')}")
                        st.markdown(f"Arrival: {flight.get('arrival')}")
                        st.markdown(f"Duration: {flight.get('duration', 'N/A')}  ")
                
                    with col2:
                        if st.button(f"❌ Remove Flight #{i+1}", key=f"rm_flight_{plan_name}_{i}"):
                            delete_item_from_plan(uid, plan_name, "flights", i)
                            st.rerun()

            st.markdown(f"""<span style=\"font-size: 20px;margin-left:24px\">📌 Points of Interest</span>""", unsafe_allow_html=True)
            for i, poi in enumerate(plan.get("pois", [])):
                name = poi.get("name", "Unnamed POI")
                category = poi.get("category", "Unknown")

                with st.container(border=True):
                    col1, col2 = st.columns([5, 1])
                    with col1:
                        st.markdown(f"{name} ({category})")
                    with col2:
                        if st.button(f"❌ Remove POI #{i+1}", key=f"rm_poi_{plan_name}_{i}"):
                            delete_item_from_plan(uid, plan_name, "pois", i)
                            st.rerun()


if __name__ == "__main__":
    main()