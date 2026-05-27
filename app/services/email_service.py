import resend

from app.config import settings
from app.models.quote import QuoteRequest


def format_request_type(request_type: str | None) -> str:
    if request_type == "import":
        return "Import Request"

    return "Quote Request"


def format_money(value) -> str:
    if value is None:
        return "Not provided"

    return f"USD {value}"


def send_quote_notification_email(quote: QuoteRequest) -> None:
    if not settings.RESEND_API_KEY or not settings.EMAIL_TO:
        print("Email service not configured. Skipping quote notification email.")
        return

    resend.api_key = settings.RESEND_API_KEY

    request_type = getattr(quote, "request_type", "general")
    request_type_label = format_request_type(request_type)

    import_html_section = ""
    import_text_section = ""

    if request_type == "import":
        import_html_section = f"""
            <h3 style="color:#E30613; margin-top:24px;">Import Details</h3>
            <table style="width:100%; border-collapse:collapse;">
                <tr><td><strong>Origin</strong></td><td>{quote.origin}</td></tr>
                <tr><td><strong>Type of Commodity</strong></td><td>{quote.commodity_type}</td></tr>
                <tr><td><strong>Has HS Code?</strong></td><td>{quote.has_hs_code or "Not provided"}</td></tr>
                <tr><td><strong>Has Certificate of Conformity?</strong></td><td>{quote.has_certificate_of_conformity or "Not provided"}</td></tr>
                <tr><td><strong>Commercial Value</strong></td><td>{format_money(quote.commercial_value_usd)}</td></tr>
            </table>
        """

        import_text_section = f"""
Import Details
Origin: {quote.origin}
Type of Commodity: {quote.commodity_type}
Has HS Code?: {quote.has_hs_code or "Not provided"}
Has Certificate of Conformity?: {quote.has_certificate_of_conformity or "Not provided"}
Commercial Value: {format_money(quote.commercial_value_usd)}
"""

    subject = f"New {request_type_label} - {quote.service_type} - {quote.full_name}"

    html_body = f"""
    <div style="font-family: Arial, sans-serif; background:#f8fafc; padding:24px;">
        <div style="max-width:680px; margin:auto; background:#ffffff; border-radius:18px; padding:28px; border:1px solid #e2e8f0;">
            <h2 style="color:#061846; margin-top:0;">New {request_type_label}</h2>
            <p style="color:#475569;">A new {request_type_label.lower()} has been submitted from the Tenwa Logistics website.</p>

            <h3 style="color:#E30613;">Client Details</h3>
            <table style="width:100%; border-collapse:collapse;">
                <tr><td><strong>Name</strong></td><td>{quote.full_name}</td></tr>
                <tr><td><strong>Email</strong></td><td>{quote.email}</td></tr>
                <tr><td><strong>Phone</strong></td><td>{quote.phone}</td></tr>
                <tr><td><strong>Customer Type</strong></td><td>{quote.customer_type}</td></tr>
                <tr><td><strong>Preferred Contact</strong></td><td>{quote.contact_method}</td></tr>
                <tr><td><strong>Request Type</strong></td><td>{request_type_label}</td></tr>
            </table>

            <h3 style="color:#E30613; margin-top:24px;">Shipment Details</h3>
            <table style="width:100%; border-collapse:collapse;">
                <tr><td><strong>Service Needed</strong></td><td>{quote.service_type}</td></tr>
                <tr><td><strong>Commodity</strong></td><td>{quote.commodity_type}</td></tr>
                <tr><td><strong>Origin</strong></td><td>{quote.origin}</td></tr>
                <tr><td><strong>Destination</strong></td><td>{quote.destination}</td></tr>
                <tr><td><strong>Pieces</strong></td><td>{quote.pieces}</td></tr>
                <tr><td><strong>Weight</strong></td><td>{quote.weight} {quote.weight_unit}</td></tr>
                <tr><td><strong>Dimensions</strong></td><td>{quote.length or "-"} x {quote.width or "-"} x {quote.height or "-"}</td></tr>
                <tr><td><strong>Urgency</strong></td><td>{quote.urgency}</td></tr>
            </table>

            {import_html_section}

            <h3 style="color:#E30613; margin-top:24px;">Notes</h3>
            <p style="background:#f1f5f9; padding:14px; border-radius:12px; color:#334155;">
                {quote.notes or "No additional notes provided."}
            </p>

            <p style="margin-top:24px; font-size:13px; color:#64748b;">
                Quote ID: {quote.id}<br/>
                Status: {quote.status}<br/>
                Created At: {quote.created_at}
            </p>
        </div>
    </div>
    """

    text_body = f"""
New {request_type_label} received from Tenwa website.

Client Details
Name: {quote.full_name}
Email: {quote.email}
Phone: {quote.phone}
Customer Type: {quote.customer_type}
Preferred Contact: {quote.contact_method}
Request Type: {request_type_label}

Shipment Details
Service Needed: {quote.service_type}
Commodity: {quote.commodity_type}
Origin: {quote.origin}
Destination: {quote.destination}
Pieces: {quote.pieces}
Weight: {quote.weight} {quote.weight_unit}
Dimensions: {quote.length or "-"} x {quote.width or "-"} x {quote.height or "-"}
Urgency: {quote.urgency}

{import_text_section}

Notes:
{quote.notes or "No additional notes provided."}

Quote ID: {quote.id}
Status: {quote.status}
Created At: {quote.created_at}
"""

    try:
        resend.Emails.send(
            {
                "from": settings.EMAIL_FROM,
                "to": [settings.EMAIL_TO],
                "subject": subject,
                "html": html_body,
                "text": text_body,
            }
        )

        print(f"{request_type_label} notification email sent for quote ID {quote.id}")

    except Exception as error:
        print(f"Failed to send quote notification email: {error}")