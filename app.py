# MarkItDown Converter: a simple Streamlit app
# Upload PDF, Word, PowerPoint or Excel files and get clean Markdown back.
# Built with Microsoft MarkItDown (MIT licence) and Streamlit.

import io
import zipfile

import pandas as pd
import streamlit as st
from markitdown import MarkItDown

# ---------- Settings you can change ----------
APP_OWNER = "Sara Khurmi"   # Put your own name here
MAX_MB = 10               # Files bigger than this are skipped
PREVIEW_CHARS = 20000     # How much text to show in the Preview tab
FILE_TYPES = ["pdf", "docx", "pptx", "xlsx", "xls", "csv",
              "html", "htm", "txt", "json", "xml"]
OFFICE_TYPES = ["pdf", "docx", "pptx", "xlsx", "xls"]   # real files of these types are never plain text

st.set_page_config(page_title="MarkItDown Converter", page_icon="📄", layout="wide")


# Create the converter once and reuse it (faster on every click)
@st.cache_resource
def get_converter():
    return MarkItDown()


def convert_file(uploaded_file):
    """Convert one uploaded file and return a dictionary with the result."""
    name = uploaded_file.name
    extension = name.rsplit(".", 1)[-1].lower() if "." in name else ""
    result = {"File": name, "Type": extension.upper(), "Status": "",
              "Characters": 0, "Words": 0, "Approx tokens": 0, "markdown": ""}

    # Step 1: check the size
    size_mb = uploaded_file.size / (1024 * 1024)
    if size_mb > MAX_MB:
        result["Status"] = f"Too large (over {MAX_MB} MB)"
        return result

    # Step 2: convert in memory, and never let one bad file crash the app
    try:
        data = io.BytesIO(uploaded_file.getvalue())
        converted = get_converter().convert_stream(data, file_extension="." + extension)
        text = converted.text_content or ""
    except Exception as error:
        # Keep only the last, most useful line of the error message
        lines = [line.strip(" -") for line in str(error).splitlines() if line.strip()]
        reason = lines[-1].split("message:")[-1].strip() if lines else type(error).__name__
        result["Status"] = f"Could not convert: {reason[:120]}"
        return result

    # Step 3: catch damaged or fake files.
    # If a "PDF" or "Word" file comes back exactly as its own raw bytes, MarkItDown
    # could only read it as plain text, so it is not a real file of that type.
    raw_text = uploaded_file.getvalue().decode("utf-8", errors="ignore")
    if extension in OFFICE_TYPES and text.strip() == raw_text.strip():
        result["Status"] = f"Could not convert: not a valid {extension.upper()} file"
        return result

    # Step 4: count characters, words and approximate tokens
    result["markdown"] = text
    result["Characters"] = len(text)
    result["Words"] = len(text.split())
    result["Approx tokens"] = round(len(text) / 4)
    if len(text.strip()) < 50:
        result["Status"] = "Very little text found (maybe a scanned image)"
    else:
        result["Status"] = "Converted"
    return result


def md_name(file_name):
    """Report.pdf becomes Report.md"""
    return file_name.rsplit(".", 1)[0] + ".md"


# ---------- Sidebar ----------
with st.sidebar:
    st.header("How to use")
    st.markdown(
        "1. Upload one or more files.\n"
        "2. Click **Convert to Markdown**.\n"
        "3. Preview, copy or download the Markdown."
    )
    st.header("Privacy")
    st.warning(
        "This app is public. Do not upload confidential or personal files. "
        "Files are processed in memory and are not saved."
    )
    st.header("Supported files")
    st.markdown(", ".join(t.upper() for t in FILE_TYPES) + f"  \nMaximum {MAX_MB} MB per file.")
    st.divider()
    st.markdown(f"Made by **{APP_OWNER}**")
    st.caption("Built with Microsoft MarkItDown and Streamlit")

# ---------- Main page ----------
st.title("📄 MarkItDown Converter")
st.caption("Turn PDF, Word, PowerPoint and Excel files into clean Markdown that any AI can read.")

uploaded_files = st.file_uploader("Upload one or more files",
                                  accept_multiple_files=True, type=FILE_TYPES)

# Convert only when the button is clicked.
# Results go into session_state so they stay on screen after a download click.
if st.button("Convert to Markdown", type="primary"):
    if not uploaded_files:
        st.warning("Please upload at least one file first.")
    else:
        with st.spinner("Converting..."):
            st.session_state["results"] = [convert_file(f) for f in uploaded_files]

results = st.session_state.get("results", [])

if results:
    # Summary table (without the long Markdown text)
    st.subheader("Results")
    table = pd.DataFrame(results).drop(columns=["markdown"])
    st.dataframe(table, hide_index=True)

    # One expander per file that produced some text
    converted = [r for r in results if r["markdown"]]
    for i, r in enumerate(converted):
        with st.expander(f"{r['File']}: {r['Status']}"):
            preview_tab, raw_tab = st.tabs(["Preview", "Raw Markdown"])
            with preview_tab:
                st.markdown(r["markdown"][:PREVIEW_CHARS])
                if len(r["markdown"]) > PREVIEW_CHARS:
                    st.caption(f"Preview trimmed to the first {PREVIEW_CHARS:,} characters. "
                               "The download has the full text.")
            with raw_tab:
                st.code(r["markdown"], language="markdown")
            st.download_button(f"Download {md_name(r['File'])}", data=r["markdown"],
                               file_name=md_name(r["File"]), mime="text/markdown",
                               key=f"download_{i}")

    # Download everything at once
    if converted:
        st.subheader("Download everything")
        combined = "\n\n---\n\n".join(f"# {r['File']}\n\n{r['markdown']}" for r in converted)

        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
            for r in converted:
                zf.writestr(md_name(r["File"]), r["markdown"])

        col1, col2 = st.columns(2)
        col1.download_button("Download all as one file", data=combined,
                             file_name="combined.md", mime="text/markdown")
        col2.download_button("Download all as ZIP", data=zip_buffer.getvalue(),
                             file_name="markdown_files.zip", mime="application/zip")

    st.info("Tip: paste the Markdown into ChatGPT, Gemini or NotebookLM and ask your questions.")
