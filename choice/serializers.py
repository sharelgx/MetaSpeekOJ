from rest_framework import serializers
from .models import ChoiceProblem, ChoiceOption
from account.serializers import UserSerializer


class ChoiceOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChoiceOption
        fields = ['id', 'content', 'is_correct', 'sequence']


class ChoiceProblemSerializer(serializers.ModelSerializer):
    created_by = UserSerializer(read_only=True)
    options = ChoiceOptionSerializer(many=True, read_only=True)
    create_time = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S', read_only=True)
    last_update_time = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S', read_only=True)
    
    # 为前端兼容性添加字段
    display_id = serializers.CharField(source='_id', read_only=True)
    choices = serializers.SerializerMethodField()
    answer = serializers.SerializerMethodField()
    hint = serializers.CharField(source='explanation', read_only=True)
    
    class Meta:
        model = ChoiceProblem
        fields = ['id', 'display_id', '_id', 'title', 'description', 'difficulty', 
                 'visible', 'create_time', 'last_update_time', 'created_by', 
                 'submission_number', 'correct_number', 'is_multiple', 'explanation',
                 'options', 'choices', 'answer', 'hint']
    
    def get_choices(self, obj):
        """获取选项列表，格式化为前端需要的格式"""
        options = obj.options.all().order_by('sequence')
        return [{'text': option.content} for option in options]
    
    def get_answer(self, obj):
        """获取正确答案，返回字母形式"""
        correct_option = obj.options.filter(is_correct=True).first()
        if correct_option:
            return chr(64 + correct_option.sequence)  # A, B, C, D...
        return 'A'


class CreateChoiceProblemSerializer(serializers.Serializer):
    display_id = serializers.CharField(max_length=128)
    title = serializers.CharField(max_length=1024)
    description = serializers.CharField()
    difficulty = serializers.ChoiceField(choices=['Low', 'Mid', 'High'])
    visible = serializers.BooleanField(default=True)
    choices = serializers.ListField(
        child=serializers.DictField(child=serializers.CharField()),
        min_length=2,
        max_length=10
    )
    answer = serializers.CharField(max_length=1)
    hint = serializers.CharField(required=False, allow_blank=True)
    is_multiple = serializers.BooleanField(default=False)
    contest_id = serializers.IntegerField(required=False)
    
    def validate_choices(self, value):
        """验证选项"""
        for choice in value:
            if 'text' not in choice or not choice['text'].strip():
                raise serializers.ValidationError("Choice text cannot be empty")
        return value
    
    def validate_answer(self, value):
        """验证答案"""
        if not value or not value.isalpha() or len(value) != 1:
            raise serializers.ValidationError("Answer must be a single letter")
        return value.upper()


class EditChoiceProblemSerializer(CreateChoiceProblemSerializer):
    id = serializers.IntegerField()
    display_id = serializers.CharField(max_length=128, required=False)