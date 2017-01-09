import React, {PropTypes, Component} from 'react';
import warning from 'warning';
import {getDisplayForValue} from 'common/array.js';
import TextField from 'common/ui/TextField';
import CheckBox from 'common/ui/CheckBox';
import Textarea from 'common/ui/Textarea';
import DateField from 'common/ui/DateField';
import Select from 'common/ui/Select';
import FieldWrapper from 'common/ui/FieldWrapper';
import TagSelect from 'common/ui/tags/TagSelect';
import DateTimePicker from 'common/ui/DateTimePicker';

export default class RemoteFormField extends Component {
  render() {
    const {fieldName, form, value, onChange,
      tagActions, selectedTags, availableTags} = this.props;
    const field = form.fields[fieldName] || {};
    const errors = (form.errors || {})[fieldName];
    const fieldDisable = field.readonly;

    function wrap(child) {
      return (
        <FieldWrapper
          label={field.label}
          helpText={field.help_text}
          errors={errors}
          required={field.required}>
          {child}
        </FieldWrapper>
      );
    }

    const inputType = (field.widget || {}).input_type || 'unspecified';

    switch (inputType) {
    case 'time':
    case 'text':
      return wrap(
        <TextField
          name={fieldName}
          onChange={e => onChange(e, fieldName)}
          required={field.required}
          value={value}
          maxLength={field.widget.maxlength}
          isHidden={field.widget.is_hidden}
          placeholder={field.widget.attrs.placeholder}
          autoFocus={field.widget.attrs.autofocus}
          disable={fieldDisable}
          />
      );
    case 'textarea':
      return wrap(
        <Textarea
          name={fieldName}
          onChange={e => onChange(e, fieldName)}
          required={field.required}
          initial={field.initial}
          maxLength={field.widget.maxlength}
          isHidden={field.widget.is_hidden}
          placeholder={field.widget.attrs.placeholder}
          autoFocus={field.widget.attrs.autofocus}
          disable={fieldDisable}
          />
      );
    case 'date':
      return wrap(
        <DateField
          name={fieldName}
          onChange={e => onChange(e, fieldName)}
          required={field.required}
          value={value}
          maxLength={field.widget.maxlength}
          isHidden={field.widget.is_hidden}
          placeholder={field.widget.attrs.placeholder}
          autoFocus={field.widget.attrs.autofocus}
          numberOfYears={50}
          disable={fieldDisable}
          pastOnly
          />
      );
    case 'select':
      return wrap(
        <Select
          name={fieldName}
          onChange={e => onChange(e, fieldName)}
          value={getDisplayForValue(field.choices, value)}
          choices={field.choices}
          disable={fieldDisable}
          />
      );
    case 'checkbox':
      return wrap(
        <CheckBox
          name={fieldName}
          onChange={e => onChange(e, fieldName)}
          required={field.required}
          initial={field.initial}
          maxLength={field.widget.maxlength}
          isHidden={field.widget.is_hidden}
          placeholder={field.widget.attrs.placeholder}
          autoFocus={field.widget.attrs.autofocus}
          disable={fieldDisable}
          />
      );
    case 'selectmultiple':
      return wrap(
          <TagSelect
          name={fieldName}
          onChoose={(tags) => tagActions('select', tags)}
          onRemove={(tags) => tagActions('remove', tags)}
          required={field.required}
          selected={selectedTags || []}
          available={availableTags || []}
          maxLength={field.widget.maxlength}
          isHidden={field.widget.is_hidden}
          placeholder={field.widget.attrs.placeholder}
          autoFocus={field.widget.attrs.autofocus}
          onNew={(tags) => tagActions('new', tags)}
          />
      );
    case 'datetime':
      return wrap(
        <DateTimePicker
          onChange={e => onChange(e, fieldName)}
          value={value}
          />
      );
    default:
      warning(false, `Unknown field type for ${fieldName}: ${inputType}`);
      return <span/>;
    }
  }
}

RemoteFormField.propTypes = {
  form: PropTypes.object.isRequired,
  fieldName: PropTypes.string.isRequired,
  value: PropTypes.any.isRequired,
  onChange: PropTypes.func.isRequired,
  tagActions: PropTypes.func,
  availableTags: PropTypes.arrayOf(
    PropTypes.shape({
      value: PropTypes.any.isRequired,
      display: PropTypes.string.isRequired,
    }).isRequired
  ),
  selectedTags: PropTypes.arrayOf(
    PropTypes.shape({
      value: PropTypes.any.isRequired,
      display: PropTypes.string.isRequired,
    }).isRequired
  ),
};
