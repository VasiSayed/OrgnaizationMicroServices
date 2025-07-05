from rest_framework import viewsets,permissions
from .models import Organization, Company, Entity
from .serializers import OrganizationSerializer, CompanySerializer, EntitySerializer
from rest_framework.decorators import action
from rest_framework.views import APIView
from rest_framework.response import Response
import requests
from rest_framework import status
from rest_framework import generics

class OrganizationViewSet(viewsets.ModelViewSet):
    queryset = Organization.objects.all()
    serializer_class = OrganizationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            print("Validation Errors:", serializer.errors)
            return Response(serializer.errors, status=400)
        self.perform_create(serializer)
        return Response(serializer.data, status=201)

    @action(detail=False, methods=['get'], url_path='by-user/(?P<user_id>[^/.]+)')
    def by_user(self, request, user_id=None):
        orgs = self.get_queryset().filter(created_by=user_id)
        serializer = self.get_serializer(orgs, many=True)
        return Response(serializer.data)
    

class CompanyViewSet(viewsets.ModelViewSet):
    queryset = Company.objects.all()
    serializer_class = CompanySerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            print("Validation Errors:", serializer.errors)
            return Response(serializer.errors, status=400)
        serializer.is_valid(raise_exception=True)
        company = serializer.save()
        return Response({
            'success': True,
            'message': 'Company created successfully.',
            'data': serializer.data
        }, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'], url_path='by-user/(?P<user_id>[^/.]+)')
    def by_user(self, request, user_id=None):
        companies = self.get_queryset().filter(created_by=user_id)
        serializer = self.get_serializer(companies, many=True)
        return Response(serializer.data)


class EntityViewSet(viewsets.ModelViewSet):
    queryset = Entity.objects.all()
    serializer_class = EntitySerializer
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=False, methods=['get'], url_path='by-user/(?P<user_id>[^/.]+)')
    def by_user(self, request, user_id=None):
        entities = self.get_queryset().filter(created_by=user_id)
        serializer = self.get_serializer(entities, many=True)
        return Response(serializer.data)
    

class UserAlloriginazitionINfo(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, user_id):
        auth_header = request.META.get("HTTP_AUTHORIZATION")
        headers = {}
        if auth_header:
            headers["Authorization"] = auth_header

        user_url = f'http://127.0.0.1:8000/api/users/{user_id}'
        try:
            user_response = requests.get(user_url, headers=headers, timeout=2)
            if user_response.status_code != 200:
                return Response(
                    {"detail": "User not verified."}, status=status.HTTP_404_NOT_FOUND
                )
        except requests.RequestException:
            return Response(
                {"detail": "User service not reachable."}, status=status.HTTP_503_SERVICE_UNAVAILABLE
            )

        org = Organization.objects.filter(created_by=user_id)
        companies = Company.objects.filter(created_by=user_id)
        entities = Entity.objects.filter(created_by=user_id)

        or_serializer = OrganizationSerializer(org, many=True)
        comp_serializer = CompanySerializer(companies, many=True)
        enti_serializer = EntitySerializer(entities, many=True)

        data = {
            'organizations': or_serializer.data,
            'companies': comp_serializer.data,
            'entities': enti_serializer.data,
        }
        return Response(data)

    
class UserSpecificOriginzationinfo(APIView):
    def get(self, request, org_id):
        # user_url = f'http://127.0.0.1:8000/api/users/{user_id}'
        # try:
        #     user_response = requests.get(user_url, timeout=2)
        #     if user_response.status_code != 200:
        #         return Response(
        #             {"detail": "User not verified."},
        #             status=status.HTTP_404_NOT_FOUND
        #         )
        # except requests.RequestException:
        #     return Response(
        #         {"detail": "User service not reachable."},
        #         status=status.HTTP_503_SERVICE_UNAVAILABLE
        #     )
        try:
            organization = Organization.objects.get(id=org_id)
        except Organization.DoesNotExist:
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
        return Response(data, status=status.HTTP_200_OK)
    

class CompanyInfoWithEntities(APIView):
    def get(self, request, user_id, company_id):
        # user_url = f'http://127.0.0.1:8000/api/users/{user_id}'
        # try:
        #     user_response = requests.get(user_url, timeout=2)
        #     if user_response.status_code != 200:
        #         return Response(
        #             {"detail": "User not verified."},
        #             status=status.HTTP_404_NOT_FOUND
        #         )
        # except requests.RequestException:
        #     return Response(
        #         {"detail": "User service not reachable."},
        #         status=status.HTTP_503_SERVICE_UNAVAILABLE
        #     )
        try:
            company = Company.objects.select_related('organization').get(id=company_id)
            organization = company.organization
        except Company.DoesNotExist:
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
        return Response(data, status=status.HTTP_200_OK)
    

class EntityInfoWithParents(APIView):
    def get(self, request, user_id, entity_id):

        try:
            entity = Entity.objects.select_related('company__organization').get(id=entity_id)
            company = entity.company
            organization = company.organization
        except Entity.DoesNotExist:
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
        return Response(data, status=status.HTTP_200_OK)


class OrganizationByUserView(generics.ListAPIView):
    serializer_class = OrganizationSerializer
    def get_queryset(self):
        user_id = self.kwargs.get('user_id')
        return Organization.objects.filter(created_by=user_id)
    

class CompanyDetailsByOrganizationId(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        org_id = request.query_params.get('organization_id')
        if not org_id:
            return Response({'success': False, 'error': 'organization_id required'}, status=400)
        try:
            organization = Organization.objects.get(id=org_id)
        except Organization.DoesNotExist:
            return Response({'success': False, 'error': 'Organization not found'}, status=404)
        companies = Company.objects.filter(organization=organization)
        serializer = CompanySerializer(companies, many=True)
        return Response({'success': True, 'data': {'company': serializer.data}})