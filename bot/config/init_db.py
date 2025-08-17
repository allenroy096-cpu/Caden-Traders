from bot.config.models import init_db

if __name__ == "__main__":
    print("Initializing database and creating tables...")
    init_db()
    print("Database setup complete.")
