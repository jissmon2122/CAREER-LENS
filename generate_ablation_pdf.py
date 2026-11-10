"""
Script to generate a publication-quality PDF report for the CareerLens Salary Prediction Ablation Study.
Uses ReportLab to produce formatted typography, headers, metric tables, and visual callouts.
"""

import os
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    HRFlowable,
    KeepTogether
)

def generate_ablation_pdf(output_path: str):
    doc = SimpleDocTemplate(
        output_path,
        pagesize=letter,
        rightMargin=45,
        leftMargin=45,
        topMargin=45,
        bottomMargin=45
    )

    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=24,
        textColor=colors.HexColor('#111827'),
        spaceAfter=6
    )

    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=15,
        textColor=colors.HexColor('#4F46E5'),
        spaceAfter=14
    )

    meta_style = ParagraphStyle(
        'MetaStyle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=13,
        textColor=colors.HexColor('#4B5563'),
        spaceAfter=14
    )

    h2_style = ParagraphStyle(
        'SectionHeading',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=13,
        leading=17,
        textColor=colors.HexColor('#1E293B'),
        spaceBefore=14,
        spaceAfter=8
    )

    body_style = ParagraphStyle(
        'BodyDark',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=13.5,
        textColor=colors.HexColor('#334155'),
        spaceAfter=8
    )

    callout_style = ParagraphStyle(
        'CalloutText',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=8.5,
        leading=12.5,
        textColor=colors.HexColor('#1E3A8A')
    )

    th_style = ParagraphStyle(
        'TableHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8,
        leading=11,
        textColor=colors.white,
        alignment=1 # Center
    )

    td_style = ParagraphStyle(
        'TableCell',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8,
        leading=11,
        textColor=colors.HexColor('#1E293B'),
        alignment=0 # Left
    )

    td_center_style = ParagraphStyle(
        'TableCellCenter',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8,
        leading=11,
        textColor=colors.HexColor('#1E293B'),
        alignment=1 # Center
    )

    story = []

    # Title & Header
    story.append(Paragraph("CareerLens — Salary Prediction Engine", title_style))
    story.append(Paragraph("COMPREHENSIVE EMPIRICAL ABLATION STUDY REPORT", subtitle_style))
    story.append(Paragraph(
        "<b>Platform:</b> CareerLens (career-intelligence-platform) &nbsp;|&nbsp; "
        "<b>Model:</b> RandomForestRegressor + Quantile Calibrator<br/>"
        "<b>Dataset:</b> 7,680 stratified multi-profession profiles &nbsp;|&nbsp; "
        "<b>Split:</b> 80% Train (6,144) / 20% Held-Out Test (1,536) &nbsp;|&nbsp; "
        "<b>Status:</b> Evaluated on Test Split",
        meta_style
    ))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#4F46E5'), spaceAfter=12))

    # Executive Summary
    story.append(Paragraph("1. Executive Summary", h2_style))
    story.append(Paragraph(
        "To rigorously quantify the individual contribution of each algorithmic module, feature vector dimension, "
        "and architectural mechanism in the CareerLens compensation engine, we conducted a systematic two-phase "
        "ablation study on a strictly held-out test split of <b>1,536 unseen profiles</b>. "
        "Our experiments confirm that compensation estimation is fundamentally non-linear across global labor markets, "
        "causing linear models to collapse (MAPE &gt; 61%), while domain isolation and geographic market conditioning "
        "form the indispensable bedrock of realistic salary predictions.",
        body_style
    ))

    # Architecture Ablation Section
    story.append(Paragraph("2. Model Architecture & Capacity Ablation", h2_style))
    story.append(Paragraph(
        "We compared the full production Random Forest (100 estimators, max depth 14) against constrained ensemble sizes, "
        "a single unpruned decision tree, shallow trees, and classic linear baselines (L2 Ridge and OLS).",
        body_style
    ))

    arch_data = [
        [
            Paragraph("Architecture / Model", th_style),
            Paragraph("Parameters", th_style),
            Paragraph("Test R²", th_style),
            Paragraph("MAPE (%)", th_style),
            Paragraph("Test MAE ($)", th_style),
            Paragraph("Test RMSE ($)", th_style),
            Paragraph("Outcome", th_style)
        ],
        [
            Paragraph("<b>Full Random Forest</b>", td_style),
            Paragraph("N=100, D=14", td_center_style),
            Paragraph("<b>0.9637</b>", td_center_style),
            Paragraph("<b>8.79%</b>", td_center_style),
            Paragraph("<b>$8,517.79</b>", td_center_style),
            Paragraph("<b>$13,810.04</b>", td_center_style),
            Paragraph("<b>Production Baseline</b>", td_style)
        ],
        [
            Paragraph("Random Forest (10 Trees)", td_style),
            Paragraph("N=10, D=14", td_center_style),
            Paragraph("0.9621", td_center_style),
            Paragraph("9.10%", td_center_style),
            Paragraph("$8,710.45", td_center_style),
            Paragraph("$14,105.78", td_center_style),
            Paragraph("Slight variance increase", td_style)
        ],
        [
            Paragraph("Single Decision Tree", td_style),
            Paragraph("N=1, D=14", td_center_style),
            Paragraph("0.9385", td_center_style),
            Paragraph("11.59%", td_center_style),
            Paragraph("$10,974.25", td_center_style),
            Paragraph("$17,961.79", td_center_style),
            Paragraph("+28.8% MAE error surge", td_style)
        ],
        [
            Paragraph("Shallow Random Forest", td_style),
            Paragraph("N=100, D=5", td_center_style),
            Paragraph("0.8918", td_center_style),
            Paragraph("17.50%", td_center_style),
            Paragraph("$15,882.48", td_center_style),
            Paragraph("$23,835.95", td_center_style),
            Paragraph("Severe underfitting", td_style)
        ],
        [
            Paragraph("Ridge Regression (L2)", td_style),
            Paragraph("alpha=1.0", td_center_style),
            Paragraph("0.3171", td_center_style),
            Paragraph("61.25%", td_center_style),
            Paragraph("$40,535.01", td_center_style),
            Paragraph("$59,873.39", td_center_style),
            Paragraph("Catastrophic linear failure", td_style)
        ],
        [
            Paragraph("Ordinary Least Squares (OLS)", td_style),
            Paragraph("Linear", td_center_style),
            Paragraph("0.3166", td_center_style),
            Paragraph("61.22%", td_center_style),
            Paragraph("$40,545.37", td_center_style),
            Paragraph("$59,896.54", td_center_style),
            Paragraph("Incapable of non-linear fit", td_style)
        ],
    ]

    t_arch = Table(arch_data, colWidths=[115, 65, 50, 50, 65, 65, 110])
    t_arch.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4F46E5')),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E1')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F8FAFC')]),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(t_arch)
    story.append(Spacer(1, 10))

    # Feature Ablation Section
    story.append(Paragraph("3. Feature Dimension Ablation (Leave-One-Out Importance)", h2_style))
    story.append(Paragraph(
        "Each input feature was systematically excluded from the model matrix, retraining under identical random seeds "
        "to directly measure accuracy degradation ($\Delta R^2$ and MAE expansion).",
        body_style
    ))

    feat_data = [
        [
            Paragraph("Ablated Dimension Dropped", th_style),
            Paragraph("Retrained R²", th_style),
            Paragraph("MAPE (%)", th_style),
            Paragraph("Retrained MAE ($)", th_style),
            Paragraph("Retrained RMSE ($)", th_style),
            Paragraph("Accuracy Loss", th_style),
            Paragraph("Criticality Level", th_style)
        ],
        [
            Paragraph("<b>None (Full 7 Dimensions)</b>", td_style),
            Paragraph("<b>0.9637</b>", td_center_style),
            Paragraph("<b>8.79%</b>", td_center_style),
            Paragraph("<b>$8,517.79</b>", td_center_style),
            Paragraph("<b>$13,810.04</b>", td_center_style),
            Paragraph("<b>0.00%</b>", td_center_style),
            Paragraph("<b>Optimal Fit</b>", td_style)
        ],
        [
            Paragraph("Without Education", td_style),
            Paragraph("0.9625", td_center_style),
            Paragraph("9.11%", td_center_style),
            Paragraph("$8,785.63", td_center_style),
            Paragraph("$14,027.54", td_center_style),
            Paragraph("-0.12%", td_center_style),
            Paragraph("Low / Fine-tuning", td_style)
        ],
        [
            Paragraph("Without Skills Premium", td_style),
            Paragraph("0.9596", td_center_style),
            Paragraph("9.25%", td_center_style),
            Paragraph("$9,040.18", td_center_style),
            Paragraph("$14,568.65", td_center_style),
            Paragraph("-0.41%", td_center_style),
            Paragraph("Moderate (Niche skills)", td_style)
        ],
        [
            Paragraph("Without Experience (Years)", td_style),
            Paragraph("0.9532", td_center_style),
            Paragraph("9.82%", td_center_style),
            Paragraph("$9,672.09", td_center_style),
            Paragraph("$15,669.08", td_center_style),
            Paragraph("-1.05%", td_center_style),
            Paragraph("Significant intra-band", td_style)
        ],
        [
            Paragraph("Without City Tier", td_style),
            Paragraph("0.9464", td_center_style),
            Paragraph("10.96%", td_center_style),
            Paragraph("$10,746.23", td_center_style),
            Paragraph("$16,777.90", td_center_style),
            Paragraph("-1.73%", td_center_style),
            Paragraph("High (Metro vs Regional)", td_style)
        ],
        [
            Paragraph("Without Seniority Level", td_style),
            Paragraph("0.9320", td_center_style),
            Paragraph("11.46%", td_center_style),
            Paragraph("$11,720.48", td_center_style),
            Paragraph("$18,900.11", td_center_style),
            Paragraph("-3.17%", td_center_style),
            Paragraph("Very High (Band bounds)", td_style)
        ],
        [
            Paragraph("<b>Without Domain Isolation</b>", td_style),
            Paragraph("<b>0.7066</b>", td_center_style),
            Paragraph("<b>30.90%</b>", td_center_style),
            Paragraph("<b>$26,731.43</b>", td_center_style),
            Paragraph("<b>$39,245.54</b>", td_center_style),
            Paragraph("<b>-25.71%</b>", td_center_style),
            Paragraph("<b>Critical (Trade Isolation)</b>", td_style)
        ],
        [
            Paragraph("<b>Without Country</b>", td_style),
            Paragraph("<b>0.4353</b>", td_center_style),
            Paragraph("<b>95.79%</b>", td_center_style),
            Paragraph("<b>$39,725.08</b>", td_center_style),
            Paragraph("<b>$54,444.57</b>", td_center_style),
            Paragraph("<b>-52.84%</b>", td_center_style),
            Paragraph("<b>Foundational (Macro economy)</b>", td_style)
        ],
        [
            Paragraph("Experience Only (Naive)", td_style),
            Paragraph("0.1595", td_center_style),
            Paragraph("111.46%", td_center_style),
            Paragraph("$46,857.70", td_center_style),
            Paragraph("$66,425.99", td_center_style),
            Paragraph("-80.42%", td_center_style),
            Paragraph("Completely inadequate", td_style)
        ]
    ]

    t_feat = Table(feat_data, colWidths=[120, 55, 50, 65, 65, 60, 105])
    t_feat.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1E293B')),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E1')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F8FAFC')]),
        ('TOPPADDING', (0, 0), (-1, -1), 3.5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3.5),
    ]))
    story.append(t_feat)
    story.append(Spacer(1, 10))

    # Analytical Insights Callout
    callout_data = [[
        Paragraph(
            "<b>Key Architectural Insights:</b><br/>"
            "• <b>The Critical Role of Domain Isolation:</b> Removing Domain causes MAE to surge from $8.5K to $26.7K (+214%), demonstrating that Universal Role Taxonomy domain mapping is essential to prevent trade professions (Electrician, Plumber) from receiving inflated tech compensation.<br/>"
            "• <b>Seniority vs. Experience:</b> Seniority level exerts 3x greater predictive leverage (-3.17% R²) than chronological experience years (-1.05% R²), as organizational tier dictates compensation brackets while years dictate positioning within the bracket.<br/>"
            "• <b>Non-Linear Dynamics:</b> Linear models (Ridge/OLS) fail catastrophically (R² ≈ 0.317, MAPE > 61%) proving the necessity of tree-based ensemble estimators.",
            callout_style
        )
    ]]
    t_callout = Table(callout_data, colWidths=[520])
    t_callout.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#EFF6FF')),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#BFDBFE')),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ('RIGHTPADDING', (0, 0), (-1, -1), 10),
    ]))
    story.append(KeepTogether(t_callout))

    doc.build(story)
    print(f"PDF successfully created at: {output_path}")

if __name__ == '__main__':
    target = os.path.abspath('CareerLens_Salary_Ablation_Study_Report.pdf')
    generate_ablation_pdf(target)
