# Formik Patterns EXTEND.md

## 默认 Formik 配置

---

## 自定义表单初始化 (Custom Form Initialization)

### controlled-form
- mode: controlled
- initialValues: empty
- validation: on_blur
- enable_reinitialize: false

### uncontrolled-form
- mode: uncontrolled
- initialValues: populated
- validation: on_submit
- enable_reinitialize: true

### hybrid-form
- mode: hybrid
- initialValues: partially_populated
- validation: on_change
- enable_reinitialize: true

---

## 自定义验证策略 (Custom Validation Strategy)

### inline-validation
- trigger: on_change
- feedback: immediate
- error_display: inline
- touch_behavior: mark_touched

### blur-validation
- trigger: on_blur
- feedback: on_field_exit
- error_display: inline
- touch_behavior: standard

### submit-validation
- trigger: on_submit
- feedback: on_form_submit
- error_display: summary
- touch_behavior: lazy

### schema-validation
- library: yup
- validation: schema_based
- error_display: field_level
- touch_behavior: validate_on_blur

---

## 自定义字段类型 (Custom Field Types)

### text-input
- component: Input
- validation: [required, min_length, max_length, pattern]
- formatting: trim
- placeholder: enabled

### number-input
- component: InputNumber
- validation: [required, min, max]
- formatting: number
- placeholder: enabled

### email-input
- component: Input
- validation: [required, email]
- formatting: lowercase
- placeholder: enabled

### password-input
- component: Input.Password
- validation: [required, min_length]
- formatting: none
- placeholder: enabled

### select-input
- component: Select
- validation: [required]
- options: array_or_function
- placeholder: enabled

### multi-select
- component: Select (multi)
- validation: [required, min_items]
- options: array_or_function
- placeholder: enabled

### checkbox-group
- component: Checkbox
- validation: none
- options: array
- inline: true

### radio-group
- component: Radio
- validation: [required]
- options: array
- inline: true

### date-picker
- component: DatePicker
- validation: [required]
- format: date
- placeholder: enabled

### textarea
- component: Input.TextArea
- validation: [required, min_length, max_length]
- rows: 4
- resize: vertical

### rich-editor
- component: RichTextEditor
- validation: [required, min_length]
- toolbar: full
- upload: enabled

### file-upload
- component: Upload
- validation: [required, file_types, max_size]
- multiple: false
- upload_handler: custom

---

## 自定义表单布局 (Custom Form Layout)

### vertical-layout
- direction: column
- spacing: standard
- labels: top
- responsive: stacked

### horizontal-layout
- direction: row
- spacing: compact
- labels: left
- responsive: stacked_mobile

### inline-layout
- direction: inline
- spacing: minimal
- labels: hidden
- responsive: forced_inline

### grid-layout
- direction: grid
- columns: 2-4
- spacing: standard
- labels: top
- responsive: responsive_columns

---

## 自定义错误处理 (Custom Error Handling)

### inline-errors
- display: field_level
- style: red_text
- position: below_field
- scroll: none

### tooltip-errors
- display: tooltip
- style: icon
- position: field_position
- scroll: none

### summary-errors
- display: top_of_form
- style: error_list
- position: form_top
- scroll: to_errors

### dialog-errors
- display: modal
- style: error_dialog
- position: center_screen
- scroll: none

---

## 自定义提交处理 (Custom Submission Handling)

### ajax-submit
- method: asynchronous
- feedback: loading_state
- redirect: none
- reset_on_success: false

### form-submit
- method: synchronous
- feedback: page_navigation
- redirect: success_page
- reset_on_success: true

### multipart-submit
- method: multipart
- feedback: progress_bar
- redirect: success_page
- reset_on_success: true

---

## 自定义加载状态 (Custom Loading States)

### spinner-loading
- type: spinner
- position: replace_button
- text: "Submitting..."
- disable_form: true

### button-loading
- type: button_state
- position: inline
- text: "Submitting..."
- disable_form: true

### overlay-loading
- type: overlay
- position: form_center
- text: "Submitting..."
- disable_form: true

### skeleton-loading
- type: skeleton
- position: field_level
- text: none
- disable_form: false

---

## 自定义字段样式 (Custom Field Styling)

### default-style
- border: 1px solid #ddd
- radius: 4px
- padding: 8px 12px
- focus: primary_color
- error: error_color

### material-style
- border: none
- radius: 4px_bottom
- padding: 8px 0
- focus: primary_color
- error: error_color
- animated: true

### outline-style
- border: none
- radius: none
- padding: 8px 12px
- focus: primary_border
- error: error_border
- underline: animated

---

## 自定义条件渲染 (Custom Conditional Rendering)

### field-visibility
- based_on: other_fields
- logic: dependent_logic
- evaluation: real_time
- performance: optimized

### field-availability
- based_on: user_role
- logic: permission_based
- evaluation: on_mount
- performance: cached

### field-requirements
- based_on: form_state
- logic: conditional_rules
- evaluation: dynamic
- performance: reactive

---

## 自定义多步骤表单 (Custom Multi-Step Form)

### linear-steps
- navigation: sequential
- validation: per_step
- progress: linear
- completion: all_steps_required

### wizard-steps
- navigation: guided
- validation: per_step
- progress: percentage
- completion: all_steps_required

### branching-steps
- navigation: conditional
- validation: per_step
- progress: dynamic
- completion: required_steps_only

---

## 自定义重置策略 (Custom Reset Strategy)

### soft-reset
- trigger: user_action
- clear: values_only
- retain: touched_state
- validation: cleared

### hard-reset
- trigger: form_unmount
- clear: all_state
- retain: none
- validation: cleared

### manual-reset
- trigger: reset_button
- clear: configurable
- retain: touched_state
- validation: configurable

---

## 配置优先级

```
CLI参数 > 项目级EXTEND.md > 用户级EXTEND.md > 默认配置
```

- **项目级**: `.claude/skills/formik-patterns/EXTEND.md`
- **用户级**: `~/.claude/skills/formik-patterns/EXTEND.md`
- **默认级**: `skills/formik-patterns/EXTEND.md`

---

## 使用示例

### 简单联系表单
```markdown
## Simple Contact Form

### contact-form
- initialization: controlled-form
- validation: blur-validation
- fields: [text-input, email-input, textarea]
- layout: vertical-layout
- errors: inline-errors
- submission: ajax-submit
- loading: spinner-loading
- style: default-style
- conditional: none
- multi_step: false
- reset: soft-reset
```

### 用户注册表单
```markdown
## User Registration Form

### registration-form
- initialization: controlled-form
- validation: schema-validation
- fields: [text-input, email-input, password-input, checkbox-group]
- layout: vertical-layout
- errors: summary-errors + inline-errors
- submission: ajax-submit
- loading: button-loading
- style: material-style
- conditional: field-visibility
- multi_step: false
- reset: hard-reset
```

### 多步骤向导
```markdown
### Multi-Step Wizard

### wizard-form
- initialization: controlled-form
- validation: schema-validation + blur-validation
- fields: all_field_types
- layout: grid-layout
- errors: tooltip-errors
- submission: ajax-submit
- loading: overlay-loading
- style: default-style
- conditional: field-availability
- multi_step: wizard-steps
- reset: manual-reset
```

### 动态调查表单
```markdown
### Dynamic Survey Form

### survey-form
- initialization: hybrid-form
- validation: inline-validation
- fields: conditional_fields
- layout: vertical-layout
- errors: inline-errors
- submission: ajax-submit
- loading: skeleton-loading
- style: outline-style
- conditional: field-visibility + field-requirements
- multi_step: branching-steps
- reset: soft-reset
```
