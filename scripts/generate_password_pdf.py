from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "data" / "password-reset-guide.pdf"

styles = getSampleStyleSheet()
styles.add(ParagraphStyle(name="Brand", parent=styles["Title"], textColor=colors.HexColor("#4F46E5"), fontName="Helvetica-Bold", fontSize=25, leading=30, spaceAfter=7 * mm))
styles.add(ParagraphStyle(name="Section", parent=styles["Heading2"], textColor=colors.HexColor("#172033"), fontName="Helvetica-Bold", fontSize=15, leading=19, spaceBefore=5 * mm, spaceAfter=2 * mm))
styles.add(ParagraphStyle(name="Body2", parent=styles["BodyText"], textColor=colors.HexColor("#475569"), fontSize=10.5, leading=16, spaceAfter=2.5 * mm))


def footer(canvas, doc):
    canvas.saveState()
    canvas.setStrokeColor(colors.HexColor("#E2E8F0"))
    canvas.line(18 * mm, 15 * mm, 192 * mm, 15 * mm)
    canvas.setFillColor(colors.HexColor("#64748B"))
    canvas.setFont("Helvetica", 8)
    canvas.drawString(18 * mm, 10 * mm, "LUMINA SUPPORT · VERIFIED GUIDE")
    canvas.drawRightString(192 * mm, 10 * mm, f"PAGE {doc.page}")
    canvas.restoreState()


def build():
    doc = SimpleDocTemplate(str(OUTPUT), pagesize=A4, leftMargin=20 * mm, rightMargin=20 * mm, topMargin=20 * mm, bottomMargin=22 * mm, title="Lumina Password Reset Guide", author="Lumina Support")
    story = [Paragraph("Password reset & account recovery", styles["Brand"]), Paragraph("A verified guide for customers and support specialists", styles["Body2"]), Spacer(1, 3 * mm)]
    story += [Paragraph("Reset a known account password", styles["Section"]), Paragraph("1. Open the Lumina sign-in page and select <b>Forgot password?</b>.<br/>2. Enter the verified account email address.<br/>3. Open the newest reset email and use its link within 30 minutes.<br/>4. Choose a password of at least 12 characters that has not been used on the account.<br/>5. Sign in again. All other active sessions are revoked after the password changes.", styles["Body2"])]
    story += [Paragraph("If the email does not arrive", styles["Section"]), Paragraph("Wait up to five minutes, then inspect spam and corporate quarantine. Allowlist <b>notifications@lumina.example</b>. Request one new link and use only the newest message because each new request invalidates earlier links. Confirm that the address belongs to an active Lumina account, but do not reveal whether an unknown address is registered.", styles["Body2"])]
    story += [Paragraph("Account lock and multi-factor authentication", styles["Section"]), Paragraph("Five failed sign-in attempts trigger a 15-minute temporary lock. A password reset does not remove multi-factor authentication. Support agents cannot disable MFA or accept one-time codes in chat. Loss of all enrolled factors requires identity verification and escalation to Account Security.", styles["Body2"])]
    data = [["Situation", "Required action"], ["Expired link", "Request one new link and open the latest email."], ["Temporary lock", "Wait 15 minutes; avoid repeated automated attempts."], ["No MFA device", "Escalate for verified account recovery."], ["Suspected compromise", "Reset password, revoke sessions, rotate API keys, review audit logs."]]
    table = Table(data, colWidths=[48 * mm, 112 * mm], repeatRows=1)
    table.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#4F46E5")), ("TEXTCOLOR", (0, 0), (-1, 0), colors.white), ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"), ("FONTNAME", (0, 1), (-1, -1), "Helvetica"), ("FONTSIZE", (0, 0), (-1, -1), 9), ("LEADING", (0, 0), (-1, -1), 13), ("GRID", (0, 0), (-1, -1), .5, colors.HexColor("#CBD5E1")), ("BACKGROUND", (0, 1), (-1, -1), colors.HexColor("#F8FAFC")), ("VALIGN", (0, 0), (-1, -1), "TOP"), ("LEFTPADDING", (0, 0), (-1, -1), 8), ("RIGHTPADDING", (0, 0), (-1, -1), 8), ("TOPPADDING", (0, 0), (-1, -1), 7), ("BOTTOMPADDING", (0, 0), (-1, -1), 7)]))
    story += [Paragraph("Support decision guide", styles["Section"]), table, Paragraph("Security boundary", styles["Section"]), Paragraph("Never ask for a password, reset link, recovery code, or one-time code. Ownership changes, MFA removal, and suspected account takeover must be handled by a human Account Security specialist after verification.", styles["Body2"])]
    doc.build(story, onFirstPage=footer, onLaterPages=footer)


if __name__ == "__main__":
    build()
    print(OUTPUT)

