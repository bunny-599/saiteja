from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfgen import canvas
import io
import datetime
from typing import Dict, Any

class NumberedCanvas(canvas.Canvas):
    """Canvas subclass to dynamically calculate total page count and add headers/footers."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count):
        # Do not draw header/footer on cover page
        if self._pageNumber == 1:
            return
            
        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#718096"))
        
        # Header
        self.drawString(54, 750, "Sky-Scrapper Competitor Intelligence Report")
        self.setStrokeColor(colors.HexColor("#E2E8F0"))
        self.setLineWidth(0.5)
        self.line(54, 742, letter[0]-54, 742)
        
        # Footer
        page_text = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(letter[0]-54, 36, page_text)
        self.drawString(54, 36, f"Generated on {datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}")
        self.line(54, 48, letter[0]-54, 48)
        
        self.restoreState()

def create_report_pdf(report_data: Dict[str, Any]) -> io.BytesIO:
    """Generates a ReportLab PDF and returns it as a BytesIO stream."""
    buffer = io.BytesIO()
    
    # Page setup - 0.75 in margins
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54
    )
    
    styles = getSampleStyleSheet()
    
    # Custom Palette
    PRIMARY = colors.HexColor("#1A365D")   # Dark Navy
    SECONDARY = colors.HexColor("#2B6CB0") # Slate Blue
    ACCENT = colors.HexColor("#319795")    # Teal
    TEXT_COLOR = colors.HexColor("#2D3748")# Charcoal
    BG_LIGHT = colors.HexColor("#F7FAFC")  # Off-white
    
    # Custom Styles
    title_style = ParagraphStyle(
        'CoverTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=32,
        leading=38,
        textColor=PRIMARY,
        spaceAfter=15
    )
    
    subtitle_style = ParagraphStyle(
        'CoverSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=16,
        leading=22,
        textColor=SECONDARY,
        spaceAfter=30
    )
    
    meta_style = ParagraphStyle(
        'CoverMeta',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        textColor=TEXT_COLOR
    )
    
    h1_style = ParagraphStyle(
        'SectionH1',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=24,
        textColor=PRIMARY,
        spaceBefore=15,
        spaceAfter=10,
        keepWithNext=True
    )
    
    h2_style = ParagraphStyle(
        'SectionH2',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=14,
        leading=18,
        textColor=SECONDARY,
        spaceBefore=12,
        spaceAfter=6,
        keepWithNext=True
    )
    
    body_style = ParagraphStyle(
        'CustomBody',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        textColor=TEXT_COLOR,
        spaceAfter=8
    )
    
    bullet_style = ParagraphStyle(
        'CustomBullet',
        parent=body_style,
        leftIndent=15,
        firstLineIndent=-10,
        spaceAfter=4
    )
    
    table_header_style = ParagraphStyle(
        'TableHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9,
        leading=11,
        textColor=colors.white
    )
    
    table_cell_style = ParagraphStyle(
        'TableCell',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=12,
        textColor=TEXT_COLOR
    )

    story = []
    
    # ------------------ COVER PAGE ------------------
    story.append(Spacer(1, 150))
    story.append(Paragraph("SKY-SCRAPPER", title_style))
    story.append(Paragraph("Competitor Intelligence & Market Report", subtitle_style))
    story.append(Spacer(1, 20))
    
    # Cover Divider Line
    line_table = Table([[""]], colWidths=[letter[0]-108])
    line_table.setStyle(TableStyle([
        ('LINEBELOW', (0,0), (-1,-1), 3, ACCENT),
        ('BOTTOMPADDING', (0,0), (-1,-1), 0),
        ('TOPPADDING', (0,0), (-1,-1), 0),
    ]))
    story.append(line_table)
    story.append(Spacer(1, 40))
    
    target_co = report_data.get("target_company", {})
    metadata = report_data.get("metadata", {})
    
    story.append(Paragraph(f"<b>Target Company:</b> {target_co.get('name')}", meta_style))
    story.append(Paragraph(f"<b>Industry Focus:</b> {metadata.get('industry')}", meta_style))
    story.append(Paragraph(f"<b>Analysis Scope:</b> {metadata.get('depth', 'standard').capitalize()} Depth", meta_style))
    story.append(Paragraph(f"<b>Generated On:</b> {datetime.datetime.utcnow().strftime('%Y-%m-%d')}", meta_style))
    story.append(PageBreak())
    
    # ------------------ EXECUTIVE SUMMARY ------------------
    recommendations = report_data.get("recommendations", {})
    if recommendations and recommendations.get("executive_summary"):
        story.append(Paragraph("Executive Summary", h1_style))
        story.append(Paragraph(recommendations.get("executive_summary", "No summary available."), body_style))
        story.append(Spacer(1, 15))
        
    # ------------------ COMPETITOR LANDSCAPE TABLE ------------------
    story.append(Paragraph("Competitor Landscape", h1_style))
    story.append(Paragraph("Key metrics and parameters of identified competitors in comparison with the target company.", body_style))
    
    # Setup Table Data
    table_data = [[
        Paragraph("Company", table_header_style),
        Paragraph("Revenue Est.", table_header_style),
        Paragraph("Employees", table_header_style),
        Paragraph("Growth Rate", table_header_style),
        Paragraph("HQ Location", table_header_style),
        Paragraph("Market Tier", table_header_style)
    ]]
    
    # Target Row
    t_metrics = target_co.get("metrics", {})
    table_data.append([
        Paragraph(f"<b>{target_co.get('name')} (Target)</b>", table_cell_style),
        Paragraph(t_metrics.get("revenue", "N/A"), table_cell_style),
        Paragraph(str(t_metrics.get("employees", "N/A")), table_cell_style),
        Paragraph(t_metrics.get("growth_percentage", "N/A"), table_cell_style),
        Paragraph(t_metrics.get("hq_location", "N/A"), table_cell_style),
        Paragraph("N/A", table_cell_style)
    ])
    
    # Competitor Rows
    comp_data = report_data.get("competitor_data", [])
    comp_profiles = report_data.get("competitor_profiles", [])
    
    # Map competitor name to profile market share tier
    tier_map = {}
    if comp_profiles:
        for p in comp_profiles:
            tier_map[p.get("company")] = p.get("estimated_market_share_tier", "niche")
        
    for cd in comp_data:
        c_metrics = cd.get("metrics", {})
        c_tier = tier_map.get(cd.get("name"), "niche").capitalize()
        table_data.append([
            Paragraph(cd.get("name"), table_cell_style),
            Paragraph(c_metrics.get("revenue", "N/A"), table_cell_style),
            Paragraph(str(c_metrics.get("employees", "N/A")), table_cell_style),
            Paragraph(c_metrics.get("growth_percentage", "N/A"), table_cell_style),
            Paragraph(c_metrics.get("hq_location", "N/A"), table_cell_style),
            Paragraph(c_tier, table_cell_style)
        ])
        
    comp_table = Table(table_data, colWidths=[110, 80, 75, 75, 110, 54])
    comp_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), PRIMARY),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('BOTTOMPADDING', (0,0), (-1,0), 6),
        ('TOPPADDING', (0,0), (-1,0), 6),
        ('BACKGROUND', (0,1), (-1,1), BG_LIGHT), # highlight target
        ('BOTTOMPADDING', (0,1), (-1,-1), 5),
        ('TOPPADDING', (0,1), (-1,-1), 5),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E0")),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    
    story.append(comp_table)
    story.append(PageBreak())
    
    # ------------------ SWOT MATRIX (2x2 Grid) ------------------
    swot = report_data.get("swot", {})
    if swot and (swot.get("strengths") or swot.get("weaknesses") or swot.get("opportunities") or swot.get("threats")):
        story.append(Paragraph("SWOT Matrix", h1_style))
        story.append(Paragraph("Strategic overview of strengths, weaknesses, opportunities, and threats for the target company with associated data evidence.", body_style))
        story.append(Spacer(1, 10))
        
        # Format bullets for SWOT quadrants
        def get_swot_bullets(items):
            bullets = []
            for it in items[:4]: # Cap at top 4
                bullets.append(f"• <b>{it.get('point')}:</b> {it.get('evidence')[:120]}...")
            return "<br/><br/>".join(bullets) if bullets else "No data."

        s_text = Paragraph(f"<b>STRENGTHS</b><br/><br/>{get_swot_bullets(swot.get('strengths', []))}", table_cell_style)
        w_text = Paragraph(f"<b>WEAKNESSES</b><br/><br/>{get_swot_bullets(swot.get('weaknesses', []))}", table_cell_style)
        o_text = Paragraph(f"<b>OPPORTUNITIES</b><br/><br/>{get_swot_bullets(swot.get('opportunities', []))}", table_cell_style)
        t_text = Paragraph(f"<b>THREATS</b><br/><br/>{get_swot_bullets(swot.get('threats', []))}", table_cell_style)
        
        swot_table_data = [
            [s_text, w_text],
            [o_text, t_text]
        ]
        
        swot_table = Table(swot_table_data, colWidths=[252, 252])
        swot_table.setStyle(TableStyle([
            ('ALIGN', (0,0), (-1,-1), 'LEFT'),
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('TOPPADDING', (0,0), (-1,-1), 10),
            ('BOTTOMPADDING', (0,0), (-1,-1), 10),
            ('LEFTPADDING', (0,0), (-1,-1), 10),
            ('RIGHTPADDING', (0,0), (-1,-1), 10),
            
            # Quadrant Colors
            ('BACKGROUND', (0,0), (0,0), colors.HexColor("#E6FFFA")), # Light Teal/Green for Strengths
            ('BACKGROUND', (1,0), (1,0), colors.HexColor("#FFFAF0")), # Light Orange/Yellow for Weaknesses
            ('BACKGROUND', (0,1), (0,1), colors.HexColor("#EBF8FF")), # Light Blue for Opportunities
            ('BACKGROUND', (1,1), (1,1), colors.HexColor("#FFF5F5")), # Light Red/Pink for Threats
            
            ('GRID', (0,0), (-1,-1), 1.5, colors.HexColor("#E2E8F0")),
        ]))
        
        story.append(swot_table)
        story.append(PageBreak())
        
    # ------------------ CUSTOMER SENTIMENT ------------------
    sentiment = report_data.get("sentiment", {})
    if sentiment and sentiment.get("overall_score") is not None and sentiment.get("top_praise_themes"):
        story.append(Paragraph("Customer Sentiment Analysis", h1_style))
        
        score_p = f"<b>Overall Customer Satisfaction Score:</b> {sentiment.get('overall_score', 0)}/10"
        nps_p = f"<b>NPS Estimate:</b> {sentiment.get('nps_estimate', 0)}"
        story.append(Paragraph(f"{score_p} &nbsp;|&nbsp; {nps_p}", h2_style))
        
        breakdown = sentiment.get("sentiment_breakdown", {})
        breakdown_text = f"Positive: {breakdown.get('positive', 0)}% &nbsp;&nbsp; Neutral: {breakdown.get('neutral', 0)}% &nbsp;&nbsp; Negative: {breakdown.get('negative', 0)}%"
        story.append(Paragraph(f"<b>Sentiment Breakdown:</b> {breakdown_text}", body_style))
        story.append(Spacer(1, 5))
        
        story.append(Paragraph("Top Praise Themes", h2_style))
        for theme in sentiment.get("top_praise_themes", []):
            story.append(Paragraph(f"• {theme}", bullet_style))
            
        story.append(Paragraph("Top Complaint Themes", h2_style))
        for theme in sentiment.get("top_complaint_themes", []):
            story.append(Paragraph(f"• {theme}", bullet_style))
            
        story.append(Paragraph("Urgent Customer Issues", h2_style))
        for issue in sentiment.get("urgent_issues", []):
            story.append(Paragraph(f"• <font color='red'><b>{issue}</b></font>", bullet_style))
            
        story.append(PageBreak())
        
    # ------------------ AD INTELLIGENCE ------------------
    ads_analysis = report_data.get("ads_analysis", {})
    if ads_analysis and ads_analysis.get("dominant_messaging_themes"):
        story.append(Paragraph("Advertising & Messaging Intelligence", h1_style))
        
        story.append(Paragraph("Dominant Advertising Themes", h2_style))
        for theme in ads_analysis.get("dominant_messaging_themes", []):
            story.append(Paragraph(f"• {theme}", bullet_style))
            
        story.append(Paragraph("Ad Content Gaps In Market", h2_style))
        for gap in ads_analysis.get("content_gaps", []):
            story.append(Paragraph(f"• {gap}", bullet_style))
            
        story.append(Paragraph("Recommended Messaging Angles", h2_style))
        for angle in ads_analysis.get("recommended_angles", []):
            story.append(Paragraph(f"• {angle}", bullet_style))
            
        story.append(PageBreak())
        
    # ------------------ MARKET OPPORTUNITIES ------------------
    opportunities = report_data.get("market_opportunity", {})
    if opportunities and opportunities.get("top_opportunities"):
        story.append(Paragraph("Market Opportunities", h1_style))
        
        for idx, opp in enumerate(opportunities.get("top_opportunities", [])):
            op_title = f"Opportunity {idx+1}: {opp.get('title')} (Urgency: {opp.get('urgency', 'medium').upper()})"
            story.append(Paragraph(op_title, h2_style))
            story.append(Paragraph(opp.get("rationale", ""), body_style))
            
        story.append(PageBreak())
        
    # ------------------ STRATEGIC RECOMMENDATIONS ------------------
    if recommendations and recommendations.get("weekly_priorities"):
        story.append(Paragraph("Strategic Recommendations", h1_style))
        
        story.append(Paragraph("Weekly Priorities (Quick Wins)", h2_style))
        for priority in recommendations.get("weekly_priorities", []):
            story.append(Paragraph(f"• {priority}", bullet_style))
            
        story.append(Paragraph("Monthly Goals (Mid-Term)", h2_style))
        for goal in recommendations.get("monthly_goals", []):
            story.append(Paragraph(f"• {goal}", bullet_style))
            
        story.append(Paragraph("Marketing Initiatives", h2_style))
        for rec in recommendations.get("marketing_recommendations", []):
            story.append(Paragraph(f"• {rec}", bullet_style))
            
        story.append(Paragraph("Product Strategy", h2_style))
        for rec in recommendations.get("product_recommendations", []):
            story.append(Paragraph(f"• {rec}", bullet_style))
            
        story.append(Paragraph("Competitive Defenses & Responses", h2_style))
        for resp in recommendations.get("competitive_responses", []):
            story.append(Paragraph(f"• <b>Threat:</b> {resp.get('threat')}<br/>  <b>Response:</b> {resp.get('response')}", bullet_style))
            story.append(Spacer(1, 4))
        
    # Build Document
    doc.build(story, canvasmaker=NumberedCanvas)
    buffer.seek(0)
    return buffer
