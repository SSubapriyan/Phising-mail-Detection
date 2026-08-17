from flask import render_template, redirect, url_for, request, jsonify, Response
from flask_login import login_required, current_user
from app.dashboard import bp
from app.models import ScamReport
import csv
import io

@bp.route('/')
@bp.route('/home')
def home():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))
    return render_template('home.html', title='CyberSecurity for Job Seekers')

@bp.route('/dashboard')
@login_required
def index():
    query = request.args.get('q', '')
    status_filter = request.args.get('status', 'all')
    
    reports_query = ScamReport.query.filter_by(author=current_user)
    
    if query:
        reports_query = reports_query.filter(ScamReport.title.contains(query) | ScamReport.content.contains(query))
    
    if status_filter == 'scam':
        reports_query = reports_query.filter_by(is_scam=True)
    elif status_filter == 'safe':
        reports_query = reports_query.filter_by(is_scam=False)
        
    reports = reports_query.order_by(ScamReport.timestamp.desc()).all()
    
    # Stats for charts
    total_scans = len(reports)
    scams_detected = sum(1 for r in reports if r.is_scam)
    safe_detected = total_scans - scams_detected
    avg_confidence = sum(r.confidence_score for r in reports if r.confidence_score) / (total_scans or 1)
    
    # Recent trends (last 7 days)
    # Mock data for demonstration if no real history
    trends = [5, 8, 3, 10, 6, 12, 7] 
    
    return render_template('dashboard/index.html', 
                           title='Security Dashboard', 
                           reports=reports,
                           total_scans=total_scans,
                           scams_detected=scams_detected,
                           safe_detected=safe_detected,
                           avg_confidence=avg_confidence,
                           trends=trends,
                           q=query,
                           status=status_filter)

@bp.route('/export/history')
@login_required
def export_history():
    reports = ScamReport.query.filter_by(author=current_user).all()
    
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['ID', 'Date', 'Title', 'Is Scam', 'Confidence', 'Grade', 'Company'])
    
    for r in reports:
        writer.writerow([r.id, r.timestamp, r.title, r.is_scam, r.confidence_score, r.safety_grade, r.company_name])
    
    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-disposition": "attachment; filename=scamguard_history.csv"}
    )
