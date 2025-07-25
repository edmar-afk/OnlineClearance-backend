# serializers.py
from rest_framework import serializers
from .models import Programs, Signature, Student, Clearance, StudentClearance, ClearanceSignature
from django.contrib.auth.models import User

        
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'is_staff', 'is_superuser']
        
class StudentSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = Student
        fields = ['user', 'year_level', 'major']
        
class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    first_name = serializers.CharField(required=True)
    year_level = serializers.CharField(write_only=True)
    major = serializers.CharField(write_only=True, allow_blank=True, required=False)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'first_name', 'last_name', 'year_level', 'major']

    def create(self, validated_data):

        year_level = validated_data.pop('year_level')
        major = validated_data.pop('major', '')

        user = User.objects.create_user(**validated_data)
        Student.objects.create(user=user, year_level=year_level, major=major)
        return user

    
class ProgramsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Programs
        fields = '__all__'



class SignatureSerializer(serializers.ModelSerializer):
    class Meta:
        model = Signature
        fields = ['id', 'staff', 'image']

    def create(self, validated_data):
        staff = validated_data.get("staff")

        # Delete existing signature for this staff
        existing_signature = Signature.objects.filter(staff=staff).first()
        if existing_signature:
            existing_signature.image.delete(save=False)
            existing_signature.delete()

        return super().create(validated_data)



class ClearanceSerializer(serializers.ModelSerializer):
    programs = ProgramsSerializer(many=True)

    class Meta:
        model = Clearance
        fields = ['id', 'programs', 'created_at', 'updated_at', 'semester', 'academic_year']

        

class ClearanceCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Clearance
        fields = ['id', 'semester', 'academic_year']

    def create(self, validated_data):
        clearance = Clearance.objects.create(**validated_data)
        all_programs = Programs.objects.all()
        clearance.programs.set(all_programs)
        return clearance


class StudentClearanceSerializer(serializers.ModelSerializer):
    student = UserSerializer()  # 👈 
    clearance = ClearanceSerializer()

    class Meta:
        model = StudentClearance
        fields = '__all__'
        read_only_fields = ['status']



class ClearanceSignatureSerializer(serializers.ModelSerializer):
    student = UserSerializer()  # 👈 
    programs = ProgramsSerializer()
    signature = SignatureSerializer()
    clearance = StudentClearanceSerializer()
    class Meta:
        model = ClearanceSignature
        fields = '__all__'