from app import app, db, UserCreds, create_user_table

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        existing_users = UserCreds.query.all()
        for user in existing_users:
            create_user_table(user.email)
    app.run(debug=True)
