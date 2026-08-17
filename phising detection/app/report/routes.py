from flask import render_template, send_file, flash, redirect, url_for, current_app
from app.report import bp
from app.models import ScamReport
from app.report.generator import generate_scam_report
from flask_login import login_required, current_user
import os

@bp.route('/download/<int:report_id>')
@login_required
def download_report(report_id):
    report = ScamReport.query.get_or_404(report_id)
    
    if report.author != current_user:
        flash('Unauthorized access.')
        return redirect(url_for('dashboard.index'))

    # Prepare data for the report
    report_data = {
        'timestamp': report.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
        'is_scam': report.is_scam,
        'confidence': report.confidence_score,
        'content': report.content
    }

    # Generate the report
    report_dir = os.path.join(current_app.root_path, 'static', 'reports')
    filename = generate_scam_report(report.id, report_data, report_dir)
    filepath = os.path.join(report_dir, filename)
    
    return send_file(
        filepath,
        mimetype='application/pdf',
        as_attachment=True,
        download_name=filename
    )
