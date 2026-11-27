from django.contrib.auth.models import Group, User
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Application, Candidate, Employer, Job


class RBACApiTests(APITestCase):
    def setUp(self):
        self.admin = self.create_user("admin@example.com", "Admin", is_staff=True)
        self.employer_user = self.create_user("employer@example.com", "Employer")
        self.other_employer_user = self.create_user(
            "other-employer@example.com", "Employer"
        )
        self.candidate_user = self.create_user(
            "candidate@example.com", "Candidate"
        )
        self.other_candidate_user = self.create_user(
            "other-candidate@example.com", "Candidate"
        )
        self.employer = Employer.objects.create(
            user=self.employer_user,
            company_name="Example Co",
            industry="Technology",
        )
        self.other_employer = Employer.objects.create(
            user=self.other_employer_user,
            company_name="Other Co",
            industry="Finance",
        )
        self.candidate = Candidate.objects.create(
            user=self.candidate_user,
            full_name="Test Candidate",
            phone="555-0100",
        )
        self.other_candidate = Candidate.objects.create(
            user=self.other_candidate_user,
            full_name="Other Candidate",
            phone="555-0101",
        )
        self.job = Job.objects.create(
            employer=self.employer,
            title="Backend Developer",
            description="Build APIs",
            location="Remote",
        )
        self.other_job = Job.objects.create(
            employer=self.other_employer,
            title="Other Developer",
            description="Build systems",
            location="Remote",
        )
        self.application = Application.objects.create(
            candidate=self.other_candidate,
            job=self.job,
        )

    def create_user(self, email, group_name, is_staff=False):
        user = User.objects.create_user(
            username=email,
            email=email,
            password="StrongPassword123!",
            is_staff=is_staff,
        )
        Group.objects.get_or_create(name=group_name)
        if group_name:
            user.groups.add(Group.objects.get(name=group_name))
        return user

    def authenticate(self, user):
        self.client.force_authenticate(user=user)

    def assert_success_response(self, response):
        self.assertEqual(response.data["success"], True)
        self.assertIn("message", response.data)
        self.assertIn("data", response.data)

    def assert_error_response(self, response):
        self.assertEqual(response.data["success"], False)
        self.assertIn("message", response.data)
        self.assertIn("errors", response.data)

    def test_admin_can_access_admin_api(self):
        self.authenticate(self.admin)
        response = self.client.get("/api/recruitment/admin/users/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_employer_can_create_and_list_own_jobs(self):
        self.authenticate(self.employer_user)
        response = self.client.post(
            "/api/recruitment/employer/jobs/",
            {
                "title": "Django Developer",
                "description": "Build Django services",
                "location": "Remote",
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data["success"])
        self.assertEqual(response.data["data"]["employer"], self.employer.id)

    def test_candidate_can_view_and_create_own_application(self):
        self.authenticate(self.candidate_user)
        response = self.client.post(
            "/api/recruitment/candidate/applications/",
            {"job_id": self.job.id},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data["success"])
        self.assertEqual(response.data["data"]["candidate"], self.candidate.id)

    def test_candidate_cannot_create_job(self):
        self.authenticate(self.candidate_user)
        response = self.client.post(
            "/api/recruitment/employer/jobs/",
            {
                "title": "Unauthorized",
                "description": "No",
                "location": "Remote",
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assert_error_response(response)

    def test_employer_cannot_apply_for_job(self):
        self.authenticate(self.employer_user)
        response = self.client.post(
            "/api/recruitment/candidate/applications/",
            {"job_id": self.job.id},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assert_error_response(response)

    def test_candidate_and_employer_cannot_access_admin_api(self):
        for user in (self.candidate_user, self.employer_user):
            self.authenticate(user)
            response = self.client.get("/api/recruitment/admin/users/")
            self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
            self.assert_error_response(response)

    def test_employer_cannot_modify_another_employers_job(self):
        self.authenticate(self.employer_user)
        response = self.client.patch(
            f"/api/recruitment/employer/jobs/{self.other_job.id}/",
            {"title": "Hijacked"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_candidate_cannot_view_another_candidates_application(self):
        self.authenticate(self.candidate_user)
        response = self.client.get(
            f"/api/recruitment/candidate/applications/{self.application.id}/"
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_unauthenticated_user_cannot_access_protected_api(self):
        response = self.client.get("/api/recruitment/employer/jobs/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_role_change_fields_are_rejected(self):
        self.authenticate(self.admin)
        response = self.client.patch(
            f"/api/recruitment/admin/users/{self.candidate_user.id}/status/",
            {"groups": ["Admin"], "is_active": True},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assert_error_response(response)

    def test_public_job_list_is_available_without_authentication(self):
        response = self.client.get("/api/recruitment/jobs/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])
        self.assertEqual(len(response.data["data"]), 2)
