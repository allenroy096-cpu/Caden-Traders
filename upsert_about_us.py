from models import SessionLocal, AboutUs
from datetime import datetime

# Example About Us content
ABOUT_US_TEXT = '''
Caden Traders is a self-learning financial analytics platform. We provide advanced analytics, automated trading insights, and real-time portfolio management for modern investors. Our mission is to empower users with actionable data and transparent results.
'''

def upsert_about_us(content):
    session = SessionLocal()
    about = session.query(AboutUs).first()
    if about:
        about.content = content
        about.last_updated = datetime.utcnow()
    else:
        about = AboutUs(content=content)
        session.add(about)
    session.commit()
    session.close()
    print("About Us content updated.")

if __name__ == "__main__":
    upsert_about_us(ABOUT_US_TEXT)
