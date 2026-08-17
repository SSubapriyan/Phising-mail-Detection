from flask import render_template, request, flash, redirect, url_for
from app.ocr import bp
from app.ocr.processor import extract_text_from_image, TESSERACT_AVAILABLE
from app.models import ScamReport, ScanFile
from app import db
import os
import logging
from werkzeug.utils import secure_filename
from flask import current_app
from flask_login import login_required, current_user

logger = logging.getLogger(__name__)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf'}
MAX_FILE_SIZE = 10 * 1024 * 1024  # Increased to 10MB for multiple files

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@bp.route('/upload', methods=['GET', 'POST'])
@login_required
def upload_image():
    if not TESSERACT_AVAILABLE:
        flash('OCR Engine (Tesseract) is not configured on the server. Please contact admin.', 'danger')

    if request.method == 'POST':
        # Check if text was pasted instead
        pasted_text = request.form.get('pasted_text')
        if pasted_text and pasted_text.strip():
            report = ScamReport(
                title="Pasted Text Analysis",
                content=pasted_text.strip(),
                author=current_user
            )
            db.session.add(report)
            db.session.commit()
            return render_template(
                'ocr/result.html',
                title='Analysis Results',
                text=pasted_text.strip(),
                report_id=report.id
            )

        # Handle multi-file upload
        if 'files' not in request.files:
            flash('No files provided', 'warning')
            return redirect(request.url)
            
        files = request.files.getlist('files')
        if not files or files[0].filename == '':
            flash('No selected files', 'warning')
            return redirect(request.url)
            
        combined_text = ""
        report_title = f"Multi-file Scan ({len(files)} files)" if len(files) > 1 else f"Scan: {files[0].filename}"
        
        # Initial report object
        report = ScamReport(
            title=report_title,
            content="", # Will fill after OCR
            author=current_user
        )
        db.session.add(report)
        db.session.flush() # Get report.id

        os.makedirs(current_app.config['UPLOAD_FOLDER'], exist_ok=True)

        for file in files:
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                unique_filename = f"{current_user.id}_{os.urandom(4).hex()}_{filename}"
                filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], unique_filename)
                
                file.save(filepath)
                
                # Create ScanFile record
                scan_file = ScanFile(
                    filename=filename,
                    filepath=unique_filename,
                    file_type=filename.rsplit('.', 1)[1].lower(),
                    report_id=report.id
                )
                db.session.add(scan_file)
                
                # Process OCR for this file
                extracted_text = extract_text_from_image(filepath)
                if extracted_text and not extracted_text.startswith("ERROR:"):
                    combined_text += f"\n--- Content from {filename} ---\n{extracted_text}\n"
            else:
                flash(f'Skipped invalid file: {file.filename}', 'warning')

        if not combined_text.strip():
            db.session.rollback()
            flash('OCR failed or no text extracted from provided files.', 'danger')
            return redirect(request.url)

        # Update report with final content
        report.content = combined_text.strip()
        report.ocr_text = combined_text.strip()
        db.session.commit()
        
        flash('Multi-file OCR Processing complete.', 'success')
        return render_template(
            'ocr/result.html',
            title='Analysis Results',
            text=report.content,
            report_id=report.id
        )
            
    return render_template('ocr/upload.html', title='Analyze Offer')
