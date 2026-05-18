import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd


def fetch_website(url):
    if not url.startswith("http"):
        url = "https://" + url

    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers, timeout=10)
    response.raise_for_status()
    return response.text, url


def analyze_website(html, url):
    soup = BeautifulSoup(html, "html.parser")

    title = soup.title.string.strip() if soup.title and soup.title.string else ""

    meta_tag = soup.find("meta", attrs={"name": "description"})
    meta_description = meta_tag["content"].strip() if meta_tag and meta_tag.get("content") else ""

    h1_tags = soup.find_all("h1")
    h2_tags = soup.find_all("h2")
    images = soup.find_all("img")
    images_without_alt = [img for img in images if not img.get("alt")]

    page_text = soup.get_text(separator=" ", strip=True)
    word_count = len(page_text.split()) if page_text else 0

    cta_keywords = [
        "buy", "sign up", "contact", "book", "get started",
        "subscribe", "download", "try", "start", "learn more"
    ]

    links_and_buttons = soup.find_all(["a", "button"])
    ctas_found = []

    for item in links_and_buttons:
        text = item.get_text(" ", strip=True).lower()
        if any(keyword in text for keyword in cta_keywords):
            ctas_found.append(text)

    seo_score = 100

    if not title:
        seo_score -= 20
    elif len(title) < 30 or len(title) > 65:
        seo_score -= 10

    if not meta_description:
        seo_score -= 20
    elif len(meta_description) < 70 or len(meta_description) > 160:
        seo_score -= 10

    if len(h1_tags) != 1:
        seo_score -= 15

    if len(images) > 0 and len(images_without_alt) / len(images) > 0.3:
        seo_score -= 15

    if not ctas_found:
        seo_score -= 15

    seo_score = max(seo_score, 0)

    accessibility_score = 100
    if len(images) > 0:
        alt_ratio = len(images_without_alt) / len(images)
        accessibility_score -= int(alt_ratio * 50)
    accessibility_score = max(accessibility_score, 0)

    ux_score = 100
    if not ctas_found:
        ux_score -= 30
    if word_count > 3000:
        ux_score -= 15
    if len(h2_tags) == 0:
        ux_score -= 10
    ux_score = max(ux_score, 0)

    return {
        "url": url,
        "title": title,
        "title_length": len(title),
        "meta_description": meta_description,
        "meta_description_length": len(meta_description),
        "h1_count": len(h1_tags),
        "h2_count": len(h2_tags),
        "image_count": len(images),
        "images_without_alt": len(images_without_alt),
        "word_count": word_count,
        "cta_count": len(ctas_found),
        "ctas_found": ctas_found[:10],
        "seo_score": seo_score,
        "ux_score": ux_score,
        "accessibility_score": accessibility_score,
    }


def generate_suggestions(result):
    suggestions = []

    if not result["title"]:
        suggestions.append("Add a clear page title.")
    elif result["title_length"] < 30:
        suggestions.append("Your title is too short. Make it more descriptive.")
    elif result["title_length"] > 65:
        suggestions.append("Your title is too long. Shorten it for better SEO.")

    if not result["meta_description"]:
        suggestions.append("Add a meta description to improve search visibility.")
    elif result["meta_description_length"] < 70:
        suggestions.append("Your meta description is too short.")
    elif result["meta_description_length"] > 160:
        suggestions.append("Your meta description is too long.")

    if result["h1_count"] == 0:
        suggestions.append("Add one main H1 heading.")
    elif result["h1_count"] > 1:
        suggestions.append("Use only one H1 heading for better structure.")

    if result["images_without_alt"] > 0:
        suggestions.append("Add alt text to images for accessibility and SEO.")

    if result["cta_count"] == 0:
        suggestions.append("Add a clear call-to-action such as 'Contact Us' or 'Get Started'.")

    if result["word_count"] > 3000:
        suggestions.append("The page contains a lot of text. Consider simplifying the content.")

    return suggestions


def build_report(result, suggestions):
    report = f"""
SMARTLANDING AI REPORT

Website:
{result['url']}

Scores:
SEO Score: {result['seo_score']}/100
UX Score: {result['ux_score']}/100
Accessibility Score: {result['accessibility_score']}/100

Website Information:
Title: {result['title']}
Title Length: {result['title_length']}
Meta Description: {result['meta_description']}
Meta Description Length: {result['meta_description_length']}

Structure:
H1 Count: {result['h1_count']}
H2 Count: {result['h2_count']}
Word Count: {result['word_count']}

Images:
Total Images: {result['image_count']}
Images Without Alt: {result['images_without_alt']}

CTA:
CTA Count: {result['cta_count']}
Detected CTAs: {', '.join(result['ctas_found']) if result['ctas_found'] else 'None'}

Suggestions:
"""
    if suggestions:
        for suggestion in suggestions:
            report += f"- {suggestion}\n"
    else:
        report += "- No major issues found.\n"

    return report


st.set_page_config(
    page_title="SmartLanding AI",
    page_icon="📊",
    layout="wide"
)

