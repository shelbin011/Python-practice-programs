import django_filters

from .models import Job


class JobFilter(django_filters.FilterSet):

    skills = django_filters.CharFilter(
        field_name="skills",
        lookup_expr="icontains"
    )

    experience = django_filters.CharFilter(
        field_name="experience",
        lookup_expr="icontains"
    )

    min_salary = django_filters.NumberFilter(
        field_name="salary_min",
        lookup_expr="gte"
    )

    max_salary = django_filters.NumberFilter(
        field_name="salary_max",
        lookup_expr="lte"
    )

    location = django_filters.CharFilter(
        field_name="location",
        lookup_expr="icontains"
    )

    job_type = django_filters.CharFilter(
        field_name="job_type",
        lookup_expr="exact"
    )
    employer = django_filters.NumberFilter(
    field_name="employer_id",
    lookup_expr="exact"
)

    class Meta:
        model = Job
        fields = []