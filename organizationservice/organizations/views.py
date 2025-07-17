from rest_framework import viewsets, permissions
from .models import Organization, Company, Entity
from .serializers import OrganizationSerializer, CompanySerializer, EntitySerializer
from rest_framework.decorators import action
from rest_framework.views import APIView
from rest_framework.response import Response
import requests
from rest_framework import status, generics

class OrganizationViewSet(viewsets.ModelViewSet):
    queryset = Organization.objects.all()
    serializer_class = OrganizationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            print("Organization create - Validation Errors:", serializer.errors)
            return Response(serializer.errors, status=400)
        self.perform_create(serializer)
        print("Organization created:", serializer.data)
        return Response(serializer.data, status=201)

    @action(detail=False, methods=['get'], url_path='by-user/(?P<user_id>[^/.]+)')
    def by_user(self, request, user_id=None):
        print("Organization by_user called with user_id:", user_id)
        orgs = self.get_queryset().filter(created_by=user_id)
        serializer = self.get_serializer(orgs, many=True)
        print("Organizations found:", len(serializer.data))
        return Response(serializer.data)


class CompanyViewSet(viewsets.ModelViewSet):
    queryset = Company.objects.all()
    serializer_class = CompanySerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            print("Company create - Validation Errors:", serializer.errors)
            return Response(serializer.errors, status=400)
        serializer.is_valid(raise_exception=True)
        company = serializer.save()
        print("Company created:", serializer.data)
        return Response({
            'success': True,
            'message': 'Company created successfully.',
            'data': serializer.data
        }, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'], url_path='by-user/(?P<user_id>[^/.]+)')
    def by_user(self, request, user_id=None):
        print("Company by_user called with user_id:", user_id)
        companies = self.get_queryset().filter(created_by=user_id)
        serializer = self.get_serializer(companies, many=True)
        print("Companies found:", len(serializer.data))
        return Response(serializer.data)


class EntityViewSet(viewsets.ModelViewSet):
    queryset = Entity.objects.all()
    serializer_class = EntitySerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            print("Entity create - Validation Errors:", serializer.errors)
            return Response(serializer.errors, status=400)
        serializer.is_valid(raise_exception=True)
        company = serializer.save()
        print("Entity created:", serializer.data)
        return Response({
            'success': True,
            'message': 'Company created successfully.',
            'data': serializer.data
        }, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'], url_path='by-user/(?P<user_id>[^/.]+)')
    def by_user(self, request, user_id=None):
        print("Entity by_user called with user_id:", user_id)
        entities = self.get_queryset().filter(created_by=user_id)
        serializer = self.get_serializer(entities, many=True)
        print("Entities found:", len(serializer.data))
        return Response(serializer.data)


class UserAlloriginazitionINfo(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, user_id):
        print("UserAlloriginazitionINfo GET for user_id:", user_id)
        auth_header = request.META.get("HTTP_AUTHORIZATION")
        headers = {}
        if auth_header:
            headers["Authorization"] = auth_header

        user_url = f'https://konstruct.world/users/{user_id}'
        print("Requesting user service:", user_url)
        try:
            user_response = requests.get(user_url, headers=headers, timeout=2)
            print("User service response status:", user_response.status_code)
            if user_response.status_code != 200:
                print("User not verified:", user_response.text)
                return Response(
                    {"detail": "User not verified."}, status=status.HTTP_404_NOT_FOUND
                )
        except requests.RequestException as e:
            print("User service not reachable:", e)
            return Response(
                {"detail": "User service not reachable."}, status=status.HTTP_503_SERVICE_UNAVAILABLE
            )

        try:
            org = Organization.objects.filter(created_by=user_id)
            companies = Company.objects.filter(created_by=user_id)
            entities = Entity.objects.filter(created_by=user_id)
            print(f"DB: Organizations={org.count()}, Companies={companies.count()}, Entities={entities.count()}")
        except Exception as e:
            print("DB query failed:", e)
            return Response({"detail": "DB query failed."}, status=500)

        try:
            or_serializer = OrganizationSerializer(org, many=True)
            comp_serializer = CompanySerializer(companies, many=True)
            enti_serializer = EntitySerializer(entities, many=True)
        except Exception as e:
            print("Serialization failed:", e)
            return Response({"detail": "Serialization failed."}, status=500)

        data = {
            'organizations': or_serializer.data,
            'companies': comp_serializer.data,
            'entities': enti_serializer.data,
        }
        print("UserAlloriginazitionINfo response data:", data)
        return Response(data)


class UserSpecificOriginzationinfo(APIView):
    def get(self, request, org_id):
        print("UserSpecificOriginzationinfo GET for org_id:", org_id)
        try:
            organization = Organization.objects.get(id=org_id)
        except Organization.DoesNotExist:
            print("Organization DOES NOT EXIST")
            return Response(
                {'ERROR': 'Organization DOES NOT EXIST'},
                status=status.HTTP_404_NOT_FOUND
            )

        companies = Company.objects.filter(organization=organization)
        entities = Entity.objects.filter(company__in=companies)

        org_serializer = OrganizationSerializer(organization)
        comp_serializer = CompanySerializer(companies, many=True)
        enti_serializer = EntitySerializer(entities, many=True)

        data = {
            'organization': org_serializer.data,
            'companies': comp_serializer.data,
            'entities': enti_serializer.data,
        }
        print("UserSpecificOriginzationinfo response data:", data)
        return Response(data, status=status.HTTP_200_OK)


class CompanyInfoWithEntities(APIView):
    def get(self, request, user_id, company_id):
        print(f"CompanyInfoWithEntities GET for user_id: {user_id}, company_id: {company_id}")
        try:
            company = Company.objects.select_related('organization').get(id=company_id)
            organization = company.organization
        except Company.DoesNotExist:
            print("Company DOES NOT EXIST")
            return Response(
                {'ERROR': 'Company DOES NOT EXIST'},
                status=status.HTTP_404_NOT_FOUND
            )

        entities = Entity.objects.filter(company=company)

        company_serializer = CompanySerializer(company)
        organization_serializer = OrganizationSerializer(organization)
        entity_serializer = EntitySerializer(entities, many=True)

        data = {
            'company': company_serializer.data,
            'organization': organization_serializer.data,
            'entities': entity_serializer.data,
        }
        print("CompanyInfoWithEntities response data:", data)
        return Response(data, status=status.HTTP_200_OK)


class EntityInfoWithParents(APIView):
    def get(self, request, user_id, entity_id):
        print(f"EntityInfoWithParents GET for user_id: {user_id}, entity_id: {entity_id}")
        try:
            entity = Entity.objects.select_related('company__organization').get(id=entity_id)
            company = entity.company
            organization = company.organization
        except Entity.DoesNotExist:
            print("Entity DOES NOT EXIST")
            return Response(
                {'ERROR': 'Entity DOES NOT EXIST'},
                status=status.HTTP_404_NOT_FOUND
            )

        entity_serializer = EntitySerializer(entity)
        company_serializer = CompanySerializer(company)
        organization_serializer = OrganizationSerializer(organization)

        data = {
            'entity': entity_serializer.data,
            'company': company_serializer.data,
            'organization': organization_serializer.data,
        }
        print("EntityInfoWithParents response data:", data)
        return Response(data, status=status.HTTP_200_OK)


class OrganizationByUserView(generics.ListAPIView):
    serializer_class = OrganizationSerializer
    def get_queryset(self):
        user_id = self.kwargs.get('user_id')
        print("OrganizationByUserView get_queryset for user_id:", user_id)
        return Organization.objects.filter(created_by=user_id)


class CompanyDetailsByOrganizationId(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        org_id = request.query_params.get('organization_id')
        print("CompanyDetailsByOrganizationId GET for org_id:", org_id)
        if not org_id:
            print("organization_id required")
            return Response({'success': False, 'error': 'organization_id required'}, status=400)
        try:
            organization = Organization.objects.get(id=org_id)
        except Organization.DoesNotExist:
            print("Organization not found")
            return Response({'success': False, 'error': 'Organization not found'}, status=404)
        companies = Company.objects.filter(organization=organization)
        serializer = CompanySerializer(companies, many=True)
        print("Companies in organization:", len(serializer.data))
        return Response({'success': True, 'data': {'company': serializer.data}})


from rest_framework.permissions import IsAuthenticated

PROJECT_SERVICE_URL = "https://konstruct.world/projects/"
ORG_SERVICE_URL = "https://konstruct.world/organizations/"
USER_SERVICE_URL = "https://konstruct.world/users/"
CHECKLIST_SERVICE_URL = "https://konstruct.world/checklists/"

class DashboardAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        headers = {"Authorization": request.headers.get("Authorization", "")}
        data = {}
        print("DashboardAPIView GET for user:", user.id, "staff:", user.is_staff, "client:", getattr(user, "is_client", False))
        try:
            if user.is_staff:
                print("Fetching all users")
                users_res = requests.get(f"{USER_SERVICE_URL}/users/", headers=headers, timeout=3)
                users = users_res.json()
                data["all_users_count"] = len(users)

                print("Fetching all clients")
                clients_res = requests.get(f"{USER_SERVICE_URL}/users/?is_client=true", headers=headers, timeout=3)
                clients = clients_res.json()
                data["all_clients_count"] = len(clients)

                print("Fetching all projects")
                proj_res = requests.get(f"{PROJECT_SERVICE_URL}/projects/", headers=headers, timeout=3)
                projects = proj_res.json()
                data["all_projects_count"] = len(projects)

                print("Fetching all organizations")
                org_res = requests.get(f"{ORG_SERVICE_URL}/organizations/", headers=headers, timeout=3)
                organizations = org_res.json()
                data["all_organizations_count"] = len(organizations)

                print("Fetching all checklists")
                checklist_res = requests.get(f"{CHECKLIST_SERVICE_URL}/checklists/", headers=headers, timeout=3)
                checklists = checklist_res.json()
                data["all_checklists_count"] = len(checklists)

                data["recent_projects"] = projects[-5:] if len(projects) > 5 else projects
                data["recent_checklists"] = checklists[-5:] if len(checklists) > 5 else checklists

            elif getattr(user, "is_client", False):
                print("Fetching client projects and checklists for user", user.id)
                proj_res = requests.get(f"{PROJECT_SERVICE_URL}/projects/?created_by={user.id}", headers=headers, timeout=3)
                projects = proj_res.json()
                data["my_projects_count"] = len(projects)
                data["my_projects"] = projects

                checklist_res = requests.get(f"{CHECKLIST_SERVICE_URL}/checklists/?created_by={user.id}", headers=headers, timeout=3)
                checklists = checklist_res.json()
                data["my_checklists_count"] = len(checklists)
                data["my_checklists"] = checklists

                if getattr(user, "org", None):
                    org_res = requests.get(f"{ORG_SERVICE_URL}/organizations/{user.org}/", headers=headers, timeout=3)
                    if org_res.status_code == 200:
                        data["my_organization"] = org_res.json()

            else:
                print("Fetching access for user", user.id)
                access_res = requests.get(f"{USER_SERVICE_URL}/user-access/?user_id={user.id}", headers=headers, timeout=3)
                accesses = access_res.json()
                data["accesses"] = accesses
        except Exception as e:
            print("DashboardAPIView error:", e)
            return Response({"error": str(e)}, status=500)

        print("DashboardAPIView response data:", data)
        return Response(data)
