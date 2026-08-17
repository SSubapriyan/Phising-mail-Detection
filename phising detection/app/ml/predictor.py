import joblib
import os
import re
from flask import current_app

def analyze_risk_factors(text):
    """
    Identifies specific risk indicators in the text.
    """
    factors = []
    
    # Financial indicators
    if re.search(r'\$?[\d,]+\s*(weekly|monthly|daily)', text, re.I):
        factors.append("Suspiciously high salary mentions")
    if re.search(r'(gift card|bitcoin|crypto|wire transfer|zelle|cash app)', text, re.I):
        factors.append("Non-standard payment methods requested")
    if re.search(r'(processing fee|security deposit|equipment fee|training fee)', text, re.I):
        factors.append("Upfront payment requested")

    # Communication indicators
    if re.search(r'(telegram|whatsapp|signal|kik|hangouts)', text, re.I):
        factors.append("Uses informal/encrypted messaging for hiring")
    if re.search(r'(immediate|urgent|hurry|start today)', text, re.I):
        factors.append("Creates artificial sense of urgency")

    # Content quality
    if re.search(r'(kindly|dear|congratulation|won a job)', text, re.I):
        factors.append("Uses generic or suspicious greetings")
    
    return factors

def calculate_safety_grade(score, is_scam, factors):
    """
    Returns a grade (A-D) based on risk factors and ML score.
    """
    risk_points = len(factors) * 15
    if is_scam:
        risk_points += 50
    
    final_score = 100 - min(risk_points + (score * 50), 100)
    
    if final_score >= 85: return "A"
    if final_score >= 70: return "B"
    if final_score >= 40: return "C"
    return "D"

def generate_explanation(is_scam, factors):
    """
    Generates a human-readable explanation of the risk.
    """
    if not is_scam and not factors:
        return "This offer appears legitimate based on current analysis. No major red flags were detected."
    
    if is_scam:
        explanation = "High risk detected. The offer structure closely matches known fraudulent patterns. "
    else:
        explanation = "Potential risk detected. While not explicitly classified as a scam, several suspicious elements were found. "
    
    if factors:
        explanation += "Key red flags include: " + ", ".join(factors).lower() + "."
    
    return explanation

def verify_company(text):
    """
    Mock company verification logic.
    In a real app, this would query an API (e.g., Clearbit, LinkedIn).
    """
    # Simple regex to find company-like names
    match = re.search(r'(company|inc|corp|llc|ltd|limited)\s*:\s*([A-Z][\w\s]+)', text, re.I)
    name = match.group(2).strip() if match else "Unknown Company"
    
    # Mock status
    verified_list = ["Google", "Microsoft", "Amazon", "Apple", "Meta", "IBM", "Intel"]
    status = "Verified" if any(v.lower() in name.lower() for v in verified_list) else "Suspicious"
    
    return name, status

def predict_scam(text):
    """
    Comprehensive risk analysis using ML and heuristic rules.
    """
    model_path = os.path.join(current_app.root_path, 'ml', 'models', 'scam_model.joblib')
    
    # Heuristic analysis
    factors = analyze_risk_factors(text)
    company_name, company_status = verify_company(text)
    
    is_scam_ml = False
    confidence_ml = 0.0

    if os.path.exists(model_path):
        try:
            model = joblib.load(model_path)
            prediction = model.predict([text])[0]
            probabilities = model.predict_proba([text])[0]
            is_scam_ml = bool(prediction == 1)
            confidence_ml = float(probabilities[1] if is_scam_ml else probabilities[0])
        except Exception as e:
            current_app.logger.error(f"ML Prediction Error: {str(e)}")

    # Combined logic
    is_scam = is_scam_ml or len(factors) >= 2
    confidence = max(confidence_ml, len(factors) * 0.2)
    
    grade = calculate_safety_grade(confidence, is_scam, factors)
    explanation = generate_explanation(is_scam, factors)
    
    return {
        'is_scam': is_scam,
        'confidence': confidence,
        'grade': grade,
        'factors': factors,
        'explanation': explanation,
        'company': company_name,
        'company_status': company_status
    }
