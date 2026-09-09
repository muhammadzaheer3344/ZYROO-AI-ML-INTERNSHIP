# ðŸ¤– AI/ML Internship @ ZyroInterns

> **Official Repository for Internship Work & Projects**

![Status: Active](https://img.shields.io/badge/Status-Active-brightgreen)
![Offer Code](https://img.shields.io/badge/Offer%20Code-ZYRO--OF--2026--843733-blue)
![Role](https://img.shields.io/badge/Role-AI%2FML%20Intern-orange)
![Year](https://img.shields.io/badge/Year-2026-lightgrey)

---

## ðŸ“Œ About This Repository

This repository serves as a centralized portfolio and documentation hub for my **AI/ML Internship** at **ZyroInterns**. 
Here, I will store all my project work, assignments, research notes, and code implementations developed throughout this internship journey.

---

## ðŸ“„ Internship Offer Details

| Attribute | Information |
| :--- | :--- |
| **Company** | ZyroInterns (via ZYR0) |
| **Position** | AI/ML Intern |
| **Offer Code** | `ZYRO-OF-2026-843733` |
| **Offer Date** | August 11, 2026 |
| **Expiration Date** | August 26, 2026 |
| **Verification** | [Verify Credential](https://zyroo.org/verify?type=offer&id=ZYRO-OF-2026-843733) |

> ðŸ”— **Official Links**
> - Student Dashboard: [https://zyroo.org/student/offer-letters](https://zyroo.org/student/offer-letters)
> - Career Hub: [https://zyroo.org/careers](https://zyroo.org/careers)

---

## Week 1 Projects

### AI Document Intelligence and Workflow Platform

The Week 1 Task 1 application is available here:

- [Open project folder](WEEK%201%20TASK%201%20AI%20Document%20Intelligence%20and%20Workflow%20Platform/)
- [Project README](WEEK%201%20TASK%201%20AI%20Document%20Intelligence%20and%20Workflow%20Platform/README.md)
- [Streamlit application](WEEK%201%20TASK%201%20AI%20Document%20Intelligence%20and%20Workflow%20Platform/app.py)

The project includes the Streamlit web interface and an optional FastAPI server for document upload, OCR, text extraction, classification, and information extraction.

### Live Links

- [GitHub repository](https://github.com/muhammadzaheer3344/ZYROO-AI-ML-INTERNSHIP)
- **Deployed Streamlit app:** https://zyroo-ai-ml-internship-gbsrtuhnqx9yjikwjzcwza.streamlit.app

---

## Streamlit Community Cloud Deployment

The repository keeps the deployment files at the root so Streamlit Community Cloud can find them reliably:

- `requirements.txt` contains the Python dependencies required by the Streamlit deployment.
- `packages.txt` installs the Linux Tesseract OCR system packages.
- `.streamlit/config.toml` contains the Streamlit theme configuration.
- `streamlit_app.py` is the root deployment entry point and loads the existing app.

In Streamlit Community Cloud, create or edit the app with:

```text
Repository: muhammadzaheer3344/ZYROO-AI-ML-INTERNSHIP
Branch: main
Main file path: streamlit_app.py
```

Cloud uses the root-level `requirements.txt` and `packages.txt`. FastAPI is an optional local service and is not installed by the Streamlit Cloud build.

---

## ðŸ—‚ Repository Structure

The repository is organized to track my progress and deliverables effectively:

```plaintext
ðŸ“¦ ai-ml-internship-zyrointerns
â”œâ”€â”€ ðŸ“„ requirements.txt       # Root Cloud dependencies
â”œâ”€â”€ ðŸ“„ packages.txt            # Tesseract OCR system dependencies
â”œâ”€â”€ ðŸ“„ streamlit_app.py       # Root Cloud entry point
â”œâ”€â”€ ðŸ“‚ .streamlit/
â”‚   â””â”€â”€ config.toml
â”œâ”€â”€ ðŸ“‚ week-1/                # Environment setup
â”œâ”€â”€ ðŸ“‚ WEEK 1 TASK 1 AI Document Intelligence and Workflow Platform/
â”œâ”€â”€ ðŸ“‚ week-2/
â”œâ”€â”€ ðŸ“‚ week-3/
â”œâ”€â”€ ðŸ“‚ week-4/
.
.
.
â””â”€â”€ ðŸ“„ README.md                # This file

