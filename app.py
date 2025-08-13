import streamlit as st
import time
import json
from streamlit_lottie import st_lottie
from forgery_checker import calculate_md5, compare_hashes, detect_changes
from PIL import Image
import tempfile
import numpy as np
import cv2
import os
import base64

# Load Lottie JSON from file
def load_lottie_file(filepath: str):
    with open(filepath, "r") as f:
        return json.load(f)

# Apply animated background with glassmorphism effect
def apply_custom_background():
    st.markdown(
        """
        <style>
        .stApp {
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        }
        .title-text {
            font-size: 2.8rem;
            text-align: center;
            color: #2c3e50;
            font-weight: 800;
            margin-bottom: 0.5rem;
            text-shadow: 1px 1px 3px rgba(0,0,0,0.1);
        }
        .subtitle-text {
            font-size: 1.3rem;
            text-align: center;
            color: #7f8c8d;
            margin-bottom: 2.5rem;
        }
        .section-header {
            font-size: 1.5rem;
            color: #34495e;
            margin-top: 2rem;
            font-weight: 700;
            border-bottom: 2px solid #3498db;
            padding-bottom: 0.3rem;
        }
        .card {
            background: rgba(255, 255, 255, 0.8);
            border-radius: 15px;
            padding: 1.5rem;
            box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.1);
            backdrop-filter: blur(4px);
            -webkit-backdrop-filter: blur(4px);
            border: 1px solid rgba(255, 255, 255, 0.18);
            margin-bottom: 1.5rem;
        }
        .stProgress > div > div > div {
            background-color: #3498db;
        }
        .stButton>button {
            border: 2px solid #3498db;
            border-radius: 20px;
            color: white;
            background-color: #3498db;
            padding: 0.5rem 1.5rem;
            transition: all 0.3s;
        }
        .stButton>button:hover {
            background-color: white;
            color: #3498db;
            border: 2px solid #3498db;
        }
        .tabs-bg {
            background-color: rgba(255,255,255,0.7) !important;
        }
        .stMarkdown {
            margin-bottom: 1rem;
        }
        .warning-box {
            background-color: #fff3cd;
            color: #856404;
            padding: 1rem;
            border-radius: 0.25rem;
            margin: 1rem 0;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

# Streamlit app config
st.set_page_config(
    page_title="Image Authenticity Analyzer", 
    layout="wide", 
    page_icon="🔍",
    initial_sidebar_state="expanded"
)

# Show welcome screen only once
if "show_main" not in st.session_state:
    st.session_state.show_main = False
    with st.spinner("Initializing forensic tools..."):
        lottie_welcome = load_lottie_file("Welcome.json")
        st_lottie(lottie_welcome, height=300, speed=1, loop=False, key="welcome")
        time.sleep(3)
        st.session_state.show_main = True
        st.rerun()

# Main UI
if st.session_state.show_main:
    apply_custom_background()

    # Sidebar with info
    with st.sidebar:
        st.markdown("## 🔍 About This Tool")
        st.markdown("""
        This forensic tool helps detect image tampering using:
        - **MD5 Hash Comparison** for exact match verification
        - **Visual Difference Detection** to highlight altered regions
        - **Advanced algorithms** to identify subtle manipulations
        """)
        
        st.markdown("## 📝 How To Use")
        st.markdown("""
        1. Upload original image
        2. Upload suspected image
        3. View comparison results
        4. Analyze detected differences
        """)
        
        st.markdown("## ℹ️ Technical Details")
        st.markdown("""
        - **MD5 Hashing**: Creates unique fingerprint for each image
        - **OpenCV**: Performs pixel-level comparison
        - **Streamlit**: Interactive web interface
        """)

    # Main content area
    col1, col2 = st.columns([0.7, 0.3])
    
    with col1:
        st.markdown("<div class='title-text'>🔎 Image Forgery Detection </div>", unsafe_allow_html=True)
        st.markdown("<div class='subtitle-text'>Forensic tool to detect digital image tampering and manipulations</div>", unsafe_allow_html=True)
        
        with st.expander("📤 Upload Images", expanded=True):
            st.markdown("### Select images to compare")
            col_upload1, col_upload2 = st.columns(2)
            
            with col_upload1:
                original_file = st.file_uploader("Original Image", type=["jpg", "jpeg", "png"], 
                                              help="Upload the original, unmodified image")
            
            with col_upload2:
                test_file = st.file_uploader("Suspected Image", type=["jpg", "jpeg", "png"], 
                                           help="Upload the potentially modified image")

        if original_file and test_file:
            try:
                progress_bar = st.progress(0)
                
                # Save uploaded files
                with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as orig_temp:
                    orig_temp.write(original_file.read())
                    original_path = orig_temp.name
                    original_size = os.path.getsize(original_path)/1024
                    progress_bar.progress(30)
                
                with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as test_temp:
                    test_temp.write(test_file.read())
                    test_path = test_temp.name
                    test_size = os.path.getsize(test_path)/1024
                    progress_bar.progress(60)
                
                # Open images with PIL
                img1 = Image.open(original_path)
                img2 = Image.open(test_path)
                
                # Image preview
                st.markdown("<div class='section-header'>🖼️ Image Preview</div>", unsafe_allow_html=True)
                tab1, tab2 = st.tabs(["Side-by-Side", "Overlay"])
                
                with tab1:
                    st.image([original_path, test_path], caption=["Original Image", "Suspected Image"], width=350)
                
                with tab2:
                    if img1.size == img2.size:
                        blended = Image.blend(img1.convert('RGBA'), img2.convert('RGBA'), alpha=0.5)
                        st.image(blended, caption="50% Overlay Comparison", width=350)
                    else:
                        st.markdown("<div class='warning-box'>⚠️ Cannot create overlay - images have different dimensions</div>", unsafe_allow_html=True)
                        st.image([img1, img2], caption=["Original", "Suspected"], width=300)
                
                progress_bar.progress(80)
                
                # Analysis section
                st.markdown("<div class='section-header'>🔬 Forensic Analysis</div>", unsafe_allow_html=True)
                
                with st.spinner("Performing cryptographic analysis..."):
                    hash1 = calculate_md5(original_path)
                    hash2 = calculate_md5(test_path)
                    progress_bar.progress(90)
                    
                    st.markdown("#### 🔐 Digital Fingerprint Comparison")
                    col_hash1, col_hash2 = st.columns(2)
                    
                    with col_hash1:
                        st.code(f"Original MD5:\n{hash1}", language="text")
                    
                    with col_hash2:
                        st.code(f"Suspected MD5:\n{hash2}", language="text")
                    
                    if compare_hashes(hash1, hash2):
                        st.success("✅ Cryptographic Verification: Images are identical (same MD5 hash)")
                    else:
                        st.error("❌ Cryptographic Alert: Images have different digital fingerprints")
                        
                        with st.spinner("Detecting visual differences..."):
                            # Read with OpenCV
                            image1 = cv2.imread(original_path)
                            image2 = cv2.imread(test_path)

                            if image1 is not None and image2 is not None:
                                # FIX: Ensure matching size & channels
                                if image1.shape[:2] != image2.shape[:2]:
                                    image2 = cv2.resize(image2, (image1.shape[1], image1.shape[0]))
                                if len(image1.shape) != len(image2.shape):
                                    if len(image1.shape) == 3 and len(image2.shape) == 2:
                                        image2 = cv2.cvtColor(image2, cv2.COLOR_GRAY2BGR)
                                    elif len(image2.shape) == 3 and len(image1.shape) == 2:
                                        image1 = cv2.cvtColor(image1, cv2.COLOR_GRAY2BGR)

                                diff_img = detect_changes(image1, image2)
                                
                                st.markdown("#### 🧐 Visual Tampering Detection")
                                col_diff1, col_diff2 = st.columns(2)
                                
                                with col_diff1:
                                    st.image(diff_img, caption="Difference Map (White = Changed Areas)", 
                                             use_column_width=True, channels="GRAY")
                                
                                with col_diff2:
                                    diff_path = "difference_map.png"
                                    cv2.imwrite(diff_path, diff_img)
                                    
                                    st.download_button(
                                        label="📥 Download Difference Map",
                                        data=open(diff_path, "rb").read(),
                                        file_name="difference_map.png",
                                        mime="image/png"
                                    )
                                    
                                    st.markdown("**Analysis Tips:**")
                                    st.markdown("""
                                    - Bright areas indicate significant changes
                                    - Dark areas show unchanged regions
                                    - Check edges and textures for subtle tampering
                                    """)
                            else:
                                st.error("Could not read images for visual comparison")
                
                progress_bar.progress(100)
                st.success("Analysis complete!")
                
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
            finally:
                if 'original_path' in locals() and os.path.exists(original_path):
                    os.remove(original_path)
                if 'test_path' in locals() and os.path.exists(test_path):
                    os.remove(test_path)
                if 'diff_path' in locals() and os.path.exists(diff_path):
                    os.remove(diff_path)
    
    with col2:
        st.markdown("## 📊 Analysis Summary")
        
        if original_file and test_file:
            if 'hash1' in locals() and 'hash2' in locals():
                with st.container():
                    st.markdown("<div class='card'>", unsafe_allow_html=True)
                    
                    if compare_hashes(hash1, hash2):
                        st.markdown("### 🔒 Verification Result")
                        st.success("**Authentic**")
                        st.markdown("The images are cryptographically identical.")
                        st.markdown("---")
                        st.markdown("**Technical Details**")
                        st.markdown(f"""
                        - MD5 Match: ✅
                        - File Size: {original_size:.2f} KB
                        - Dimensions: {img1.size[0]}×{img1.size[1]} px
                        """)
                    else:
                        st.markdown("### 🚨 Verification Result")
                        st.error("**Potential Tampering Detected**")
                        st.markdown("The images differ in their digital fingerprints.")
                        st.markdown("---")
                        st.markdown("**Technical Details**")
                        st.markdown(f"""
                        - MD5 Match: ❌
                        - Original Size: {original_size:.2f} KB
                        - Suspected Size: {test_size:.2f} KB
                        - Dimensions Match: {'✅' if img1.size == img2.size else '❌'}
                        """)
                    
                    st.markdown("</div>", unsafe_allow_html=True)
        
        with st.expander("💡 Quick Tips"):
            st.markdown("""
            - **For best results**, use high-quality images
            - **Common tampering signs**:
              - Mismatched lighting/shadows
              - Inconsistent noise patterns
              - Cloned regions
            - **Limitations**:
              - MD5 won't detect visually identical copies
              - Resaving images creates new hashes
            """)
        
        with st.expander("📝 Feedback"):
            feedback = st.text_area("Help us improve this tool")
            if st.button("Submit Feedback"):
                st.success("Thank you for your feedback!")
    
    st.markdown("---")
    st.markdown("""
    <p style='text-align:center; color:#7f8c8d; font-size:0.9rem'>
    <a href="#" style="color:#3498db; text-decoration:none">Privacy Policy</a> • 
    <a href="#" style="color:#3498db; text-decoration:none">Terms of Use</a>
    </p>
    """, unsafe_allow_html=True)
