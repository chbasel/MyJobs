import React, {Component, PropTypes} from 'react';
import {map} from 'lodash-compat/collection';
import RemoteFormField from 'common/ui/RemoteFormField';
import Card from './Card';

class Form extends Component {
  render() {
    const {
      form,
      formContents,
      title,
      submitTitle,
      onSubmit,
      onEdit,
      tagActions,
      availableTags,
      selectedTags,
    } = this.props;

    const fields = map(form.ordered_fields, fieldName => (
      <RemoteFormField
        key={fieldName}
        form={form}
        fieldName={fieldName}
        value={formContents[fieldName] || ''}
        onChange={e => onEdit(fieldName, e.target.value)}
        tagActions={tagActions}
        availableTags={availableTags}
        selectedTags={selectedTags} />
    ));

    return (
      <Card title={title}>
        {fields}
        <button
          onClick={() => onSubmit()}>
          {submitTitle}
        </button>
      </Card>
    );
  }
}

Form.propTypes = {
  form: PropTypes.object.isRequired,
  formContents: PropTypes.object.isRequired,
  title: PropTypes.string.isRequired,
  submitTitle: PropTypes.string.isRequired,
  onSubmit: PropTypes.func.isRequired,
  onEdit: PropTypes.func.isRequired,
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

export default Form;
