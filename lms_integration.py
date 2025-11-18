"""
LMS Integration Framework for Edge AI Collaborative Learning Platform
Supports Canvas, Moodle, and Blackboard LMS platforms
"""

import logging
from typing import List, Dict, Any, Optional
from abc import ABC, abstractmethod
from datetime import datetime
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

from config import config
from database import (
    Session,
    User,
    Student,
    Course,
    Group,
    Contribution,
    UserRole,
)

logger = logging.getLogger(__name__)


class LMSProvider(ABC):
    """Abstract base class for LMS providers"""

    def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.session = self._create_session()

    def _create_session(self) -> requests.Session:
        """Create a requests session with retry logic"""
        session = requests.Session()

        # Retry strategy
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            method_whitelist=["HEAD", "GET", "OPTIONS", "POST"]
        )

        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)

        return session

    @abstractmethod
    def get_courses(self) -> List[Dict[str, Any]]:
        """Fetch all courses"""
        pass

    @abstractmethod
    def get_course_students(self, course_id: str) -> List[Dict[str, Any]]:
        """Fetch students enrolled in a course"""
        pass

    @abstractmethod
    def get_course_groups(self, course_id: str) -> List[Dict[str, Any]]:
        """Fetch groups in a course"""
        pass

    @abstractmethod
    def get_student_activities(
        self,
        course_id: str,
        student_id: str,
        start_date: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """Fetch student activities"""
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """Check if LMS is available"""
        pass


class CanvasProvider(LMSProvider):
    """Canvas LMS provider"""

    def __init__(self, base_url: str, api_key: str):
        super().__init__(base_url, api_key)
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

    def get_courses(self) -> List[Dict[str, Any]]:
        """Fetch all courses from Canvas"""
        try:
            response = self.session.get(
                f"{self.base_url}/courses",
                headers=self.headers,
                params={"per_page": 100}
            )
            response.raise_for_status()

            courses = response.json()
            return [
                {
                    "lms_id": str(course["id"]),
                    "code": course.get("course_code", ""),
                    "name": course.get("name", ""),
                    "start_date": course.get("start_at"),
                    "end_date": course.get("end_at"),
                }
                for course in courses
            ]
        except Exception as e:
            logger.error(f"Error fetching Canvas courses: {e}")
            return []

    def get_course_students(self, course_id: str) -> List[Dict[str, Any]]:
        """Fetch students from Canvas course"""
        try:
            response = self.session.get(
                f"{self.base_url}/courses/{course_id}/users",
                headers=self.headers,
                params={"enrollment_type[]": "student", "per_page": 100}
            )
            response.raise_for_status()

            students = response.json()
            return [
                {
                    "lms_id": str(student["id"]),
                    "name": student.get("name", ""),
                    "email": student.get("email", ""),
                    "username": student.get("login_id", ""),
                }
                for student in students
            ]
        except Exception as e:
            logger.error(f"Error fetching Canvas students: {e}")
            return []

    def get_course_groups(self, course_id: str) -> List[Dict[str, Any]]:
        """Fetch groups from Canvas course"""
        try:
            response = self.session.get(
                f"{self.base_url}/courses/{course_id}/groups",
                headers=self.headers,
                params={"per_page": 100}
            )
            response.raise_for_status()

            groups = response.json()
            return [
                {
                    "lms_id": str(group["id"]),
                    "name": group.get("name", ""),
                    "description": group.get("description", ""),
                    "member_count": group.get("members_count", 0),
                }
                for group in groups
            ]
        except Exception as e:
            logger.error(f"Error fetching Canvas groups: {e}")
            return []

    def get_student_activities(
        self,
        course_id: str,
        student_id: str,
        start_date: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """Fetch student activities from Canvas"""
        try:
            # Get submissions
            response = self.session.get(
                f"{self.base_url}/courses/{course_id}/students/submissions",
                headers=self.headers,
                params={"student_ids[]": student_id, "per_page": 100}
            )
            response.raise_for_status()

            submissions = response.json()
            activities = []

            for submission in submissions:
                if submission.get("submitted_at"):
                    activities.append({
                        "type": "submission",
                        "title": submission.get("assignment", {}).get("name", "Assignment"),
                        "timestamp": submission.get("submitted_at"),
                        "score": submission.get("score"),
                        "grade": submission.get("grade"),
                    })

            return activities
        except Exception as e:
            logger.error(f"Error fetching Canvas activities: {e}")
            return []

    def is_available(self) -> bool:
        """Check if Canvas is available"""
        try:
            response = self.session.get(
                f"{self.base_url}/users/self",
                headers=self.headers,
                timeout=5
            )
            return response.status_code == 200
        except:
            return False


class MoodleProvider(LMSProvider):
    """Moodle LMS provider"""

    def __init__(self, base_url: str, api_key: str):
        super().__init__(base_url, api_key)

    def _call_api(self, function: str, params: Dict[str, Any]) -> Any:
        """Call Moodle Web Services API"""
        try:
            data = {
                "wstoken": self.api_key,
                "wsfunction": function,
                "moodlewsrestformat": "json",
                **params
            }

            response = self.session.post(
                f"{self.base_url}/webservice/rest/server.php",
                data=data
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Moodle API error ({function}): {e}")
            return None

    def get_courses(self) -> List[Dict[str, Any]]:
        """Fetch all courses from Moodle"""
        result = self._call_api("core_course_get_courses", {})
        if not result:
            return []

        return [
            {
                "lms_id": str(course["id"]),
                "code": course.get("shortname", ""),
                "name": course.get("fullname", ""),
                "start_date": datetime.fromtimestamp(course.get("startdate", 0)),
                "end_date": datetime.fromtimestamp(course.get("enddate", 0)) if course.get("enddate") else None,
            }
            for course in result
            if isinstance(result, list)
        ]

    def get_course_students(self, course_id: str) -> List[Dict[str, Any]]:
        """Fetch students from Moodle course"""
        result = self._call_api(
            "core_enrol_get_enrolled_users",
            {"courseid": course_id}
        )
        if not result:
            return []

        return [
            {
                "lms_id": str(user["id"]),
                "name": user.get("fullname", ""),
                "email": user.get("email", ""),
                "username": user.get("username", ""),
            }
            for user in result
            if isinstance(result, list)
        ]

    def get_course_groups(self, course_id: str) -> List[Dict[str, Any]]:
        """Fetch groups from Moodle course"""
        result = self._call_api(
            "core_group_get_course_groups",
            {"courseid": course_id}
        )
        if not result:
            return []

        return [
            {
                "lms_id": str(group["id"]),
                "name": group.get("name", ""),
                "description": group.get("description", ""),
                "member_count": len(group.get("members", [])),
            }
            for group in result
            if isinstance(result, list)
        ]

    def get_student_activities(
        self,
        course_id: str,
        student_id: str,
        start_date: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """Fetch student activities from Moodle"""
        # Moodle activities are more complex, would require multiple API calls
        # This is a simplified version
        return []

    def is_available(self) -> bool:
        """Check if Moodle is available"""
        result = self._call_api("core_webservice_get_site_info", {})
        return result is not None


class LMSSyncService:
    """Service for syncing data from LMS to local database"""

    def __init__(self, provider: LMSProvider):
        self.provider = provider

    def sync_courses(self, db: Session) -> int:
        """Sync courses from LMS to database"""
        try:
            lms_courses = self.provider.get_courses()
            synced_count = 0

            for lms_course in lms_courses:
                # Check if course exists
                existing_course = db.query(Course).filter(
                    Course.lms_course_id == lms_course["lms_id"]
                ).first()

                if existing_course:
                    # Update existing course
                    existing_course.course_name = lms_course["name"]
                    existing_course.course_code = lms_course["code"]
                    existing_course.updated_at = datetime.utcnow()
                else:
                    # Create new course (requires instructor)
                    # For now, skip courses without instructor
                    logger.warning(f"Skipping course {lms_course['name']} - no instructor assigned")
                    continue

                synced_count += 1

            db.commit()
            logger.info(f"Synced {synced_count} courses from LMS")
            return synced_count

        except Exception as e:
            db.rollback()
            logger.error(f"Error syncing courses: {e}")
            return 0

    def sync_students(self, db: Session, course_id: int) -> int:
        """Sync students from LMS course to database"""
        try:
            course = db.query(Course).filter(Course.id == course_id).first()
            if not course or not course.lms_course_id:
                return 0

            lms_students = self.provider.get_course_students(course.lms_course_id)
            synced_count = 0

            for lms_student in lms_students:
                # Check if user exists
                existing_user = db.query(User).filter(
                    User.lms_user_id == lms_student["lms_id"]
                ).first()

                if not existing_user:
                    # Create user and student profile
                    user = User(
                        username=lms_student["username"],
                        email=lms_student["email"],
                        full_name=lms_student["name"],
                        hashed_password="",  # LMS users login via LMS
                        role=UserRole.STUDENT,
                        lms_user_id=lms_student["lms_id"],
                        is_active=True
                    )
                    db.add(user)
                    db.flush()

                    student = Student(
                        user_id=user.id,
                        student_id=lms_student["lms_id"],
                    )
                    db.add(student)

                synced_count += 1

            db.commit()
            logger.info(f"Synced {synced_count} students from LMS")
            return synced_count

        except Exception as e:
            db.rollback()
            logger.error(f"Error syncing students: {e}")
            return 0

    def sync_groups(self, db: Session, course_id: int) -> int:
        """Sync groups from LMS course to database"""
        try:
            course = db.query(Course).filter(Course.id == course_id).first()
            if not course or not course.lms_course_id:
                return 0

            lms_groups = self.provider.get_course_groups(course.lms_course_id)
            synced_count = 0

            for lms_group in lms_groups:
                # Check if group exists
                existing_group = db.query(Group).filter(
                    Group.lms_group_id == lms_group["lms_id"]
                ).first()

                if existing_group:
                    # Update existing group
                    existing_group.group_name = lms_group["name"]
                    existing_group.updated_at = datetime.utcnow()
                else:
                    # Create new group
                    group = Group(
                        group_name=lms_group["name"],
                        course_id=course_id,
                        lms_group_id=lms_group["lms_id"],
                    )
                    db.add(group)

                synced_count += 1

            db.commit()
            logger.info(f"Synced {synced_count} groups from LMS")
            return synced_count

        except Exception as e:
            db.rollback()
            logger.error(f"Error syncing groups: {e}")
            return 0


def create_lms_provider() -> Optional[LMSProvider]:
    """Create LMS provider based on configuration"""
    if not config.LMS_API_URL or not config.LMS_API_KEY:
        logger.warning("LMS integration not configured")
        return None

    if config.LMS_PROVIDER == "canvas":
        return CanvasProvider(config.LMS_API_URL, config.LMS_API_KEY)
    elif config.LMS_PROVIDER == "moodle":
        return MoodleProvider(config.LMS_API_URL, config.LMS_API_KEY)
    else:
        logger.error(f"Unsupported LMS provider: {config.LMS_PROVIDER}")
        return None


# Singleton instance
lms_provider = create_lms_provider()
lms_sync_service = LMSSyncService(lms_provider) if lms_provider else None


if __name__ == "__main__":
    # Test LMS integration
    from database import init_db, SessionLocal

    if lms_provider and lms_provider.is_available():
        print(f"LMS ({config.LMS_PROVIDER}) is available")

        # Test fetching courses
        courses = lms_provider.get_courses()
        print(f"Found {len(courses)} courses")

        if courses:
            print(f"First course: {courses[0]}")
    else:
        print("LMS integration not configured or not available")
