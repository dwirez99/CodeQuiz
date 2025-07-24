// Code Editor Admin JavaScript

(function($) {
    'use strict';

    // Initialize code editors when DOM is ready
    $(document).ready(function() {
        initializeCodeEditors();
        initializeTestCaseHelpers();
        initializeFormValidation();
    });

    // Initialize Ace editors for code fields
    function initializeCodeEditors() {
        $('.code-editor').each(function() {
            const textarea = this;
            const $textarea = $(textarea);
            const mode = $textarea.data('mode') || 'python';
            
            // Create editor container
            const editorId = 'ace-editor-' + Math.random().toString(36).substr(2, 9);
            const $editorDiv = $('<div>').attr('id', editorId).addClass('ace-editor-container');
            
            // Insert editor div after textarea and hide textarea
            $textarea.after($editorDiv).hide();
            
            // Initialize Ace editor
            const editor = ace.edit(editorId);
            editor.setTheme('ace/theme/monokai');
            editor.session.setMode('ace/mode/' + mode);
            editor.setFontSize(14);
            editor.setOptions({
                enableLiveAutocompletion: true,
                enableSnippets: true,
                showPrintMargin: false,
                highlightActiveLine: true,
                wrap: true
            });
            
            // Set initial value
            editor.setValue($textarea.val(), -1);
            
            // Sync editor content with textarea
            editor.session.on('change', function() {
                $textarea.val(editor.getValue());
                $textarea.trigger('change');
            });
            
            // Handle form submission
            $textarea.closest('form').on('submit', function() {
                $textarea.val(editor.getValue());
            });
            
            // Store editor reference
            $textarea.data('ace-editor', editor);
            
            // Set appropriate height
            const minHeight = $textarea.attr('rows') ? parseInt($textarea.attr('rows')) * 20 : 300;
            $editorDiv.height(minHeight);
            editor.resize();
        });
    }

    // Initialize test case helper functions
    function initializeTestCaseHelpers() {
        // Add test case validation
        $('.inline-related').each(function() {
            const $inline = $(this);
            const $inputField = $inline.find('textarea[name*="input_data"]');
            const $outputField = $inline.find('textarea[name*="expected_output"]');
            
            if ($inputField.length && $outputField.length) {
                // Add validation on blur
                $inputField.add($outputField).on('blur', function() {
                    validateTestCase($inline);
                });
                
                // Add copy button for test cases
                addCopyButton($inputField, 'Copy Input');
                addCopyButton($outputField, 'Copy Output');
            }
        });
        
        // Add "Add Test Case" helper
        $('.add-row a').on('click', function() {
            setTimeout(function() {
                initializeNewTestCaseRow();
            }, 100);
        });
    }

    // Validate test case data
    function validateTestCase($inline) {
        const $inputField = $inline.find('textarea[name*="input_data"]');
        const $outputField = $inline.find('textarea[name*="expected_output"]');
        const $sampleField = $inline.find('input[name*="is_sample"]');
        
        // Clear previous validation
        $inline.removeClass('has-error has-warning');
        $inline.find('.validation-message').remove();
        
        const input = $inputField.val().trim();
        const output = $outputField.val().trim();
        const isSample = $sampleField.is(':checked');
        
        let messages = [];
        
        // Check if both input and output are provided
        if (input && !output) {
            messages.push('Expected output is required when input is provided');
            $inline.addClass('has-error');
        } else if (!input && output) {
            messages.push('Input is required when expected output is provided');
            $inline.addClass('has-error');
        }
        
        // Warn about sample test cases
        if (isSample && (!input || !output)) {
            messages.push('Sample test cases should have both input and output');
            $inline.addClass('has-warning');
        }
        
        // Display validation messages
        if (messages.length > 0) {
            const $messageDiv = $('<div class="validation-message"></div>');
            messages.forEach(function(message) {
                $messageDiv.append('<p class="text-danger">' + message + '</p>');
            });
            $inline.append($messageDiv);
        }
    }

    // Add copy button to text areas
    function addCopyButton($textarea, label) {
        const $copyBtn = $('<button type="button" class="btn btn-sm btn-outline-secondary copy-btn">')
            .text(label)
            .css({
                'position': 'absolute',
                'top': '5px',
                'right': '5px',
                'z-index': '10',
                'font-size': '10px',
                'padding': '2px 6px'
            });
        
        $textarea.parent().css('position', 'relative').append($copyBtn);
        
        $copyBtn.on('click', function() {
            const text = $textarea.val();
            if (navigator.clipboard) {
                navigator.clipboard.writeText(text).then(function() {
                    showCopyFeedback($copyBtn);
                });
            } else {
                // Fallback for older browsers
                $textarea.select();
                document.execCommand('copy');
                showCopyFeedback($copyBtn);
            }
        });
    }

    // Show copy feedback
    function showCopyFeedback($btn) {
        const originalText = $btn.text();
        $btn.text('Copied!').addClass('btn-success').removeClass('btn-outline-secondary');
        setTimeout(function() {
            $btn.text(originalText).removeClass('btn-success').addClass('btn-outline-secondary');
        }, 1500);
    }

    // Initialize new test case row
    function initializeNewTestCaseRow() {
        const $newRow = $('.inline-related:last');
        const $inputField = $newRow.find('textarea[name*="input_data"]');
        const $outputField = $newRow.find('textarea[name*="expected_output"]');
        
        if ($inputField.length && $outputField.length) {
            $inputField.add($outputField).on('blur', function() {
                validateTestCase($newRow);
            });
            
            addCopyButton($inputField, 'Copy Input');
            addCopyButton($outputField, 'Copy Output');
        }
    }

    // Initialize form validation
    function initializeFormValidation() {
        // Add real-time validation for required fields
        $('form').on('submit', function(e) {
            let hasErrors = false;
            
            // Validate code fields
            $('.code-editor').each(function() {
                const $textarea = $(this);
                const editor = $textarea.data('ace-editor');
                const isRequired = $textarea.attr('required') || $textarea.hasClass('required');
                
                if (isRequired && editor && !editor.getValue().trim()) {
                    hasErrors = true;
                    showFieldError($textarea, 'This field is required');
                } else {
                    clearFieldError($textarea);
                }
            });
            
            // Validate test cases
            $('.inline-related').each(function() {
                validateTestCase($(this));
                if ($(this).hasClass('has-error')) {
                    hasErrors = true;
                }
            });
            
            if (hasErrors) {
                e.preventDefault();
                showFormErrors();
            }
        });
    }

    // Show field error
    function showFieldError($field, message) {
        $field.addClass('field-error');
        $field.next('.ace-editor-container').addClass('field-error');
        
        const $errorDiv = $field.siblings('.field-error-message');
        if ($errorDiv.length === 0) {
            $('<div class="field-error-message text-danger">' + message + '</div>')
                .insertAfter($field.next('.ace-editor-container'));
        }
    }

    // Clear field error
    function clearFieldError($field) {
        $field.removeClass('field-error');
        $field.next('.ace-editor-container').removeClass('field-error');
        $field.siblings('.field-error-message').remove();
    }

    // Show form errors summary
    function showFormErrors() {
        const $errorSummary = $('.form-error-summary');
        if ($errorSummary.length === 0) {
            $('<div class="form-error-summary alert alert-danger">')
                .html('<strong>Please correct the following errors:</strong><ul>' +
                      '<li>Check required fields are filled</li>' +
                      '<li>Ensure test cases have valid input/output pairs</li>' +
                      '</ul>')
                .prependTo('.content');
        }
        
        // Scroll to first error
        const $firstError = $('.field-error, .has-error').first();
        if ($firstError.length) {
            $('html, body').animate({
                scrollTop: $firstError.offset().top - 100
            }, 500);
        }
    }

    // Language-specific code templates
    const codeTemplates = {
        python: {
            starter: '# Write your solution here\ndef solution():\n    pass\n\n# Test your solution\nif __name__ == "__main__":\n    result = solution()\n    print(result)',
            test: '# Test case\ninput_data = ""\nexpected_output = ""\n\n# Your solution here\ndef solution():\n    pass\n\nresult = solution()\nprint(result)'
        },
        java: {
            starter: 'public class Solution {\n    public static void main(String[] args) {\n        // Write your solution here\n    }\n}',
            test: 'import java.util.*;\n\npublic class Solution {\n    public static void main(String[] args) {\n        Scanner scanner = new Scanner(System.in);\n        // Read input and solve\n    }\n}'
        },
        cpp: {
            starter: '#include <iostream>\nusing namespace std;\n\nint main() {\n    // Write your solution here\n    return 0;\n}',
            test: '#include <iostream>\n#include <vector>\n#include <string>\nusing namespace std;\n\nint main() {\n    // Read input and solve\n    return 0;\n}'
        }
    };

    // Add template buttons
    function addTemplateButtons() {
        $('.code-editor').each(function() {
            const $textarea = $(this);
            const $container = $textarea.next('.ace-editor-container');
            const mode = $textarea.data('mode') || 'python';
            
            if (codeTemplates[mode]) {
                const $toolbar = $('<div class="code-toolbar"></div>');
                
                Object.keys(codeTemplates[mode]).forEach(function(templateType) {
                    const $btn = $('<button type="button" class="btn btn-sm btn-outline-info">')
                        .text('Insert ' + templateType + ' template')
                        .on('click', function() {
                            const editor = $textarea.data('ace-editor');
                            if (editor) {
                                editor.setValue(codeTemplates[mode][templateType], -1);
                            }
                        });
                    $toolbar.append($btn);
                });
                
                $container.before($toolbar);
            }
        });
    }

    // Initialize template buttons after editors are ready
    $(document).ready(function() {
        setTimeout(addTemplateButtons, 500);
    });

    // Export functions for global access
    window.CodeEditorAdmin = {
        initializeCodeEditors: initializeCodeEditors,
        validateTestCase: validateTestCase,
        codeTemplates: codeTemplates
    };

})(django.jQuery);
