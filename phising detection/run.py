from app import create_app, db
from app.models import User, ScamReport

app = create_app()

@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'ScamReport': ScamReport}

if __name__ == '__main__':
    # Ensure upload folder exists
    import os
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    app.run(debug=True, host='0.0.0.0', port=5000)
