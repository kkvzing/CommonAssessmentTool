"""
Module for initializing the database with default users and client data from a CSV file.
It creates an admin user, a case worker, and populates the database with client information
and associated case data from a CSV file.
"""

import pandas as pd
from app.database import SessionLocal
from app.models import Client, User, ClientCase, UserRole
from app.auth.router import get_password_hash

def initialize_database():
    """
    Initializes the database by creating default users (admin and case worker) and loading
    client data from a CSV file into the database.
    """
    print("Starting database initialization...")
    db = SessionLocal()
    try:
        # Create admin user if doesn't exist
        admin = db.query(User).filter(User.username == "admin").first()
        if not admin:
            admin_user = User(
                username="admin",
                email="admin@example.com",
                hashed_password=get_password_hash("admin123"),
                role=UserRole.ADMIN
            )
            db.add(admin_user)
            db.commit()
            print("Admin user created successfully")
        else:
            print("Admin user already exists")

        # Create case worker if doesn't exist
        case_worker = db.query(User).filter(User.username == "case_worker1").first()
        if not case_worker:
            case_worker = User(
                username="case_worker1",
                email="caseworker1@example.com",
                hashed_password=get_password_hash("worker123"),
                role=UserRole.CASE_WORKER
            )
            db.add(case_worker)
            db.commit()
            print("Case worker created successfully")
        else:
            print("Case worker already exists")

        # Load CSV data
        print("Loading CSV data...")
        df = pd.read_csv('app/clients/service/data_commontool.csv')

        # Convert data types for integer columns
        integer_columns = [
            'age', 'gender', 'work_experience', 'canada_workex', 'dep_num',
            'level_of_schooling', 'reading_english_scale', 'speaking_english_scale',
            'writing_english_scale', 'numeracy_scale', 'computer_scale',
            'housing', 'income_source', 'time_unemployed', 'success_rate'
        ]
        for col in integer_columns:
            df[col] = pd.to_numeric(df[col], errors='raise')

        # Process each row in the CSV and create client and client_case
        for _, row in df.iterrows():  # Using _ to discard the unused 'index' variable
            # Create client
            client = Client(
                age=int(row['age']),
                gender=int(row['gender']),
                work_experience=int(row['work_experience']),
                canada_workex=int(row['canada_workex']),
                dep_num=int(row['dep_num']),
                canada_born=bool(row['canada_born']),
                citizen_status=bool(row['citizen_status']),
                level_of_schooling=int(row['level_of_schooling']),
                fluent_english=bool(row['fluent_english']),
                reading_english_scale=int(row['reading_english_scale']),
                speaking_english_scale=int(row['speaking_english_scale']),
                writing_english_scale=int(row['writing_english_scale']),
                numeracy_scale=int(row['numeracy_scale']),
                computer_scale=int(row['computer_scale']),
                transportation_bool=bool(row['transportation_bool']),
                caregiver_bool=bool(row['caregiver_bool']),
                housing=int(row['housing']),
                income_source=int(row['income_source']),
                felony_bool=bool(row['felony_bool']),
                attending_school=bool(row['attending_school']),
                currently_employed=bool(row['currently_employed']),
                substance_use=bool(row['substance_use']),
                time_unemployed=int(row['time_unemployed']),
                need_mental_health_support_bool=bool(row['need_mental_health_support_bool'])
            )
            db.add(client)
            db.commit()

            # Create client_case
            client_case = ClientCase(
                client_id=client.id,
                user_id=admin_user.id,  # Assign to admin
                employment_assistance=bool(row['employment_assistance']),
                life_stabilization=bool(row['life_stabilization']),
                retention_services=bool(row['retention_services']),
                specialized_services=bool(row['specialized_services']),
                employment_related_financial_supports=bool(row['employment_related_financial_supports']),
                employer_financial_supports=bool(row['employer_financial_supports']),
                enhanced_referrals=bool(row['enhanced_referrals']),
                success_rate=int(row['success_rate'])
            )
            db.add(client_case)
            db.commit()

        print("Database initialization completed successfully!")

    except (FileNotFoundError, ValueError) as e:
        print(f"Error during initialization: {e}")
        db.rollback()
    except Exception as e:
        print(f"Unexpected error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    initialize_database()

