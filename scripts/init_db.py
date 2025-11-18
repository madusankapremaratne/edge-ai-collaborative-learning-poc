#!/usr/bin/env python3
"""
Initialize database with sample data for development/testing
"""

import sys
import os
from datetime import datetime, timedelta

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import (
    init_db,
    SessionLocal,
    User,
    Student,
    Instructor,
    Course,
    Group,
    Contribution,
    Milestone,
    Communication,
    UserRole,
    GroupStatus,
    MilestoneStatus,
    MessageTone,
)
from auth import auth_service


def create_sample_data():
    """Create sample data for development"""
    db = SessionLocal()

    try:
        print("Creating sample data...")

        # Create admin user
        admin = auth_service.create_user(
            username="admin",
            email="admin@example.com",
            password="admin123",
            full_name="System Administrator",
            role=UserRole.ADMIN,
            db=db
        )
        print(f"✓ Created admin user: {admin.username}")

        # Create instructor
        instructor_user = auth_service.create_user(
            username="prof_smith",
            email="smith@university.edu",
            password="prof123",
            full_name="Dr. Jane Smith",
            role=UserRole.INSTRUCTOR,
            db=db
        )

        instructor = Instructor(
            user_id=instructor_user.id,
            instructor_id="INST001",
            department="Computer Science"
        )
        db.add(instructor)
        db.flush()
        print(f"✓ Created instructor: {instructor_user.full_name}")

        # Create course
        course = Course(
            course_code="CS401",
            course_name="Collaborative Software Engineering",
            instructor_id=instructor.id,
            semester="Fall",
            year=2024,
            is_active=True
        )
        db.add(course)
        db.flush()
        print(f"✓ Created course: {course.course_code} - {course.course_name}")

        # Create students
        student_names = [
            ("alice_wonder", "alice@university.edu", "Alice Wonderland"),
            ("bob_builder", "bob@university.edu", "Bob Builder"),
            ("charlie_ch", "charlie@university.edu", "Charlie Chocolate"),
            ("diana_dev", "diana@university.edu", "Diana Developer"),
            ("eve_eng", "eve@university.edu", "Eve Engineer"),
            ("frank_full", "frank@university.edu", "Frank Fullstack"),
        ]

        students = []
        for i, (username, email, full_name) in enumerate(student_names, 1):
            user = auth_service.create_user(
                username=username,
                email=email,
                password="student123",
                full_name=full_name,
                role=UserRole.STUDENT,
                db=db
            )

            student = Student(
                user_id=user.id,
                student_id=f"STU{i:03d}",
                status="Active"
            )
            db.add(student)
            students.append((user, student))

        db.flush()
        print(f"✓ Created {len(students)} students")

        # Create groups
        group_data = [
            ("Alpha Team", "Project Management System", GroupStatus.AT_RISK),
            ("Beta Squad", "E-Learning Platform", GroupStatus.HEALTHY),
            ("Gamma Force", "Mobile Health App", GroupStatus.THRIVING),
        ]

        groups = []
        for group_name, project, status in group_data:
            group = Group(
                group_name=group_name,
                course_id=course.id,
                project_name=project,
                status=status,
                health_score=0.8 if status == GroupStatus.HEALTHY else 0.5,
                deadline=datetime.utcnow() + timedelta(days=30)
            )
            db.add(group)
            groups.append(group)

        db.flush()
        print(f"✓ Created {len(groups)} groups")

        # Assign students to groups
        for i, (user, student) in enumerate(students):
            group = groups[i % len(groups)]
            student.current_group_id = group.id

        db.flush()

        # Create contributions
        contribution_count = 0
        for i, (user, student) in enumerate(students):
            # Vary contribution levels
            num_contributions = 3 + (i % 5)

            for j in range(num_contributions):
                contribution = Contribution(
                    student_id=student.id,
                    task_type=["Development", "Documentation", "Testing", "Design"][j % 4],
                    action=f"Completed task {j + 1}",
                    hours=1.5 + (j % 3) * 0.5,
                    timestamp=datetime.utcnow() - timedelta(days=j * 2)
                )
                db.add(contribution)
                contribution_count += 1

                # Update student metrics
                student.total_hours += contribution.hours
                student.tasks_completed += 1
                student.last_activity = contribution.timestamp

        db.flush()
        print(f"✓ Created {contribution_count} contributions")

        # Create milestones
        milestone_count = 0
        for group in groups:
            milestones = [
                ("Project Proposal", MilestoneStatus.COMPLETED),
                ("Requirements Document", MilestoneStatus.COMPLETED),
                ("Prototype Development", MilestoneStatus.IN_PROGRESS),
                ("Testing Phase", MilestoneStatus.NOT_STARTED),
            ]

            for i, (title, status) in enumerate(milestones):
                milestone = Milestone(
                    group_id=group.id,
                    title=title,
                    status=status,
                    due_date=datetime.utcnow() + timedelta(days=7 * (i + 1))
                )
                db.add(milestone)
                milestone_count += 1

        db.flush()
        print(f"✓ Created {milestone_count} milestones")

        # Create communications
        comm_count = 0
        for group in groups:
            # Get students in this group
            group_students = [s for u, s in students if s.current_group_id == group.id]

            for i, student in enumerate(group_students[:2]):
                comm = Communication(
                    group_id=group.id,
                    student_id=student.id,
                    message=f"Update on task progress from student {i + 1}",
                    tone=MessageTone.COLLABORATIVE,
                    timestamp=datetime.utcnow() - timedelta(hours=i * 12)
                )
                db.add(comm)
                comm_count += 1

        db.flush()
        print(f"✓ Created {comm_count} communications")

        # Commit all changes
        db.commit()
        print("\n✅ Sample data created successfully!")

        # Print summary
        print("\n" + "=" * 50)
        print("SAMPLE DATA SUMMARY")
        print("=" * 50)
        print(f"Admin user: admin / admin123")
        print(f"Instructor: prof_smith / prof123")
        print(f"Students: {len(students)} (password: student123)")
        print(f"  - alice_wonder, bob_builder, charlie_ch, etc.")
        print(f"Course: {course.course_code} - {course.course_name}")
        print(f"Groups: {len(groups)}")
        for group in groups:
            print(f"  - {group.group_name} ({group.status.value})")
        print("=" * 50)

    except Exception as e:
        db.rollback()
        print(f"\n❌ Error creating sample data: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    print("Initializing database...")
    init_db()
    print("✓ Database tables created")

    print("\nCreating sample data...")
    create_sample_data()

    print("\n✅ Database initialization complete!")
    print("\nYou can now:")
    print("  - Start the API: uvicorn api:app --reload")
    print("  - Start the UI: streamlit run app.py")
    print("  - Login with admin/admin123 or prof_smith/prof123")