st.markdown(
    """
    <style>
    .hero {
        background: linear-gradient(135deg, #0f172a, #1e293b, #312e81);
        padding: 60px 50px;
        border-radius: 28px;
        color: white;
        margin-bottom: 35px;
        box-shadow: 0 20px 50px rgba(0,0,0,0.25);
        animation: fadeIn 1s ease-in-out;
    }

    .hero h1 {
        font-size: 58px;
        font-weight: 800;
        margin-bottom: 18px;
    }

    .hero p {
        font-size: 20px;
        color: #cbd5e1;
        max-width: 850px;
        line-height: 1.6;
    }

    .badge {
        display: inline-block;
        padding: 8px 16px;
        border-radius: 999px;
        background: rgba(255,255,255,0.12);
        color: #c7d2fe;
        margin-bottom: 18px;
        border: 1px solid rgba(255,255,255,0.15);
    }

    .feature-pill {
        display: inline-block;
        background: rgba(255,255,255,0.12);
        padding: 10px 16px;
        border-radius: 14px;
        margin: 6px 6px 0 0;
        color: #e2e8f0;
        border: 1px solid rgba(255,255,255,0.12);
    }

    .input-box {
        background: #ffffff;
        padding: 26px;
        border-radius: 22px;
        box-shadow: 0 12px 35px rgba(15,23,42,0.10);
        margin-bottom: 30px;
    }

    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    </style>

    <div class="hero">
        <div class="badge">AI-powered SEO & UX Intelligence</div>
        <h1>SmartLanding AI</h1>
        <p>
            Analyze any website in seconds. Detect SEO issues, CTA structure,
            accessibility gaps, UX signals, and generate a downloadable website report.
        </p>
        <div>
            <span class="feature-pill">📊 SEO Scoring</span>
            <span class="feature-pill">🎯 CTA Detection</span>
            <span class="feature-pill">🧩 UX Signals</span>
            <span class="feature-pill">🖼️ Accessibility</span>
            <span class="feature-pill">📥 Report Export</span>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown('<div class="input-box">', unsafe_allow_html=True)

st.subheader("Start Website Analysis")
st.write("Enter a website URL below and generate an instant SEO / UX report.")

url = st.text_input("Website URL", placeholder="example.com")

analyze_clicked = st.button("Analyze Website")

st.markdown("</div>", unsafe_allow_html=True)

if analyze_clicked:
    if not url:
        st.warning("Please enter a website URL.")
    else:
        try:
            with st.spinner("Analyzing website..."):
                html, final_url = fetch_website(url)
                result = analyze_website(html, final_url)
                suggestions = generate_suggestions(result)

            overall_score = round(
                (result["seo_score"] + result["ux_score"] + result["accessibility_score"]) / 3
            )

            st.markdown("---")
            st.subheader("📊 Website Analysis Dashboard")

            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.metric("Overall Score", f"{overall_score}/100")

            with col2:
                st.metric("SEO Score", f"{result['seo_score']}/100")

            with col3:
                st.metric("UX Score", f"{result['ux_score']}/100")

            with col4:
                st.metric("Accessibility", f"{result['accessibility_score']}/100")

            st.progress(overall_score / 100)

            st.markdown("---")
            st.subheader("📈 Score Breakdown Chart")

            score_df = pd.DataFrame({
                "Category": ["SEO", "UX", "Accessibility"],
                "Score": [
                    result["seo_score"],
                    result["ux_score"],
                    result["accessibility_score"]
                ]
            })

            st.bar_chart(score_df.set_index("Category"))

            st.markdown("---")
            st.subheader("🌐 Website Information")

            info_col1, info_col2 = st.columns(2)

            with info_col1:
                st.write(f"**URL:** {result['url']}")
                st.write(f"**Title:** {result['title'] if result['title'] else 'Not found'}")
                st.write(
                    f"**Meta Description:** "
                    f"{result['meta_description'] if result['meta_description'] else 'Not found'}"
                )

            with info_col2:
                st.write(f"**Word Count:** {result['word_count']}")
                st.write(f"**H1 Count:** {result['h1_count']}")
                st.write(f"**H2 Count:** {result['h2_count']}")

            st.markdown("---")
            st.subheader("🧩 Detailed Analysis")

            analysis_df = pd.DataFrame({
                "Metric": [
                    "Title Length",
                    "Meta Description Length",
                    "H1 Count",
                    "H2 Count",
                    "Images",
                    "Images Without Alt",
                    "Word Count",
                    "CTA Count",
                ],
                "Value": [
                    result["title_length"],
                    result["meta_description_length"],
                    result["h1_count"],
                    result["h2_count"],
                    result["image_count"],
                    result["images_without_alt"],
                    result["word_count"],
                    result["cta_count"],
                ],
            })

            st.dataframe(analysis_df, use_container_width=True)

            st.markdown("---")
            st.subheader("🖼️ Image Accessibility")

            image_df = pd.DataFrame({
                "Type": ["Images With Alt", "Images Without Alt"],
                "Count": [
                    result["image_count"] - result["images_without_alt"],
                    result["images_without_alt"]
                ]
            })

            st.bar_chart(image_df.set_index("Type"))

            if result["ctas_found"]:
                st.markdown("---")
                st.subheader("🎯 Detected CTAs")

                unique_ctas = list(dict.fromkeys(result["ctas_found"]))

                for cta in unique_ctas:
                    st.success(cta)

            st.markdown("---")
            st.subheader("💡 Improvement Suggestions")

            if suggestions:
                for suggestion in suggestions:
                    st.warning(suggestion)
            else:
                st.success("No major issues found.")

            st.markdown("---")
            st.subheader("📥 Download Report")

            report = build_report(result, suggestions)

            st.download_button(
                label="Download TXT Report",
                data=report,
                file_name="smartlanding_report.txt",
                mime="text/plain"
            )

        except Exception as e:
            st.error(f"Error: {e}")