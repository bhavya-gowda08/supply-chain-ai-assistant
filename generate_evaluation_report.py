
import os
import pandas as pd

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    Image,
    PageBreak
)

# -----------------------------------------
# 1. Load actual evaluation results
# -----------------------------------------

csv_file = "advanced_evaluation_v2_results.csv"

if not os.path.exists(csv_file):
    raise FileNotFoundError(
        "Evaluation results CSV not found. Run advanced_evaluation_v2.py first."
    )

df = pd.read_csv(csv_file)

# -----------------------------------------
# 2. PDF configuration
# -----------------------------------------

output_file = "RAG_Evaluation_Report.pdf"

pdf = SimpleDocTemplate(
    output_file,
    pagesize=A4,
    rightMargin=45,
    leftMargin=45,
    topMargin=45,
    bottomMargin=45
)

styles = getSampleStyleSheet()

title_style = ParagraphStyle(
    "ReportTitle",
    parent=styles["Title"],
    fontSize=21,
    alignment=TA_CENTER,
    spaceAfter=18
)

heading_style = ParagraphStyle(
    "SectionHeading",
    parent=styles["Heading2"],
    fontSize=14,
    textColor=colors.darkblue,
    spaceBefore=14,
    spaceAfter=8
)

body_style = ParagraphStyle(
    "ReportBody",
    parent=styles["BodyText"],
    fontSize=10,
    leading=15,
    spaceAfter=8
)

story = []

# -----------------------------------------
# 3. Title page
# -----------------------------------------

story.append(Spacer(1, 1.2 * inch))

story.append(
    Paragraph(
        "ADVANCED RAG EVALUATION REPORT",
        title_style
    )
)

story.append(
    Paragraph(
        "Enterprise AI Demand Planning &amp; Supply Chain Intelligence Assistant",
        ParagraphStyle(
            "Subtitle",
            parent=styles["Normal"],
            fontSize=13,
            alignment=TA_CENTER,
            leading=18
        )
    )
)

story.append(Spacer(1, 0.5 * inch))

story.append(
    Paragraph(
        "Embedding Model Performance Comparison",
        ParagraphStyle(
            "Subtitle2",
            parent=styles["Normal"],
            fontSize=12,
            alignment=TA_CENTER
        )
    )
)

story.append(Spacer(1, 2 * inch))

story.append(
    Paragraph(
        "Evaluation Dataset: 25 Questions<br/>"
        "Embedding Models: MiniLM and MPNet<br/>"
        "Vector Database: ChromaDB<br/>"
        "Evaluation Type: Document-level Retrieval",
        ParagraphStyle(
            "CoverInfo",
            parent=styles["Normal"],
            alignment=TA_CENTER,
            leading=22
        )
    )
)

story.append(PageBreak())

# -----------------------------------------
# 4. Introduction
# -----------------------------------------

story.append(
    Paragraph("1. Introduction", heading_style)
)

story.append(
    Paragraph(
        "This evaluation compares two sentence embedding models "
        "for document retrieval in an Enterprise AI Demand Planning "
        "and Supply Chain Intelligence Assistant. The objective is "
        "to examine their retrieval quality and response speed using "
        "supply-chain-related documents.",
        body_style
    )
)

# -----------------------------------------
# 5. Evaluation objectives
# -----------------------------------------

story.append(
    Paragraph("2. Evaluation Objectives", heading_style)
)

objectives = [
    "Compare all-MiniLM-L6-v2 and all-mpnet-base-v2.",
    "Evaluate document retrieval using 25 questions.",
    "Measure Precision@3, Recall@3 and Mean Reciprocal Rank.",
    "Compare average retrieval time.",
    "Identify a suitable embedding model for further testing."
]

for objective in objectives:
    story.append(
        Paragraph("• " + objective, body_style)
    )

# -----------------------------------------
# 6. Dataset
# -----------------------------------------

story.append(
    Paragraph("3. Evaluation Dataset", heading_style)
)

story.append(
    Paragraph(
        "The evaluation uses four source files: "
        "supply_chain_policy.pdf, test_document.txt, "
        "test_inventory.csv and test_inventory.xlsx. "
        "The dataset contains 25 manually prepared questions "
        "covering inventory management, reorder policies, "
        "warehouse management, suppliers and demand planning.",
        body_style
    )
)

story.append(
    Paragraph(
        "The CSV and Excel files contain duplicate inventory records. "
        "Both were labelled relevant where appropriate. "
        "The relevance labels are preliminary manual judgements.",
        body_style
    )
)

