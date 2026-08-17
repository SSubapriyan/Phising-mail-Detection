from flask import render_template, request, jsonify, flash
from app.ml import bp
from app.ml.predictor import predict_scam
from app.models import ScamReport
from app import db
from flask_login import login_required

@bp.route('/predict', methods=['POST'])
@login_required
def predict():
    data = request.get_json()
    if not data or 'text' not in data:
        return jsonify({'error': 'No text provided'}), 400
    
    text = data['text']
    report_id = data.get('report_id')
    
    results = predict_scam(text)
    
    # Update the report in database if report_id is provided
    if report_id:
        report = ScamReport.query.get(report_id)
        if report:
            report.is_scam = results['is_scam']
            report.confidence_score = results['confidence']
            report.safety_grade = results['grade']
            report.set_risk_factors(results['factors'])
            report.explanation = results['explanation']
            report.company_name = results['company']
            report.company_status = results['company_status']
            db.session.commit()
    
    return jsonify(results)
