import streamlit as st
import av

from streamlit_webrtc import (
    webrtc_streamer,
    WebRtcMode,
    RTCConfiguration,
    VideoProcessorBase
)

from src.driver_monitor import DriverMonitor


# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="DriverGuard AI",
    page_icon="🚗",
    layout="wide"
)


# =========================================================
# EMERGENCY CONTACT
# =========================================================

EMERGENCY_CONTACT = "+91XXXXXXXXXX"


# =========================================================
# SESSION STATE
# =========================================================

if "safety_score" not in st.session_state:
    st.session_state.safety_score = 0

if "driver_status" not in st.session_state:
    st.session_state.driver_status = "WAITING"

if "attention_status" not in st.session_state:
    st.session_state.attention_status = "WAITING"

if "yawning_status" not in st.session_state:
    st.session_state.yawning_status = "WAITING"

if "head_direction" not in st.session_state:
    st.session_state.head_direction = "UNKNOWN"

if "safety_status" not in st.session_state:
    st.session_state.safety_status = "WAITING"


# =========================================================
# VIDEO PROCESSOR
# =========================================================

class DriverGuardProcessor(VideoProcessorBase):

    def __init__(self):

        self.monitor = DriverMonitor()

    def recv(self, frame):

        img = frame.to_ndarray(format="bgr24")

        processed_frame, data = self.monitor.process_frame(img)

        # Update Streamlit session state
        st.session_state.safety_score = data["safety_score"]

        st.session_state.driver_status = data["driver_status"]

        st.session_state.attention_status = data["attention_status"]

        st.session_state.yawning_status = data["yawning_status"]

        st.session_state.head_direction = data["head_direction"]

        st.session_state.safety_status = data["safety_status"]

        return av.VideoFrame.from_ndarray(
            processed_frame,
            format="bgr24"
        )


# =========================================================
# TITLE
# =========================================================

st.title("🚗 DriverGuard AI")

st.subheader(
    "Passenger Safety & Driver Monitoring System"
)

st.divider()


# =========================================================
# MAIN LAYOUT
# =========================================================

camera_col, status_col = st.columns(
    [2, 1]
)


# =========================================================
# CAMERA
# =========================================================

with camera_col:

    st.markdown("### 🎥 Live Driver Camera")

    webrtc_streamer(

        key="driverguard-camera",

        mode=WebRtcMode.SENDRECV,

        video_processor_factory=DriverGuardProcessor,

        media_stream_constraints={
            "video": True,
            "audio": False
        },

        async_processing=True
    )


# =========================================================
# DRIVER STATUS
# =========================================================

with status_col:

    st.markdown("### DRIVER STATUS")

    safety_status = st.session_state.safety_status

    if safety_status == "SAFE":

        st.success("🟢 SAFE")

    elif safety_status == "CAUTION":

        st.warning("🟠 CAUTION")

    elif safety_status == "HIGH RISK":

        st.error("🔴 HIGH RISK")

    else:

        st.info("Waiting for driver...")


    st.metric(
        "Safety Score",
        f"{st.session_state.safety_score} / 100"
    )


# =========================================================
# DRIVER CONDITION
# =========================================================

st.divider()

st.markdown("### 🧠 Driver Condition")

col1, col2, col3, col4 = st.columns(4)


with col1:

    if "CRITICAL" in st.session_state.driver_status:

        st.error(
            "🔴 " +
            st.session_state.driver_status
        )

    elif "DROWSY" in st.session_state.driver_status:

        st.warning(
            "🟠 " +
            st.session_state.driver_status
        )

    else:

        st.success("🟢 ALERT")

    st.caption("Alertness")


with col2:

    if "SEVERE" in st.session_state.attention_status:

        st.error(
            "🔴 " +
            st.session_state.attention_status
        )

    elif "DISTRACT" in st.session_state.attention_status:

        st.warning(
            "🟠 " +
            st.session_state.attention_status
        )

    else:

        st.success("🟢 FOCUSED")

    st.caption("Attention")


with col3:

    if "YAWNING" in st.session_state.yawning_status:

        st.warning("🟠 YAWNING")

    else:

        st.success("🟢 LOW")

    st.caption("Fatigue")


with col4:

    st.info(
        st.session_state.head_direction
    )

    st.caption("Head Direction")


# =========================================================
# PASSENGER SAFETY
# =========================================================

st.divider()

st.markdown("### 🛡️ Passenger Safety")


if st.session_state.safety_status == "SAFE":

    st.success(
        "🟢 No immediate safety concerns"
    )

elif st.session_state.safety_status == "CAUTION":

    st.warning(
        "🟠 Driver condition requires attention"
    )

elif st.session_state.safety_status == "HIGH RISK":

    st.error(
        "🔴 HIGH RISK — Passenger safety concern detected"
    )

else:

    st.info(
        "Waiting for driver monitoring..."
    )


# =========================================================
# JOURNEY INFORMATION
# =========================================================

st.markdown("### 🗺️ Journey")

col1, col2, col3 = st.columns(3)

with col1:

    st.metric(
        "Journey Status",
        "Monitoring"
    )

with col2:

    st.metric(
        "Warnings",
        "Live"
    )

with col3:

    st.metric(
        "AI System",
        "Active"
    )


# =========================================================
# EMERGENCY ASSISTANCE
# =========================================================

st.divider()

st.markdown("### 🚨 Emergency Assistance")

st.warning(
    "If you feel unsafe, use the emergency assistance button."
)


# =========================================================
# GET HELP
# =========================================================

st.markdown(
    f"""
    <a href="tel:{EMERGENCY_CONTACT}">
        <button style="
            width:100%;
            height:60px;
            font-size:22px;
            font-weight:bold;
            background-color:#d32f2f;
            color:white;
            border:none;
            border-radius:10px;
            cursor:pointer;
        ">
        🚨 GET HELP — CALL EMERGENCY CONTACT
        </button>
    </a>
    """,
    unsafe_allow_html=True
)


st.caption(
    "The call button opens the phone's dialer. "
    "A real automatic SMS/voice notification will be "
    "connected in the next stage."
)