# -----------------------------------------
# 7. Evaluation methodology
# -----------------------------------------

story.append(
    Paragraph("4. Evaluation Methodology", heading_style)
)

methodology = [
    "<b>Precision@3:</b> Proportion of the top three retrieved "
    "documents that are labelled relevant.",
    "<b>Recall@3:</b> Proportion of all labelled relevant documents "
    "retrieved in the top three results.",
    "<b>MRR:</b> Average reciprocal rank of the first relevant "
    "retrieved document.",
    "<b>Retrieval Time:</b> Average time taken for a retrieval query."
]

for item in methodology:
    story.append(Paragraph("• " + item, body_style))

# -----------------------------------------
# 8. Results table
# -----------------------------------------

story.append(
    Paragraph("5. Experimental Results", heading_style)
)

table_data = [
    [
        "Model",
        "Precision@3",
        "Recall@3",
        "MRR",
        "Time (sec)"
    ]
]

for _, row in df.iterrows():
    table_data.append([
        row["Model"],
        f'{row["Precision@3"]:.4f}',
        f'{row["Recall@3"]:.4f}',
        f'{row["MRR"]:.4f}',
        f'{row["Average Retrieval Time (seconds)"]:.6f}'
    ])

results_table = Table(
    table_data,
    colWidths=[125, 75, 70, 60, 75]
)

results_table.setStyle(
    TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.darkblue),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("ALIGN", (1, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 9),
        ("TOPPADDING", (0, 0), (-1, -1), 9)
    ])
)

story.append(results_table)

# -----------------------------------------
# 9. Charts
# -----------------------------------------

story.append(
    Paragraph("6. Performance Comparison Charts", heading_style)
)

chart_files = [
    "precision_3_v2.png",
    "recall_3_v2.png",
    "mrr_v2.png",
    "retrieval_time_v2.png"
]

for chart in chart_files:

    if os.path.exists(chart):

        story.append(Spacer(1, 10))

        story.append(
            Image(
                chart,
                width=6 * inch,
                height=3.5 * inch
            )
        )

    else:
        story.append(
            Paragraph(
                f"Chart not found: {chart}",
                body_style
            )
        )

# -----------------------------------------
# 10. Observations
# -----------------------------------------

story.append(
    Paragraph("7. Key Observations", heading_style)
)

observations = [
    "MPNet achieved Precision@3 of 0.6000, compared with "
    "0.5733 for MiniLM.",
    "MPNet achieved Recall@3 of 0.9733, compared with "
    "0.9067 for MiniLM.",
    "MiniLM achieved a slightly higher MRR of 0.9400, "
    "compared with 0.9333 for MPNet.",
    "MPNet recorded an average retrieval time of 0.004965 seconds, "
    "while MiniLM recorded 0.007777 seconds."
]

for observation in observations:
    story.append(
        Paragraph("• " + observation, body_style)
    )

# -----------------------------------------
# 11. Conclusion
# -----------------------------------------

story.append(
    Paragraph("8. Conclusion", heading_style)
)

story.append(
    Paragraph(
        "In this preliminary experiment, all-mpnet-base-v2 achieved "
        "higher Precision@3 and Recall@3 and a lower measured retrieval "
        "time. all-MiniLM-L6-v2 achieved a slightly higher MRR. "
        "MPNet is therefore a promising candidate for further testing. "
        "However, the experiment uses only four whole documents, "
        "including duplicate inventory records in CSV and Excel format. "
        "The findings should not be treated as a definitive production "
        "benchmark. Further evaluation using independent documents, "
        "verified relevance labels, document chunking and repeated "
        "measurements is required.",
        body_style
    )
)

# -----------------------------------------
# 12. Limitations and future work
# -----------------------------------------

story.append(
    Paragraph("9. Limitations and Future Improvements", heading_style)
)

limitations = [
    "The evaluation uses only four source documents.",
    "CSV and Excel inventory data are duplicates.",
    "Relevance labels require further independent validation.",
    "Retrieval measurements should be repeated across multiple runs.",
    "Future testing should evaluate chunk-level hybrid retrieval "
    "and reranking."
]

for item in limitations:
    story.append(
        Paragraph("• " + item, body_style)
    )

# -----------------------------------------
# 13. Generate PDF
# -----------------------------------------

pdf.build(story)

print("\n===================================")
print("PDF REPORT GENERATED SUCCESSFULLY!")
print("===================================")
print("File:", output_file)
