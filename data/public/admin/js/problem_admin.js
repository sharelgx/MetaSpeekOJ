(function($) {
    'use strict';
    
    $(document).ready(function() {
        // 题目类型字段
        var problemTypeField = $('#id_problem_type');
        var choiceTemplateFieldset = $('.field-choice_template').closest('.form-row').parent();
        
        // 初始化显示状态
        toggleChoiceFields();
        
        // 监听题目类型变化
        problemTypeField.change(function() {
            toggleChoiceFields();
        });
        
        function toggleChoiceFields() {
            var problemType = problemTypeField.val();
            
            if (problemType === 'Choice') {
                // 选择题类型
                choiceTemplateFieldset.show();
                
                // 添加提示信息
                if (!$('#choice-type-notice').length) {
                    var notice = $('<div id="choice-type-notice" class="help" style="color: #0066cc; margin: 10px 0;">' +
                        '<strong>提示：</strong>您选择了选择题类型，请：<br>' +
                        '1. 使用下方的选择题模板创建题目描述<br>' +
                        '2. 保存后在选择题选项中添加具体选项<br>' +
                        '3. 编程相关字段（如时间限制、内存限制等）对选择题无效' +
                        '</div>');
                    choiceTemplateFieldset.before(notice);
                }
                
                // 隐藏编程题相关字段
                $('.field-time_limit, .field-memory_limit, .field-languages, .field-template').closest('.form-row').hide();
                $('.field-test_case_id, .field-test_case_score, .field-samples').closest('.form-row').hide();
                $('fieldset').filter(function() {
                    return $(this).find('legend').text().indexOf('特殊判题') !== -1;
                }).hide();
                
            } else {
                // 编程题类型
                choiceTemplateFieldset.hide();
                $('#choice-type-notice').remove();
                
                // 显示编程题相关字段
                $('.field-time_limit, .field-memory_limit, .field-languages, .field-template').closest('.form-row').show();
                $('.field-test_case_id, .field-test_case_score, .field-samples').closest('.form-row').show();
                $('fieldset').filter(function() {
                    return $(this).find('legend').text().indexOf('特殊判题') !== -1;
                }).show();
            }
        }
        
        // 选择题模板复制功能
        var choiceTemplateField = $('#id_choice_template');
        var descriptionField = $('#id_description');
        
        if (choiceTemplateField.length && descriptionField.length) {
            var copyButton = $('<button type="button" class="btn btn-sm btn-secondary" style="margin-left: 10px;">复制到题目描述</button>');
            choiceTemplateField.after(copyButton);
            
            copyButton.click(function() {
                var template = choiceTemplateField.val();
                if (template) {
                    // 如果使用富文本编辑器
                    if (typeof CKEDITOR !== 'undefined' && CKEDITOR.instances.id_description) {
                        CKEDITOR.instances.id_description.setData(template);
                    } else {
                        descriptionField.val(template);
                    }
                    alert('模板已复制到题目描述中！');
                } else {
                    alert('模板内容为空！');
                }
            });
        }
    });
    
})(django.jQuery);