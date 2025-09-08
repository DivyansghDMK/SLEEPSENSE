"""
PDF report generation for SleepSense Pro
"""

import os
from datetime import datetime
from pathlib import Path
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle, Image
from io import BytesIO
import matplotlib.pyplot as plt
from matplotlib.figure import Figure


class PDFGenerator:
    """Handles PDF report generation"""
    
    def __init__(self):
        self.width, self.height = A4
        # Branding colors for page-2 template styling
        self.blue_primary = colors.HexColor('#1F4EAD')
        self.blue_light = colors.HexColor('#e6eefc')
        self.gray_grid = colors.HexColor('#7a7a7a')

    def _draw_section_header(self, c, y, title, left_margin, usable_width):
        """Draw a filled blue section header bar and return new y."""
        bar_h = 0.9 * cm
        c.setFillColor(self.blue_primary)
        c.rect(left_margin, y - bar_h, usable_width, bar_h, stroke=0, fill=1)
        c.setFillColor(colors.white)
        c.setFont("Helvetica-Bold", 12)
        c.drawString(left_margin + 0.25*cm, y - 0.62*cm, title)
        c.setFillColor(colors.black)
        return y - (bar_h + 0.25*cm)

    def _blue_table_style(self, header_rows=1):
        """Return a TableStyle matching the blue header row template."""
        style = [
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,0), 9),
            ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            ('BACKGROUND', (0,0), (-1,0), self.blue_primary),
            ('FONTSIZE', (0,1), (-1,-1), 8),
            ('ALIGN', (1,0), (-1,-1), 'CENTER'),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('GRID', (0,0), (-1,-1), 0.5, self.gray_grid),
        ]
        return TableStyle(style)

    def _draw_table_fit(self, c, table, y, left_margin, usable_width, bottom_margin):
        """Draw table scaled to fit between y and bottom margin, preserving width.
        Returns the new y below the table with spacing.
        """
        spacing = 0.6 * cm
        # Try to fit with uniform scale s so final width == usable_width
        # We wrap with width usable_width/s so after scaling by s, it equals usable_width
        # Compute maximum scale from height available
        available_h = max(0.0, y - bottom_margin)
        if available_h <= 0:
            return bottom_margin
        # First try s=1.0, then compute needed s if doesn't fit
        s_candidates = [1.0]
        # A couple of fallback scales
        s_candidates += [0.95, 0.9, 0.85, 0.8, 0.75, 0.7]
        for s in s_candidates:
            tw, th = table.wrap(usable_width / s, self.height)
            if th * s <= available_h:
                c.saveState()
                c.translate(left_margin, y)
                c.scale(s, s)
                table.drawOn(c, 0, -th)
                c.restoreState()
                return y - th * s - spacing
        # Final attempt: compute exact scale to fit height
        tw, th = table.wrap(usable_width, self.height)
        s = min(0.68, available_h / th * 0.98)  # cap extreme downscaling
        if s <= 0:
            return bottom_margin
        tw, th = table.wrap(usable_width / s, self.height)
        c.saveState()
        c.translate(left_margin, y)
        c.scale(s, s)
        table.drawOn(c, 0, -th)
        c.restoreState()
        return y - th * s - spacing
    
    def generate_pdf_report(self, filename, analysis_results, signals):
        """Generates the full multi-page PDF report"""
        try:
            print("Starting PDF generation...")
            
            # Create PDF canvas
            print("Creating PDF canvas...")
            c = canvas.Canvas(filename, pagesize=A4)
            print(f"PDF canvas created. Size: {self.width}x{self.height}")

            # Draw each page
            print("Drawing page 1...")
            self.draw_page_one(c, analysis_results)
            c.showPage()
            
            print("Drawing page 2...")
            self.draw_page_two(c, analysis_results)
            c.showPage()
            
            print("Drawing page 3...")
            self.draw_page_three(c, analysis_results)
            c.showPage()
            
            print("Drawing page 4...")
            self.draw_page_four(c, analysis_results, signals)
            
            print("Saving PDF...")
            c.save()
            print("PDF generation completed successfully!")
            
        except Exception as e:
            print(f"Error in PDF generation: {e}")
            print(f"Error type: {type(e)}")
            import traceback
            traceback.print_exc()
            raise e
    
    def draw_page_one(self, c, res):
        """Draw the first page with patient information"""
        left_margin = 2 * cm
        usable_width = self.width - 4 * cm
        
        # Header section
        c.setFont("Helvetica-Bold", 18)
        c.drawString(left_margin, self.height - 2.5 * cm, "Sleep Study Report")
        c.setFont("Helvetica-Bold", 12)
        c.setFillColor(colors.red)
        c.drawString(left_margin, self.height - 3.2 * cm, "⚠️ MOCK DATA - FOR DEMONSTRATION PURPOSES ONLY")
        c.setFillColor(colors.black)
        c.setFont("Helvetica", 10)
        c.drawString(self.width - 6 * cm, self.height - 2.5 * cm, "Deckmount PVt LTD")

        # Patient Data section (blue bar)
        y = self.height - 4.0 * cm
        y = self._draw_section_header(c, y, "Patient Data", left_margin, usable_width)

        p_data = [
            ['Last Name:', 'Divyansh', 'Height:', '180cm'],
            ['First Name:', 'Srivastava', 'Weight:', '65kg'],
            ['Date of Birth:', res['recording_date'], 'BMI:', '20.1 kg/m²'],
            ['Patient ID:', res['patient_id'], 'Study Date:', res['recording_date']]
        ]
        p_table = Table(p_data, colWidths=[2.5*cm, 4.5*cm, 2*cm, 4.5*cm])
        p_table.setStyle(TableStyle([
            ('FONTNAME', (0,0), (-1,-1), 'Helvetica'),
            ('FONTSIZE', (0,0), (-1,-1), 10),
            ('GRID', (0,0), (-1,-1), 0.5, self.gray_grid),
            ('ALIGN', (0,0), (-1,-1), 'LEFT'),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ]))
        tw, th = p_table.wrap(usable_width, self.height)
        y -= th
        p_table.drawOn(c, left_margin, y)
        y -= 0.6 * cm

        # Section: Case History
        y = self._draw_section_header(c, y, "Case History", left_margin, usable_width)
        c.rect(left_margin, y - 2.5*cm, usable_width, 2.2*cm, stroke=1, fill=0)
        y -= 2.7 * cm

        # Section: Findings
        y = self._draw_section_header(c, y, "Findings", left_margin, usable_width)
        c.rect(left_margin, y - 2.5*cm, usable_width, 2.2*cm, stroke=1, fill=0)
        y -= 2.7 * cm

        # Section: Diagnosis
        y = self._draw_section_header(c, y, "Diagnosis", left_margin, usable_width)
        c.rect(left_margin, y - 2.5*cm, usable_width, 2.2*cm, stroke=1, fill=0)
        y -= 2.7 * cm

        # Section: Comments
        y = self._draw_section_header(c, y, "Comments", left_margin, usable_width)
        c.rect(left_margin, y - 2.5*cm, usable_width, 2.2*cm, stroke=1, fill=0)

    def draw_page_two(self, c, res):
        """Draw the second page with respiratory analysis"""
        left_margin = 2 * cm
        usable_width = self.width - 4 * cm
        
        # Page Title with Mock Data Warning
        y = self.height - 2.5 * cm
        c.setFont("Helvetica-Bold", 18)
        c.drawString(left_margin, y, "Sleep Study Analysis Results")
        y -= 0.7 * cm
        c.setFont("Helvetica-Bold", 12)
        c.setFillColor(colors.red)
        c.drawString(left_margin, y, "⚠️ MOCK DATA - FOR DEMONSTRATION PURPOSES ONLY")
        c.setFillColor(colors.black)
        
        # Respiratory Analysis Section header bar
        y -= 0.6 * cm
        y = self._draw_section_header(c, y, "Respiratory Analysis", left_margin, usable_width)
        
        # Table 1: Respiratory Events by Sleep Stage
        y -= 1.0 * cm
        y = self._draw_section_header(c, y + 0.35*cm, "Respiratory Events by Sleep Stage", left_margin, usable_width)
        
        resp_stage_data = [
            ['Number (Index)', 'REM', 'Non-REM', 'Sleep'],
            ['Obstructive', f"{res['obstructive_apneas']} ({res['ahi']*0.75:.1f})", f"{res['obstructive_apneas']//2} ({res['ahi']*0.75*0.3:.1f})", f"{res['obstructive_apneas']} ({res['ahi']*0.75:.1f})"],
            ['Mixed', '-', '-', '-'],
            ['Central', f"{res['central_apneas']} ({res['ahi']*0.25:.1f})", f"{res['central_apneas']//2} ({res['ahi']*0.25*0.3:.1f})", f"{res['central_apneas']} ({res['ahi']*0.25:.1f})"],
            ['Undef A.', '-', '-', '-'],
            ['Apnea (Index)', '-', '-', f"{res['total_apneas']} ({res['ahi']:.1f})"],
            ['Hypopnea (Index)', '-', '-', f"{res['hypopneas']} ({res['hypopneas']/res['tib_hours']:.1f})"],
            ['AHI / RDI [/h]', f"{res['rem_ahi']:.1f} / {res['rem_ahi']:.1f}", f"{res['nrem_ahi']:.1f} / {res['nrem_ahi']:.1f}", f"{res['ahi']:.1f} / {res['rdi']:.1f}"],
            ['Flow Limitations (Index)', '-', '-', f"{res['flow_limitations']/res['tib_hours']:.1f}"],
            ['Total Apn.', f"{res['total_apneas']//3}", f"{res['total_apneas']*2//3}", f"{res['total_apneas']} ({res['ahi']:.1f})"],
            ['Hypopnea', f"{res['hypopneas']//3}", f"{res['hypopneas']*2//3}", f"{res['hypopneas']} ({res['hypopneas']/res['tib_hours']:.1f})"],
            ['A+H', f"{(res['total_apneas']+res['hypopneas'])//3}", f"{(res['total_apneas']+res['hypopneas'])*2//3}", f"{res['total_apneas']+res['hypopneas']} ({res['ahi']:.1f})"],
            ['Max. Apnea Duration (s)', f"{res['max_apnea_duration']*0.8:.0f}", f"{res['max_apnea_duration']*1.2:.0f}", f"{res['max_apnea_duration']:.0f}"],
            ['Max. Hypopnoea Duration (s)', f"{res['max_hypopnea_duration']*0.8:.0f}", f"{res['max_hypopnea_duration']*1.2:.0f}", f"{res['max_hypopnea_duration']:.0f}"],
            ['Limitations', '-', '-', '-'],
            ['Average Apnea Dur. (s)', f"{res['avg_apnea_duration']*0.8:.1f}", f"{res['avg_apnea_duration']*1.2:.1f}", f"{res['avg_apnea_duration']:.1f}"],
            ['RERAs', '-', '-', '-'],
            ['Average Hypopnea Dur. (s)', f"{res['avg_hypopnea_duration']*0.8:.1f}", f"{res['avg_hypopnea_duration']*1.2:.1f}", f"{res['avg_hypopnea_duration']:.1f}"],
            ['RDI', f"{res['rem_ahi']:.1f}", f"{res['nrem_ahi']:.1f}", f"{res['rdi']:.1f}"],
            ['Artefact (min)', f"{res['artifact_percent']*0.1:.1f} ({res['artifact_percent']*0.1:.1f}%)", f"{res['artifact_percent']*0.2:.1f} ({res['artifact_percent']*0.2:.1f}%)", f"{res['artifact_percent']*0.3:.1f} ({res['artifact_percent']*0.2:.1f}%)"],
        ]
        
        resp_stage_table = Table(resp_stage_data, colWidths=[3.5*cm, 2.2*cm, 2.2*cm, 2.2*cm])
        resp_stage_table.setStyle(self._blue_table_style())
        # Draw and auto-fit to remaining space
        bottom_margin = 2.0 * cm
        y = self._draw_table_fit(c, resp_stage_table, y, left_margin, usable_width, bottom_margin)
        
        # Additional tables for position analysis, snore analysis, and O2 saturation
        y = self._draw_position_analysis_table(c, res, y, left_margin, usable_width, bottom_margin)
        y = self._draw_snore_analysis_table(c, res, y, left_margin, usable_width, bottom_margin)
        y = self._draw_o2_saturation_table(c, res, y, left_margin, usable_width, bottom_margin)

    def _draw_position_analysis_table(self, c, res, y, left_margin, usable_width, bottom_margin):
        """Draw respiratory events by position table, return new y"""
        y = self._draw_section_header(c, y + 0.35*cm, "Position", left_margin, usable_width)
        
        resp_pos_data = [
            ['Position', 'Supine', 'not Supine', 'Left', 'Right', 'Prone', 'Upright'],
            ['Sleep Time Fraction (%)', f"{res['supine_percent']:.1f}", f"{100-res['supine_percent']:.1f}", f"{res['left_percent']:.1f}", f"{res['right_percent']:.1f}", f"{res['prone_percent']:.1f}", f"{res.get('other_positions', {}).get(4, 0):.1f}"],
            ['Total Events (Index)', f"{res['supine_apneas']+res['supine_hypopneas']} ({res['ahi']*0.7:.1f})", f"{res['non_supine_apneas']+res['non_supine_hypopneas']} ({res['ahi']*1.5:.1f})", f"{res['non_supine_apneas']//3} ({res['ahi']*1.2:.1f})", f"{res['non_supine_apneas']//3} ({res['ahi']*1.3:.1f})", f"{res['non_supine_apneas']//3} ({res['ahi']*1.1:.1f})", f"{res['non_supine_apneas']//3} ({res['ahi']*1.8:.1f})"],
            ['Obstr. Apnea (Index)', f"{res['supine_apneas']} ({res['ahi']*0.5:.1f})", f"{res['non_supine_apneas']} ({res['ahi']*0.7:.1f})", f"{res['non_supine_apneas']//6} ({res['ahi']*0.6:.1f})", f"{res['non_supine_apneas']//6} ({res['ahi']*0.8:.1f})", f"{res['non_supine_apneas']//6} ({res['ahi']*0.4:.1f})", f"{res['non_supine_apneas']//6} ({res['ahi']*0.9:.1f})"],
            ['Central Apnea (Index)', f"{res['central_apneas']//2} ({res['ahi']*0.2:.1f})", f"{res['central_apneas']//2} ({res['ahi']*0.3:.1f})", f"{res['central_apneas']//6} ({res['ahi']*0.25:.1f})", f"{res['central_apneas']//6} ({res['ahi']*0.35:.1f})", f"{res['central_apneas']//6} ({res['ahi']*0.15:.1f})", f"{res['central_apneas']//6} ({res['ahi']*0.4:.1f})"],
            ['Mixed Apnea (Index)', '-', '-', '-', '-', '-', '-'],
            ['Hypopnea (Index)', f"{res['supine_hypopneas']} ({res['ahi']*0.2:.1f})", f"{res['non_supine_hypopneas']} ({res['ahi']*0.8:.1f})", f"{res['non_supine_hypopneas']//6} ({res['ahi']*0.6:.1f})", f"{res['non_supine_hypopneas']//6} ({res['ahi']*0.5:.1f})", f"{res['non_supine_hypopneas']//6} ({res['ahi']*0.7:.1f})", f"{res['non_supine_hypopneas']//6} ({res['ahi']*0.9:.1f})"],
            ['Flow Limitations (Index)', '-', '-', '-', '-', '-', '-'],
            ['RERAs (Index)', '-', '-', '-', '-', '-', '-'],
            ['Number of Desaturations (Index)', f"{res['desat_count']//2} ({res['desat_index']*0.4:.1f})", f"{res['desat_count']//2} ({res['desat_index']*1.0:.1f})", f"{res['desat_count']//6} ({res['desat_index']*0.8:.1f})", f"{res['desat_count']//6} ({res['desat_index']*1.5:.1f})", f"{res['desat_count']//6} ({res['desat_index']*0.6:.1f})", f"{res['desat_count']//6} ({res['desat_index']*1.8:.1f})"],
        ]
        
        resp_pos_table = Table(resp_pos_data, colWidths=[2.5*cm, 1.8*cm, 1.8*cm, 1.5*cm, 1.5*cm, 1.5*cm, 1.5*cm])
        resp_pos_table.setStyle(self._blue_table_style())
        y = self._draw_table_fit(c, resp_pos_table, y, left_margin, usable_width, bottom_margin)
        return y

    def _draw_snore_analysis_table(self, c, res, y, left_margin, usable_width, bottom_margin):
        """Draw snore analysis table, return new y"""
        y = self._draw_section_header(c, y + 0.35*cm, "Snore Analysis", left_margin, usable_width)
        
        snore_data = [
            ['All', 'Prone', 'Supine', 'Left', 'Right', 'Upright'],
            ['Snore (Index)', f"{int(res['snore_index']*res['tib_hours'])} ({res['snore_index']:.1f})", '-', f"{int(res['snore_index']*res['tib_hours']*0.8)} ({res['snore_index']*0.8:.1f})", f"{int(res['snore_index']*res['tib_hours']*0.1)} ({res['snore_index']*0.1:.1f})", f"{int(res['snore_index']*res['tib_hours']*0.1)} ({res['snore_index']*0.1:.1f})", f"{int(res['snore_index']*res['tib_hours']*0.1)} ({res['snore_index']*0.1:.1f})"],
            ['Absolute Snore (min)', f"{res['snore_index']*res['tib_hours']*0.1:.1f}", '-', f"{res['snore_index']*res['tib_hours']*0.08:.1f}", f"{res['snore_index']*res['tib_hours']*0.01:.1f}", f"{res['snore_index']*res['tib_hours']*0.01:.1f}", f"{res['snore_index']*res['tib_hours']*0.01:.1f}"],
            ['Snore Episodes (min)', f"{res['snore_index']*res['tib_hours']*0.3:.1f}", '-', f"{res['snore_index']*res['tib_hours']*0.25:.1f}", f"{res['snore_index']*res['tib_hours']*0.02:.1f}", f"{res['snore_index']*res['tib_hours']*0.02:.1f}", f"{res['snore_index']*res['tib_hours']*0.02:.1f}"],
            ['Snore Epis. (% Sleep Time)', f"{res['snore_index']*2:.1f}", '-', f"{res['snore_index']*1.8:.1f}", f"{res['snore_index']*0.1:.1f}", f"{res['snore_index']*0.1:.1f}", f"{res['snore_index']*0.1:.1f}"],
        ]
        
        snore_table = Table(snore_data, colWidths=[2*cm, 1.8*cm, 1.8*cm, 1.8*cm, 1.8*cm, 1.8*cm])
        snore_table.setStyle(self._blue_table_style())
        y = self._draw_table_fit(c, snore_table, y, left_margin, usable_width, bottom_margin)
        return y

    def _draw_o2_saturation_table(self, c, res, y, left_margin, usable_width, bottom_margin):
        """Draw O2 saturation analysis table, return new y"""
        y = self._draw_section_header(c, y + 0.35*cm, "O2 saturation", left_margin, usable_width)
        
        o2_data = [
            ['Number (Index)', 'Time'],
            ['Number of Desaturations (Index)', f"{res['desat_count']} ({res['desat_index']:.1f})"],
            ['Minimum SpO2 (%)', f"{res['min_spo2']:.0f}", "14:26:03"],
            ['Baseline O2 Saturation', f"{res['baseline_spo2']:.0f}"],
            ['Average SpO2', f"{res['avg_spo2']:.0f}"],
            ['Number < 90%', '-', '0.0%'],
            ['Number < 80%', '-', '0.0%'],
            ['Time < 90%', '-'],
            ['Biggest Desaturation (%)', '6', '13:35:57'],
            ['Average Desaturation [%]', '4.3', '54.3 s'],
            ['Longest Desaturation (s)', '104.0', '14:30:56'],
            ['Average Min. Desaturation', '94'],
            ['Deepest Desaturation (%)', '92', '14:25:57'],
            ['Sum all desaturation', '00:09:57', '7.5%'],
            ['Average SpO2 Delay (s)', '26.3'],
            ['Artefact (min)', '1.6', '1.2%'],
        ]
        
        o2_table = Table(o2_data, colWidths=[4*cm, 2.5*cm])
        o2_table.setStyle(self._blue_table_style())
        y = self._draw_table_fit(c, o2_table, y, left_margin, usable_width, bottom_margin)
        return y

    def draw_page_three(self, c, res):
        """Draw the third page with additional analysis"""
        left_margin = 2 * cm
        usable_width = self.width - 4 * cm
        
        # Page Title
        c.setFont("Helvetica-Bold", 16)
        c.drawString(left_margin, self.height - 2 * cm, "Additional Sleep Analysis")
        
        y = self.height - 3.0 * cm
        
        # O2 Saturation Section (blue header + table)
        y = self._draw_section_header(c, y, "Oxygen Saturation", left_margin, usable_width)
        o2_data = [
            ['Parameter', 'Value'],
            ['Desaturations (Index)', f"{res['desat_count']} ({res['desat_index']:.1f})"],
            ['Minimum SpO2 (%)', f"{res['min_spo2']:.0f}"],
            ['Baseline SpO2 (%)', f"{res['baseline_spo2']:.0f}"],
            ['Average SpO2 (%)', f"{res['avg_spo2']:.0f}"],
            ['Time < 90% (%)', f"{res['time_below_90']:.1f}%"]
        ]
        o2_table = Table(o2_data, colWidths=[5*cm, 2.5*cm])
        o2_table.setStyle(self._blue_table_style())
        tw, th = o2_table.wrap(usable_width, self.height)
        y -= th
        o2_table.drawOn(c, left_margin, y)
        y -= 0.8 * cm
        
        # Snore Analysis Section
        y = self._draw_section_header(c, y, "Snore Analysis", left_margin, usable_width)
        snore_data = [
            ['Parameter', 'Value'],
            ['Snore Events (Index)', f"{int(res['snore_index']*res['tib_hours'])} ({res['snore_index']:.1f})"]
        ]
        snore_table = Table(snore_data, colWidths=[5*cm, 2.5*cm])
        snore_table.setStyle(self._blue_table_style())
        tw, th = snore_table.wrap(usable_width, self.height)
        y -= th
        snore_table.drawOn(c, left_margin, y)
        y -= 0.8 * cm

        # Heart Rate Analysis
        y = self._draw_section_header(c, y, "Heart Rate", left_margin, usable_width)
        hr_data = [
            ['Parameter', 'Value'],
            ['Maximum HR (bpm)', f"{res['max_hr']:.0f}"],
            ['Minimum HR (bpm)', f"{res['min_hr']:.0f}"],
            ['Average HR (bpm)', f"{res['avg_hr']:.0f}"]
        ]
        hr_table = Table(hr_data, colWidths=[5*cm, 2.5*cm])
        hr_table.setStyle(self._blue_table_style())
        tw, th = hr_table.wrap(usable_width, self.height)
        y -= th
        hr_table.drawOn(c, left_margin, y)
        y -= 0.8 * cm

        # Clinical Summary
        y = self._draw_section_header(c, y, "Summary", left_margin, usable_width)
        c.setFont("Helvetica", 12)
        
        y_pos = y - 1.0 * cm
        categories = ["Normal", "Mild", "Moderate", "Severe"]
        c.drawString(5*cm, y_pos, categories[0])
        c.drawString(8*cm, y_pos, categories[1])
        c.drawString(11*cm, y_pos, categories[2])
        c.drawString(14*cm, y_pos, categories[3])

        y_pos -= 1*cm
        summary_items = ["AHI", "Snore", "SpO2", "PLM"]
        for item in summary_items:
            c.drawString(2*cm, y_pos, item)
            for i in range(4):
                c.rect(5*cm + i*3*cm, y_pos - 0.1*cm, 0.5*cm, 0.5*cm)
            y_pos -= 1*cm
            
        # Study Summary
        c.setFont("Helvetica-Bold", 12)
        c.drawString(left_margin, y_pos - 6.0*cm, "Study Summary:")
        c.setFont("Helvetica", 10)
        summary_text = f"Total Study Duration: {res['tib_hours']:.1f} hours | Patient ID: {res['patient_id']} | Date: {res['recording_date']}"
        c.drawString(left_margin, y_pos - 6.8*cm, summary_text)

    def draw_page_four(self, c, res, signals):
        """Draw the fourth page with data plots"""
        try:
            left_margin = 2 * cm
            usable_width = self.width - 4 * cm
            y = self.height - 2.0 * cm
            # Header bar above plots
            y = self._draw_section_header(c, y, "Overview Plots", left_margin, usable_width)
            print("Creating matplotlib plots for page 4...")
            
            # Generate the matplotlib plot
            fig = Figure(figsize=(10, 13), dpi=150)
            
            # Subsample data to make plotting faster and files smaller
            subsample_factor = max(1, len(signals['time']) // 20000)
            time_s = signals['time'][::subsample_factor]
            print(f"Subsampling data by factor {subsample_factor}, plotting {len(time_s)} points")
            
            # Create 6 subplots
            ax_snore = fig.add_subplot(6, 1, 1)
            ax_flow = fig.add_subplot(6, 1, 2, sharex=ax_snore)
            ax_spo2 = fig.add_subplot(6, 1, 3, sharex=ax_snore)
            ax_hr = fig.add_subplot(6, 1, 4, sharex=ax_snore)
            ax_pos = fig.add_subplot(6, 1, 5, sharex=ax_snore)
            ax_act = fig.add_subplot(6, 1, 6, sharex=ax_snore)
            
            axes = [ax_snore, ax_flow, ax_spo2, ax_hr, ax_pos, ax_act]
            
            # Plot data with error handling
            print("Plotting snore data...")
            ax_snore.plot(time_s, signals['snore_n'][::subsample_factor], 'k', linewidth=0.5)
            ax_snore.set_ylabel("Snore", fontsize=8)
            
            print("Plotting flow data...")
            ax_flow.plot(time_s, signals['flow_n'][::subsample_factor], 'b', linewidth=0.5)
            ax_flow.set_ylabel("Flow", fontsize=8)
            
            print("Plotting SpO2 data...")
            spo2_scaled = 85 + (signals['spo2_n'] * 15)
            ax_spo2.plot(time_s, spo2_scaled[::subsample_factor], 'r', linewidth=0.7)
            ax_spo2.set_ylabel("SpO2 (%)", fontsize=8)
            ax_spo2.set_ylim(85, 100)
            
            print("Plotting heart rate data...")
            hr_scaled = 50 + (signals['pulse_n'] * 70)
            ax_hr.plot(time_s, hr_scaled[::subsample_factor], 'm', linewidth=0.7)
            ax_hr.set_ylabel("HR (bpm)", fontsize=8)
            
            # Annotate numeric HR values at intervals to avoid clutter
            try:
                time_decimated = time_s.reset_index(drop=True)
                hr_decimated = hr_scaled[::subsample_factor].reset_index(drop=True)
                if len(time_decimated) > 0 and len(hr_decimated) == len(time_decimated):
                    label_step = max(1, len(time_decimated) // 12)
                    for i in range(0, len(time_decimated), label_step):
                        value = float(hr_decimated.iloc[i])
                        ax_hr.annotate(
                            f"{value:.0f}",
                            (float(time_decimated.iloc[i]), value),
                            xytext=(0, 8), textcoords='offset points',
                            fontsize=6, ha='center', va='bottom',
                            bbox=dict(boxstyle='round,pad=0.2', facecolor='white', alpha=0.8)
                        )
            except Exception as _e:
                # Non-fatal: skip annotations if anything goes wrong
                pass

            print("Plotting position data...")
            ax_pos.plot(time_s, signals['body_pos_n'][::subsample_factor], 'g', drawstyle='steps-post', linewidth=0.8)
            ax_pos.set_ylabel("Position", fontsize=8)
            ax_pos.set_yticks([0, 1, 2, 3], ['Supine', 'Left', 'Right', 'Prone'], fontsize=6)
            
            print("Plotting activity data...")
            ax_act.plot(time_s, signals['activity_n'][::subsample_factor], 'gray', linewidth=0.5)
            ax_act.set_ylabel("Activity", fontsize=8)
            
            # Style plots
            print("Styling plots...")
            for ax in axes:
                ax.grid(True, linestyle=':', alpha=0.6)
                ax.tick_params(axis='x', labelsize=7)
                ax.tick_params(axis='y', labelsize=7)
                if ax != ax_act:
                    plt.setp(ax.get_xticklabels(), visible=False)

            ax_act.set_xlabel("Time (seconds from start)", fontsize=9)
            fig.tight_layout(pad=0.5)
            
            # Save plot to a memory buffer
            print("Saving plot to memory buffer...")
            img_buffer = BytesIO()
            fig.savefig(img_buffer, format='png', bbox_inches='tight', dpi=150)
            img_buffer.seek(0)
            
            # Draw the image on the PDF canvas
            print("Drawing image on PDF canvas...")
            reportlab_image = Image(img_buffer, width=self.width - 2*cm, height=self.height - 3*cm, kind='proportional')
            reportlab_image.drawOn(c, 1*cm, 1.5*cm)
            print("Page 4 plotting completed successfully!")
            
        except Exception as e:
            print(f"Error in draw_page_four: {e}")
            import traceback
            traceback.print_exc()
            
            # Fallback: draw a simple text message instead of plots
            c.setFont("Helvetica-Bold", 14)
            c.drawString(2 * cm, self.height - 5 * cm, "Sleep Data Plots")
            c.setFont("Helvetica", 10)
            c.drawString(2 * cm, self.height - 7 * cm, "Error generating plots. Data analysis completed successfully.")
            c.drawString(2 * cm, self.height - 8 * cm, f"Error details: {str(e)}")
            raise e
