# MarkItDown Converter

A simple web app that turns PDF, Word, PowerPoint and Excel files into clean Markdown that any AI can read.

Upload one or more files, click **Convert to Markdown**, then preview, copy or download the result. You can download each file as `.md`, all files as one combined file, or all files as a ZIP.

Supported files: PDF, DOCX, PPTX, XLSX, XLS, CSV, HTML, HTM, TXT, JSON, XML. Maximum 10 MB per file.

## Files in this repo

- `app.py`: the app
- `requirements.txt`: the Python packages the app needs
- `README.md`: this file

Before you deploy, open `app.py` and change `APP_OWNER = "Your Name"` to your own name.

## Deploy free on Streamlit Community Cloud

1. Put the three files in a public GitHub repository (branch `main`).
2. Go to https://share.streamlit.io and sign in with GitHub.
3. Click **Create app**, then choose to deploy from a GitHub repository.
4. Pick your repository, branch `main`, and main file `app.py`.
5. Open **Advanced settings** and choose the Python version (3.12 or 3.13 both work).
6. Click **Deploy**. The first build takes a few minutes. You then get a public link to share.

## Run it on your own computer

```
pip install -r requirements.txt
streamlit run app.py
```

The app opens in your browser at http://localhost:8501

## Privacy

The app is public once deployed. Do not upload confidential or personal files. Files are processed in memory and are not saved by the app.

## Credits

- MarkItDown by Microsoft, MIT licence: https://github.com/microsoft/markitdown
- Streamlit: https://streamlit.io
- Project 5 of the GenAI and Agentic AI programme by CA Aashish Sachdev
