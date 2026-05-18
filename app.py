import streamlit as st
import requests
from bs4 import BeautifulSoup

from urllib.parse import urlparse


def fetch_website(url):
    if not url.startswith("http"):
        url = "https://" + url

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    response = requests.get(url, headers=headers, timeout=10)
    response.raise_for_status()
    return response.text, url


def analyze_website(html, url):
    soup = BeautifulSoup(html, "html.parser")

    title = soup.title.string.strip() if soup.title and soup.title.string else ""
    meta_description_tag = soup.find("meta", attrs={"name": "description"})
    meta_description = meta_description_tag["content"].strip() if meta_description_tag and meta_description_tag.get("content") else ""

    h1_tags = soup.find_all("h1")
    h2_tags = soup.find_all("h2")
    images = soup.find_all("img")

    images_without_alt = [img for img in images if not img.get("alt")]

    page_text = soup.get_text(separator=" ", strip=True)
    readability_score = 70 if page_text else 0

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
        "readability_score": round(readability_score, 2),
        "cta_count": len(ctas_found),
        "ctas_found": ctas_found[:10],
        "seo_score": seo_score,
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
        suggestions.append("Add a clear call-to-action button such as 'Contact Us' or 'Get Started'.")

    if result["readability_score"] < 50:
        suggestions.append("Simplify the text to improve readability.")

    return suggestions


st.set_page_config(page_title="SmartLanding AI", page_icon="📊")

st.title("SmartLanding AI")
st.write("Analyze basic SEO, UX, readability, and CTA structure of a website.")

url = st.text_input("Enter website URL", placeholder="example.com")

if st.button("Analyze Website"):
    if not url:
        st.warning("Please enter a website URL.")
    else:
        try:
            with st.spinner("Analyzing website..."):
                html, final_url = fetch_website(url)
                result = analyze_website(html, final_url)
                suggestions = generate_suggestions(result)

            st.subheader("Overall Score")
            st.metric("SEO / UX Score", f"{result['seo_score']}/100")

            st.subheader("Website Information")
            st.write("URL:", result["url"])
            st.write("Title:", result["title"])
            st.write("Meta Description:", result["meta_description"])

            st.subheader("Analysis Results")
            st.write("Title Length:", result["title_length"])
            st.write("Meta Description Length:", result["meta_description_length"])
            st.write("H1 Count:", result["h1_count"])
            st.write("H2 Count:", result["h2_count"])
            st.write("Images:", result["image_count"])
            st.write("Images Without Alt:", result["images_without_alt"])
            st.write("Readability Score:", result["readability_score"])
            st.write("CTA Count:", result["cta_count"])

            if result["ctas_found"]:
                st.subheader("Detected CTAs")
                for cta in result["ctas_found"]:
                    st.write("-", cta)

            st.subheader("Suggestions")
            if suggestions:
                for suggestion in suggestions:
                    st.write("✅", suggestion)
            else:
                st.success("No major issues found.")

        except Exception as e:
            st.error(f"Error: {e}")