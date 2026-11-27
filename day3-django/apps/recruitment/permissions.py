from rest_framework.permissions import BasePermission, SAFE_METHODS


def user_in_group(user, group_name):
    return (
        user.is_authenticated
        and user.groups.filter(name__iexact=group_name).exists()
    )
    

class IsAdmin(BasePermission):
    message = "Administrator access is required."

    def has_permission(self, request, view):
        return bool(
            request.user.is_authenticated
            and (
                request.user.is_staff
                or request.user.is_superuser
                or user_in_group(request.user, "Admin")
            )
        )


class IsEmployer(BasePermission):
    message = "Employer access is required."

    def has_permission(self, request, view):
        return user_in_group(request.user, "Employer")


class IsCandidate(BasePermission):
    message = "Candidate access is required."

    def has_permission(self, request, view):
        return user_in_group(request.user, "Candidate")


class IsAdminOrReadOnly(BasePermission):
    message = "Administrator access is required for write operations."

    def has_permission(self, request, view):
        return request.method in SAFE_METHODS or IsAdmin().has_permission(
            request, view
        )


class IsEmployerOwner(BasePermission):
    message = "You may only manage your own jobs."

    def has_permission(self, request, view):
        return IsEmployer().has_permission(request, view)

    def has_object_permission(self, request, view, obj):
        return obj.employer.user_id == request.user.id


class IsCandidateOwner(BasePermission):
    message = "You may only access your own applications."

    def has_permission(self, request, view):
        return IsCandidate().has_permission(request, view)

    def has_object_permission(self, request, view, obj):
        return obj.candidate.user_id == request.user.id
